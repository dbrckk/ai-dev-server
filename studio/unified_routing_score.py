"""Unified bounded provider routing score. Hard eligibility remains external/fail-closed."""
from __future__ import annotations

from provider_health import reliability_bonus
from provider_metrics import latency_bonus
from provider_runtime_reliability import routing_bonus as runtime_bonus
from routing_calibration import adjustment as calibration_adjustment


def score(
    *,
    provider,
    role: str,
    model: str,
    health: dict | None = None,
    metrics: dict | None = None,
    runtime: dict | None = None,
    contextual_adjustment: float = 0.0,
    exploration_bonus: float = 0.0,
    calibration: dict | None = None,
) -> dict:
    base = max(0.0, min(100.0, float(getattr(provider, "priority", 50))))
    free_bonus = 8.0 if bool(getattr(provider, "free_preferred", False)) else 0.0
    unmetered_bonus = 10.0 if bool(getattr(provider, "unmetered", False)) else 0.0
    quota_bonus = 5.0 if int(getattr(provider, "monthly_token_quota", 0) or 0) > 0 else 0.0
    health_signal = max(-20.0, min(20.0, reliability_bonus(health or {}, provider.name)))
    latency_signal = max(-12.0, min(12.0, latency_bonus(metrics or {}, provider.name, role)))
    runtime_signal = max(-12.0, min(12.0, runtime_bonus(runtime or {}, provider.name, model)))
    context_signal = max(-18.0, min(12.0, float(contextual_adjustment or 0.0)))
    exploration_signal = max(0.0, min(8.0, float(exploration_bonus or 0.0)))
    calibration_signal = calibration_adjustment(calibration or {}, provider.name, model)
    total = (
        base + free_bonus + unmetered_bonus + quota_bonus
        + health_signal + latency_signal + runtime_signal
        + context_signal + exploration_signal + calibration_signal
    )
    return {
        "score": round(total, 6),
        "components": {
            "priority": base,
            "free": free_bonus,
            "unmetered": unmetered_bonus,
            "quota": quota_bonus,
            "health": health_signal,
            "latency": latency_signal,
            "runtime_reliability": runtime_signal,
            "context": context_signal,
            "exploration": exploration_signal,
            "verified_outcome_calibration": calibration_signal,
        },
    }
