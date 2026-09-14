"""Provider-routed structured model calls for generic projects."""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

from core import API, APIError, ProtocolError, StudioError
from provider_router import candidates_for, load_providers, budget_eligible
from provider_health import eligible as provider_eligible, load as load_provider_health, reliability_bonus, record_failure as record_provider_failure, record_success as record_provider_success
from provider_metrics import latency_bonus, load as load_provider_metrics, record as record_provider_latency
from adaptive_scoring import score_provider
from routing_history import learned_weights, load as load_routing_history, record as record_routing_event
from safe_rewrite_learning import (
    summarize as summarize_safe_rewrite_learning,
    origin_violation_penalty,
    rewrite_recovery_bonus,
    exploration_bonus,
)
from contextual_routing_memory import (
    load as load_contextual_routing_memory,
    contextual_adjustment,
    contextual_bandit_score,
)
from contextual_utility import utility_score
from provider_cost import (
    load as load_provider_cost,
    record as record_provider_cost,
    ema_cost as provider_ema_cost,
    estimate_call_cost,
)


def _decode(response: dict) -> dict:
    try:
        choice = response["choices"][0]
        if choice.get("finish_reason") == "length":
            raise ProtocolError("Generic model response truncated")
        raw = choice["message"]["content"].strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
        value = json.loads(raw)
    except (KeyError, IndexError, TypeError, AttributeError, json.JSONDecodeError):
        raise ProtocolError("Generic model returned invalid JSON") from None
    if not isinstance(value, dict):
        raise ProtocolError("Generic model JSON must be an object")
    return value


def ask(system: str, user: str, *, code: bool = False, avoid_models: set[str] | None = None, avoid_providers: set[str] | None = None, timeout_seconds: int | float = 300) -> tuple[dict, dict]:
    try:
        providers = load_providers(prefer_free=True)
    except ValueError as exc:
        raise StudioError(str(exc)) from None
    role = "implementation" if code else "product"
    providers = candidates_for(role, providers=providers)
    health_raw = os.environ.get("STUDIO_PROVIDER_HEALTH_PATH", "")
    metrics_raw = os.environ.get("STUDIO_PROVIDER_METRICS_PATH", "")
    health_path = Path(health_raw) if health_raw else None
    metrics_path = Path(metrics_raw) if metrics_raw else None
    history_raw = os.environ.get("STUDIO_ROUTING_HISTORY_PATH", "")
    history_path = Path(history_raw) if history_raw else None
    safe_rewrite_raw = os.environ.get("STUDIO_SAFE_REWRITE_LEARNING_PATH", "")
    safe_rewrite_path = Path(safe_rewrite_raw) if safe_rewrite_raw else None
    contextual_routing_raw = os.environ.get("STUDIO_CONTEXTUAL_ROUTING_MEMORY_PATH", "")
    contextual_routing_path = Path(contextual_routing_raw) if contextual_routing_raw else None
    provider_cost_raw = os.environ.get("STUDIO_PROVIDER_COST_PATH", "")
    provider_cost_path = Path(provider_cost_raw) if provider_cost_raw else None
    try:
        weighted_contexts = json.loads(os.environ.get("STUDIO_ROUTING_CONTEXTS_JSON", "[]"))
    except json.JSONDecodeError:
        weighted_contexts = []
    if not isinstance(weighted_contexts, list):
        weighted_contexts = []
    health = load_provider_health(health_path) if health_path is not None else {}
    metrics = load_provider_metrics(metrics_path) if metrics_path is not None else {}
    history = load_routing_history(history_path) if history_path is not None else []
    try:
        verification_seconds = float(os.environ.get("STUDIO_EXPECTED_VERIFICATION_SECONDS", "0") or 0)
    except ValueError:
        verification_seconds = 0.0
    architecture_hold = any(
        isinstance(item, list) and len(item) == 2 and item[0] == "architecture-risk:hold"
        for item in weighted_contexts
    )
    safe_rewrite_summary = summarize_safe_rewrite_learning(safe_rewrite_path) if safe_rewrite_path is not None else {}
    contextual_routing = load_contextual_routing_memory(contextual_routing_path) if contextual_routing_path is not None else {}
    provider_costs = load_provider_cost(provider_cost_path) if provider_cost_path is not None else {}
    try:
        max_api_cost_usd = float(os.environ.get("STUDIO_MAX_API_COST_USD", "0") or 0.0)
    except ValueError:
        max_api_cost_usd = 0.0
    spent_api_cost_usd = sum(
        max(0.0, float(row.get("total_cost_usd", 0.0) or 0.0))
        for row in provider_costs.values()
        if isinstance(row, dict)
    )
    weights = learned_weights(history, kind="provider", role=role)
    if health_path is not None:
        providers = tuple(provider for provider in providers if provider_eligible(health_path, provider.name))
    providers = budget_eligible(
        providers,
        max_api_cost_usd=max_api_cost_usd,
        spent_api_cost_usd=spent_api_cost_usd,
    )
    if not providers:
        raise StudioError(
            "Paid API budget exhausted and no unmetered provider is configured"
        )
    provider_scores = {}
    for provider in providers:
        base = score_provider(
            name=provider.name,
            priority=provider.priority,
            free_preferred=provider.free_preferred,
            reliability=reliability_bonus(health, provider.name),
            latency=latency_bonus(metrics, provider.name, role),
            weights=weights,
        )
        components = dict(base.components)
        if role == "implementation" and safe_rewrite_path is not None:
            violation = origin_violation_penalty(
                safe_rewrite_summary,
                kind="provider",
                name=provider.name,
                role=role,
            )
            recovery = rewrite_recovery_bonus(
                safe_rewrite_summary,
                kind="provider",
                name=provider.name,
                role=role,
            )
            components["architecture_violation"] = -violation
            components["safe_rewrite_recovery"] = recovery
            components["architecture_exploration"] = exploration_bonus(
                safe_rewrite_summary,
                kind="provider",
                name=provider.name,
                role=role,
            )
        if role == "implementation" and contextual_routing_path is not None:
            parsed_contexts = [
                (str(item[0]), float(item[1]))
                for item in weighted_contexts
                if isinstance(item, list) and len(item) == 2
            ]
            components["contextual_performance"] = contextual_adjustment(
                contextual_routing,
                weighted_contexts=parsed_contexts,
                kind="provider",
                name=provider.name,
            )
            bandit = contextual_bandit_score(
                contextual_routing,
                weighted_contexts=parsed_contexts,
                kind="provider",
                name=provider.name,
            )
            components["contextual_expected_success"] = bandit["expected_success"] * 10.0
            components["contextual_uncertainty"] = -bandit["uncertainty"] * 2.0
            components["contextual_bandit_exploration"] = bandit["exploration_bonus"]
            metric_row = metrics.get(provider.name + ":" + role, {}) if isinstance(metrics, dict) else {}
            execution_seconds = (
                float(metric_row.get("ema_latency_seconds", 0.0))
                if isinstance(metric_row, dict)
                else 0.0
            )
            retry_probability = max(0.0, min(1.0, 1.0 - bandit["expected_success"]))
            monetary_cost_usd = provider_ema_cost(provider_costs, provider.name, role)
            utility = utility_score(
                expected_success=bandit["expected_success"],
                execution_seconds=execution_seconds,
                verification_seconds=verification_seconds,
                architecture_hold=architecture_hold,
                free_preferred=provider.free_preferred,
                monetary_cost_usd=monetary_cost_usd,
                retry_probability=retry_probability,
                unmetered=provider.unmetered,
            )
            components["cost_aware_utility"] = utility["score"]
            components["verified_value_per_unit_cost"] = utility["verified_value_per_unit_cost"]
            components["unmetered_capacity"] = utility["unmetered_bonus"]
            if max_api_cost_usd > 0 and not provider.unmetered:
                remaining_ratio = max(
                    0.0,
                    min(1.0, (max_api_cost_usd - spent_api_cost_usd) / max_api_cost_usd),
                )
                components["remaining_paid_budget"] = (remaining_ratio - 0.5) * 6.0
        from adaptive_scoring import ScoreTrace
        provider_scores[provider.name] = ScoreTrace(
            name=provider.name,
            total=sum(float(v) for v in components.values()),
            components=components,
        )
    providers = tuple(sorted(
        providers,
        key=lambda provider: (-provider_scores[provider.name].total, provider.name),
    ))
    if not providers:
        raise StudioError("No healthy configured provider available for generic project")
    avoid_models = avoid_models or set()
    avoid_providers = avoid_providers or set()
    preferred = [
        provider for provider in providers
        if provider.name not in avoid_providers and provider.model_for(role) not in avoid_models
    ]
    fallback = [provider for provider in providers if provider not in preferred]
    ordered = [*preferred, *fallback]
    last = None
    total_timeout = max(1.0, min(300.0, float(timeout_seconds)))
    deadline = time.monotonic() + total_timeout
    for provider in ordered:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        model = provider.model_for(role)
        api = API(provider.base, provider.key)
        params = {
            "model": model,
            "stream": False,
            "max_tokens": 16000 if code else 8192,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        if api.base == "https://integrate.api.nvidia.com/v1" and model.startswith("nvidia/nemotron-3-"):
            params.update(chat_template_kwargs={"enable_thinking": True}, reasoning_budget=2048)
        started = time.monotonic()
        try:
            response = api.call("POST", "/chat/completions", params, timeout_seconds=remaining)
            elapsed = time.monotonic() - started
            if metrics_path is not None:
                record_provider_latency(metrics_path, provider.name, role, elapsed)
            usage = response.get("usage") if isinstance(response, dict) else None
            call_cost = 0.0
            if provider_cost_path is not None and isinstance(usage, dict):
                try:
                    call_cost = 0.0 if provider.unmetered else estimate_call_cost(
                        prompt_tokens=int(usage.get("prompt_tokens", 0) or 0),
                        completion_tokens=int(usage.get("completion_tokens", 0) or 0),
                        input_cost_per_million=provider.input_cost_per_million,
                        output_cost_per_million=provider.output_cost_per_million,
                    )
                except (TypeError, ValueError):
                    call_cost = 0.0
                record_provider_cost(provider_cost_path, provider.name, role, call_cost)
            decoded = _decode(response)
            if health_path is not None:
                record_provider_success(health_path, provider.name)
            if history_path is not None:
                record_routing_event(
                    history_path,
                    kind="provider",
                    name=provider.name,
                    role=role,
                    score=provider_scores[provider.name].as_dict(),
                    success=True,
                    duration_seconds=elapsed,
                )
            return decoded, {
                "provider": provider.name,
                "model": model,
                "independent_preference_met": provider.name not in avoid_providers and model not in avoid_models,
                "routing_score": provider_scores[provider.name].as_dict(),
                "duration_seconds": elapsed,
                "estimated_cost_usd": round(call_cost, 8),
                "unmetered": provider.unmetered,
                "paid_budget": {
                    "limit_usd": max_api_cost_usd if max_api_cost_usd > 0 else None,
                    "spent_before_call_usd": round(spent_api_cost_usd, 8),
                },
            }
        except (APIError, StudioError, ProtocolError) as exc:
            elapsed = time.monotonic() - started
            if metrics_path is not None:
                record_provider_latency(metrics_path, provider.name, role, elapsed)
            if health_path is not None:
                record_provider_failure(health_path, provider.name)
            if history_path is not None:
                record_routing_event(
                    history_path,
                    kind="provider",
                    name=provider.name,
                    role=role,
                    score=provider_scores[provider.name].as_dict(),
                    success=False,
                    duration_seconds=elapsed,
                )
            last = exc
            continue
    if time.monotonic() >= deadline:
        raise StudioError("Generic model call quota timed out") from None
    raise StudioError("All generic-project providers failed: " + (str(last) if last else "unknown")) from None
