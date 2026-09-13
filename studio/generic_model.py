"""Provider-routed structured model calls for generic projects."""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

from core import API, APIError, ProtocolError, StudioError
from provider_router import candidates_for, load_providers
from provider_health import eligible as provider_eligible, load as load_provider_health, reliability_bonus, record_failure as record_provider_failure, record_success as record_provider_success
from provider_metrics import latency_bonus, load as load_provider_metrics, record as record_provider_latency
from adaptive_scoring import score_provider
from routing_history import learned_weights, load as load_routing_history, record as record_routing_event


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


def ask(system: str, user: str, *, code: bool = False, avoid_models: set[str] | None = None, avoid_providers: set[str] | None = None) -> tuple[dict, dict]:
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
    health = load_provider_health(health_path) if health_path is not None else {}
    metrics = load_provider_metrics(metrics_path) if metrics_path is not None else {}
    history = load_routing_history(history_path) if history_path is not None else []
    weights = learned_weights(history, kind="provider", role=role)
    if health_path is not None:
        providers = tuple(provider for provider in providers if provider_eligible(health_path, provider.name))
    provider_scores = {
        provider.name: score_provider(
            name=provider.name,
            priority=provider.priority,
            free_preferred=provider.free_preferred,
            reliability=reliability_bonus(health, provider.name),
            latency=latency_bonus(metrics, provider.name, role),
            weights=weights,
        )
        for provider in providers
    }
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
    for provider in ordered:
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
            response = api.call("POST", "/chat/completions", params)
            elapsed = time.monotonic() - started
            if metrics_path is not None:
                record_provider_latency(metrics_path, provider.name, role, elapsed)
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
    raise StudioError("All generic-project providers failed: " + (str(last) if last else "unknown")) from None
