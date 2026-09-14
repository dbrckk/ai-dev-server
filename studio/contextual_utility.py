"""Bounded cost-aware utility for contextual routing."""
from __future__ import annotations

MAX_UTILITY_BONUS = 12.0
MAX_UTILITY_PENALTY = 16.0
REFERENCE_LATENCY_SECONDS = 30.0
REFERENCE_VERIFICATION_SECONDS = 120.0
HIGH_RISK_MULTIPLIER = 1.35


def utility_score(
    *,
    expected_success: float,
    execution_seconds: float | None,
    verification_seconds: float | None,
    architecture_hold: bool,
    free_preferred: bool = True,
) -> dict:
    success = max(0.0, min(1.0, float(expected_success)))
    execution = max(0.0, float(execution_seconds or 0.0))
    verification = max(0.0, float(verification_seconds or 0.0))

    execution_cost = min(1.0, execution / REFERENCE_LATENCY_SECONDS)
    verification_cost = min(1.0, verification / REFERENCE_VERIFICATION_SECONDS)
    risk = HIGH_RISK_MULTIPLIER if architecture_hold else 1.0

    quality_value = success * 1.2
    time_cost = (0.45 * execution_cost + 0.35 * verification_cost) * risk
    paid_cost = 0.0 if free_preferred else 0.10

    normalized = quality_value - time_cost - paid_cost
    normalized = max(-1.0, min(1.0, normalized))

    if normalized >= 0:
        score = normalized * MAX_UTILITY_BONUS
    else:
        score = normalized * MAX_UTILITY_PENALTY

    return {
        "score": round(score, 4),
        "expected_success": round(success, 4),
        "execution_cost": round(execution_cost, 4),
        "verification_cost": round(verification_cost, 4),
        "architecture_risk_multiplier": round(risk, 4),
        "paid_cost": round(paid_cost, 4),
    }
