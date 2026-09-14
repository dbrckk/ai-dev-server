"""Provider registry and ordered fallback policy for AI Dev Server."""
from __future__ import annotations

from dataclasses import dataclass
import json
import os
from typing import Iterable


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

    def model_for(self, role: str, screenshots: bool = False) -> str:
        if screenshots:
            return self.vision_model
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


def _primary() -> ProviderSpec | None:
    key = os.environ.get("STUDIO_API_KEY", "")
    if not key:
        return None
    base = os.environ.get("STUDIO_API_BASE", "https://integrate.api.nvidia.com/v1")
    model = os.environ.get("STUDIO_MODEL", "nvidia/nemotron-3-super-120b-a12b")
    code_model = os.environ.get("STUDIO_CODE_MODEL", "") or model
    vision = os.environ.get("STUDIO_VISION_MODEL", "")
    if not vision and base.rstrip("/") == "https://integrate.api.nvidia.com/v1":
        vision = "nvidia/nemotron-nano-12b-v2-vl"
    if vision == "disabled":
        vision = ""
    explicit_unmetered = os.environ.get("STUDIO_PROVIDER_UNMETERED")
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
            else _is_local_base(base)
        ),
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
            "priority", "free_preferred", "input_cost_per_million", "output_cost_per_million", "unmetered",
        }
        if set(item) - allowed:
            raise ValueError("Unknown provider configuration field")
        name = item.get("name") or f"fallback-{index + 1}"
        base = item.get("base")
        key_env = item.get("key_env")
        model = item.get("model")
        if not all(isinstance(v, str) and v.strip() for v in (name, base, key_env, model)):
            raise ValueError("Provider name/base/key_env/model are required strings")
        key = os.environ.get(key_env, "")
        if not key:
            continue
        priority = item.get("priority", 50)
        if type(priority) is not int:
            raise ValueError("Provider priority must be an integer")
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
                else _is_local_base(base)
            ),
        ))
    return specs


def load_providers(*, prefer_free: bool = True) -> tuple[ProviderSpec, ...]:
    specs = []
    primary = _primary()
    if primary:
        specs.append(primary)
    specs.extend(_json_specs(os.environ.get("STUDIO_PROVIDERS_JSON", "")))

    deduped = {}
    for spec in specs:
        key = (spec.base.rstrip("/"), spec.model, spec.code_model, spec.vision_model)
        current = deduped.get(key)
        if current is None or spec.priority > current.priority:
            deduped[key] = spec

    def sort_key(spec: ProviderSpec):
        free_bonus = 1 if (prefer_free and spec.free_preferred) else 0
        return (-free_bonus, -spec.priority, spec.name)

    return tuple(sorted(deduped.values(), key=sort_key))


def candidates_for(
    role: str,
    *,
    screenshots: bool = False,
    prefer_free: bool = True,
    providers: Iterable[ProviderSpec] | None = None,
) -> tuple[ProviderSpec, ...]:
    specs = tuple(providers) if providers is not None else load_providers(prefer_free=prefer_free)
    return tuple(spec for spec in specs if spec.model_for(role, screenshots))
