"""Provider registry and ordered fallback policy for AI Dev Server."""
# repo-brain-v4-impact-pilot
from __future__ import annotations

from dataclasses import dataclass, field
import json
import os
import urllib.request
import urllib.error
from pathlib import Path
from typing import Iterable

from provider_runtime_reliability import summarize as summarize_runtime_reliability
from provider_health import load as load_provider_health, eligible as provider_eligible
from provider_metrics import load as load_provider_metrics
from unified_routing_score import score as unified_provider_score
from routing_audit import append as append_routing_audit

from local_capacity import discover as discover_local_capacity


@dataclass(frozen=True)
class ProviderSpec:
    name: str
    base: str
    key: str
    model: str
    code_model: str = ""
    vision_model: str = ""
    priority: int = 50
    free_preferred: bool = True
    input_cost_per_million: float = 0.0
    output_cost_per_million: float = 0.0
    unmetered: bool = False
    monthly_token_quota: int = 0
    role_models: dict[str, str] = field(default_factory=dict)

    def model_for(self, role: str, screenshots: bool = False) -> str:
        if screenshots:
            return self.role_models.get("visual") or self.vision_model
        explicit = self.role_models.get(role)
        if explicit:
            return explicit
        if role in {"implementation", "tests", "security_fix", "release_fix"}:
            return self.code_model or self.model
        return self.model


def _is_local_base(base: str) -> bool:
    text = (base or "").strip().lower()
    return (
        text.startswith("http://127.0.0.1")
        or text.startswith("https://127.0.0.1")
        or text.startswith("http://localhost")
        or text.startswith("https://localhost")
        or text.startswith("http://0.0.0.0")
        or text.startswith("https://0.0.0.0")
    )


def _bool(value, default=True):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() not in {"0", "false", "no", "off"}
    return default


def _auto_omniroute() -> ProviderSpec | None:
    if not _bool(os.environ.get("STUDIO_AUTO_DISCOVER_OMNIROUTE", "true"), True):
        return None
    base = os.environ.get("STUDIO_OMNIROUTE_BASE", "http://127.0.0.1:20128/v1").rstrip("/")
    if not _is_local_base(base):
        return None
    try:
        req = urllib.request.Request(
            base + "/models",
            headers={"Accept": "application/json", "User-Agent": "ai-dev-server"},
        )
        with urllib.request.urlopen(req, timeout=0.35) as response:
            if response.status != 200:
                return None
            raw = response.read(200000)
            value = json.loads(raw)
    except (OSError, ValueError, urllib.error.URLError):
        return None
    if not isinstance(value, dict) or not isinstance(value.get("data"), list):
        return None
    return ProviderSpec(
        name="omniroute",
        base=base,
        key="",
        model="auto",
        code_model="auto",
        priority=98,
        free_preferred=True,
        unmetered=False,
        monthly_token_quota=1_470_000_000,
    )


def _primary() -> ProviderSpec | None:
    base = os.environ.get("STUDIO_API_BASE", "https://integrate.api.nvidia.com/v1")
    key = os.environ.get("STUDIO_API_KEY", "")
    if not key and not _is_local_base(base):
        return None
    model = os.environ.get("STUDIO_MODEL", "nvidia/nemotron-3-super-120b-a12b")
    code_model = os.environ.get("STUDIO_CODE_MODEL", "") or model
    vision = os.environ.get("STUDIO_VISION_MODEL", "")
    if not vision and base.rstrip("/") == "https://integrate.api.nvidia.com/v1":
        vision = "nvidia/nemotron-nano-12b-v2-vl"
    if vision == "disabled":
        vision = ""
    explicit_unmetered = os.environ.get("STUDIO_PROVIDER_UNMETERED")
    role_models_raw = os.environ.get("STUDIO_ROLE_MODELS_JSON", "")
    role_models = {}
    if role_models_raw.strip():
        try:
            parsed_role_models = json.loads(role_models_raw)
        except json.JSONDecodeError as exc:
            raise ValueError("STUDIO_ROLE_MODELS_JSON must be valid JSON") from exc
        if not isinstance(parsed_role_models, dict):
            raise ValueError("STUDIO_ROLE_MODELS_JSON must be a JSON object")
        for role_name, role_model in parsed_role_models.items():
            if (
                not isinstance(role_name, str)
                or not role_name.strip()
                or not isinstance(role_model, str)
                or not role_model.strip()
            ):
                raise ValueError("STUDIO_ROLE_MODELS_JSON must map roles to non-empty model names")
            role_models[role_name.strip()] = role_model.strip()
    quota_raw = os.environ.get("STUDIO_MONTHLY_TOKEN_QUOTA", "")
    if quota_raw:
        try:
            monthly_token_quota = max(0, int(quota_raw))
        except ValueError:
            raise ValueError("STUDIO_MONTHLY_TOKEN_QUOTA must be an integer") from None
    elif "omniroute" in os.environ.get("STUDIO_PROVIDER_NAME", "primary").lower() or ":20128" in base:
        monthly_token_quota = 1_470_000_000
    else:
        monthly_token_quota = 0
    return ProviderSpec(
        name=os.environ.get("STUDIO_PROVIDER_NAME", "primary"),
        base=base,
        key=key,
        model=model,
        code_model=code_model,
        vision_model=vision,
        priority=100,
        free_preferred=_bool(os.environ.get("STUDIO_PROVIDER_FREE", "true")),
        input_cost_per_million=max(0.0, float(os.environ.get("STUDIO_INPUT_COST_PER_MILLION", "0") or 0)),
        output_cost_per_million=max(0.0, float(os.environ.get("STUDIO_OUTPUT_COST_PER_MILLION", "0") or 0)),
        unmetered=(
            _bool(explicit_unmetered, False)
            if explicit_unmetered is not None
            else (_is_local_base(base) and monthly_token_quota == 0)
        ),
        monthly_token_quota=monthly_token_quota,
        role_models=role_models,
    )


def _json_specs(raw: str) -> list[ProviderSpec]:
    if not raw.strip():
        return []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("STUDIO_PROVIDERS_JSON must be valid JSON") from exc
    if not isinstance(data, list):
        raise ValueError("STUDIO_PROVIDERS_JSON must be a JSON array")
    specs = []
    for index, item in enumerate(data):
        if not isinstance(item, dict):
            raise ValueError("Provider entries must be objects")
        allowed = {
            "name", "base", "key_env", "model", "code_model", "vision_model",
            "priority", "free_preferred", "input_cost_per_million", "output_cost_per_million", "unmetered", "monthly_token_quota", "role_models",
        }
        if set(item) - allowed:
            raise ValueError("Unknown provider configuration field")
        name = item.get("name") or f"fallback-{index + 1}"
        base = item.get("base")
        key_env = item.get("key_env")
        model = item.get("model")
        if not all(isinstance(v, str) and v.strip() for v in (name, base, model)):
            raise ValueError("Provider name/base/model are required strings")
        local_base = _is_local_base(base)
        if key_env is not None and (not isinstance(key_env, str) or not key_env.strip()):
            raise ValueError("Provider key_env must be a non-empty string when provided")
        if key_env:
            key = os.environ.get(key_env, "")
            if not key and not local_base:
                continue
        else:
            if not local_base:
                raise ValueError("Remote providers require key_env")
            key = ""
        priority = item.get("priority", 50)
        if type(priority) is not int:
            raise ValueError("Provider priority must be an integer")
        role_models = item.get("role_models", {})
        if not isinstance(role_models, dict):
            raise ValueError("Provider role_models must be an object")
        clean_role_models = {}
        for role_name, role_model in role_models.items():
            if (
                not isinstance(role_name, str)
                or not role_name.strip()
                or not isinstance(role_model, str)
                or not role_model.strip()
            ):
                raise ValueError("Provider role_models must map roles to non-empty model names")
            clean_role_models[role_name.strip()] = role_model.strip()
        specs.append(ProviderSpec(
            name=name.strip(),
            base=base.strip(),
            key=key,
            model=model.strip(),
            code_model=(item.get("code_model") or "").strip(),
            vision_model=(item.get("vision_model") or "").strip(),
            priority=priority,
            free_preferred=_bool(item.get("free_preferred", True)),
            input_cost_per_million=max(0.0, float(item.get("input_cost_per_million", 0.0) or 0.0)),
            output_cost_per_million=max(0.0, float(item.get("output_cost_per_million", 0.0) or 0.0)),
            unmetered=(
                _bool(item.get("unmetered"), False)
                if "unmetered" in item
                else (
                    _is_local_base(base)
                    and int(item.get("monthly_token_quota", 0) or 0) == 0
                )
            ),
            monthly_token_quota=max(0, int(item.get("monthly_token_quota", 0) or 0)),
            role_models=clean_role_models,
        ))
    return specs


def _local_capacity_specs() -> list[ProviderSpec]:
    specs = []
    for row in discover_local_capacity():
        try:
            name = str(row["name"])
            base = str(row["base"])
            quota = max(0, int(row.get("monthly_token_quota", 0) or 0))
            if quota > 0:
                specs.append(ProviderSpec(
                    name=name,
                    base=base,
                    key="",
                    model=str(row.get("model") or "auto"),
                    code_model=str(row.get("code_model") or row.get("model") or "auto"),
                    vision_model=str(row.get("vision_model") or ""),
                    priority=99,
                    free_preferred=True,
                    unmetered=False,
                    monthly_token_quota=quota,
                ))
                continue

            models = [
                str(model)
                for model in (row.get("models") or [])
                if isinstance(model, str) and model.strip()
            ][:12]
            if not models:
                models = [str(row["model"])]
            vision_model = str(row.get("vision_model") or "")
            for index, model in enumerate(models):
                is_code = any(hint in model.lower() for hint in ("coder","code","qwen","deepseek","starcoder","codestral","devstral"))
                is_vision = bool(vision_model and model == vision_model)
                specs.append(ProviderSpec(
                    name=f"{name}:{model}",
                    base=base,
                    key="",
                    model=model,
                    code_model=model if is_code else "",
                    vision_model=model if is_vision else "",
                    priority=max(70, 96 - index),
                    free_preferred=True,
                    unmetered=True,
                    monthly_token_quota=0,
                ))
        except (KeyError, TypeError, ValueError):
            continue
    return specs


def load_providers(*, prefer_free: bool = True) -> tuple[ProviderSpec, ...]:
    specs = []
    primary = _primary()
    explicit_json = os.environ.get("STUDIO_PROVIDERS_JSON", "")
    if primary:
        specs.append(primary)
    if primary is None and not explicit_json.strip():
        local_specs = _local_capacity_specs()
        if local_specs:
            specs.extend(local_specs)
        else:
            auto_omniroute = _auto_omniroute()
            if auto_omniroute:
                specs.append(auto_omniroute)
    specs.extend(_json_specs(explicit_json))

    deduped = {}
    for spec in specs:
        key = (
            spec.base.rstrip("/"),
            spec.model,
            spec.code_model,
            spec.vision_model,
            tuple(sorted(spec.role_models.items())),
        )
        current = deduped.get(key)
        if current is None or spec.priority > current.priority:
            deduped[key] = spec

    def sort_key(spec: ProviderSpec):
        unmetered_bonus = 2 if spec.unmetered else (1 if spec.monthly_token_quota > 0 else 0)
        free_bonus = 1 if (prefer_free and spec.free_preferred) else 0
        return (-unmetered_bonus, -free_bonus, -spec.priority, spec.name)

    return tuple(sorted(deduped.values(), key=sort_key))


def candidates_for(
    role: str,
    *,
    screenshots: bool = False,
    prefer_free: bool = True,
    providers: Iterable[ProviderSpec] | None = None,
) -> tuple[ProviderSpec, ...]:
    specs = tuple(providers) if providers is not None else load_providers(prefer_free=prefer_free)
    eligible = tuple(spec for spec in specs if spec.model_for(role, screenshots))
    rejected = [
        {"provider": spec.name, "reason": "required_model_unavailable"}
        for spec in specs if not spec.model_for(role, screenshots)
    ]
    reliability_path = os.environ.get("STUDIO_WORKER_LIVENESS_PATH", "").strip()
    if not reliability_path:
        return eligible
    try:
        with open(reliability_path, "r", encoding="utf-8") as handle:
            liveness = json.load(handle)
    except (OSError, UnicodeError, json.JSONDecodeError):
        return eligible
    reliability = summarize_runtime_reliability(liveness)
    health_path = Path(os.environ.get("STUDIO_PROVIDER_HEALTH_PATH", "provider-health.json"))
    metrics_path = Path(os.environ.get("STUDIO_PROVIDER_METRICS_PATH", "provider-metrics.json"))
    health = load_provider_health(health_path)
    metrics = load_provider_metrics(metrics_path)
    calibration_path = os.environ.get("STUDIO_ROUTING_CALIBRATION_PATH", "").strip()
    if calibration_path:
        try:
            calibration = json.loads(Path(calibration_path).read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            calibration = {}
    else:
        calibration = {}
    current = tuple(
        spec for spec in eligible
        if provider_eligible(health_path, spec.name)
    )
    rejected.extend(
        {"provider": spec.name, "reason": "circuit_breaker_open"}
        for spec in eligible if spec not in current
    )
    scored = []
    for spec in current:
        model = spec.model_for(role, screenshots)
        result = unified_provider_score(
            provider=spec, role=role, model=model,
            health=health, metrics=metrics, runtime=reliability,
            calibration=calibration,
        )
        scored.append((spec, result))
    scored.sort(key=lambda item: (-float(item[1]["score"]), item[0].name))
    ordered = tuple(item[0] for item in scored)
    audit_path = os.environ.get("STUDIO_ROUTING_AUDIT_PATH", "").strip()
    if audit_path:
        append_routing_audit(Path(audit_path), {
            "role": role,
            "screenshots": screenshots,
            "winner": ordered[0].name if ordered else None,
            "winner_model": ordered[0].model_for(role, screenshots) if ordered else None,
            "candidates": [
                {
                    "provider": spec.name,
                    "model": spec.model_for(role, screenshots),
                    "score": result["score"],
                    "components": result["components"],
                }
                for spec, result in scored
            ],
            "rejected": rejected,
        })
    return ordered


def budget_eligible(
    providers: Iterable[ProviderSpec],
    *,
    max_api_cost_usd: float,
    spent_api_cost_usd: float,
) -> tuple[ProviderSpec, ...]:
    specs = tuple(providers)
    limit = max(0.0, float(max_api_cost_usd))
    spent = max(0.0, float(spent_api_cost_usd))
    if limit <= 0 or spent < limit:
        return specs
    return tuple(
        spec
        for spec in specs
        if spec.unmetered or spec.monthly_token_quota > 0
    )
