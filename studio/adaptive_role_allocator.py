"""Bounded adaptive allocation of model roles for one autonomous round."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RoleAllocation:
    implementation_models: int
    require_review: bool
    require_planning: bool
    difficulty: float
    uncertainty: float
    budget_pressure: float
    reason: str

    def as_dict(self) -> dict:
        return {
            "implementation_models": self.implementation_models,
            "require_review": self.require_review,
            "require_planning": self.require_planning,
            "difficulty": round(self.difficulty, 4),
            "uncertainty": round(self.uncertainty, 4),
            "budget_pressure": round(self.budget_pressure, 4),
            "reason": self.reason,
        }


def budget_pressure(
    *,
    remaining_seconds: float | None,
    verification_seconds: float | None,
) -> float:
    verification = max(0.0, float(verification_seconds or 0.0))
    remaining = None if remaining_seconds is None else max(0.0, float(remaining_seconds))
    if remaining is None:
        return 0.0
    reserve = max(120.0, verification * 2.0)
    return max(0.0, min(1.0, 1.0 - remaining / reserve))


def planning_required(
    *,
    difficulty: float,
    remaining_seconds: float | None,
    verification_seconds: float | None,
) -> bool:
    """Return whether this round is worth spending a model call on planning."""
    normalized_difficulty = max(0.0, min(1.0, float(difficulty or 0.0)))
    pressure = budget_pressure(
        remaining_seconds=remaining_seconds,
        verification_seconds=verification_seconds,
    )
    return normalized_difficulty >= 0.45 and pressure < 0.85


def choose_role_allocation(
    *,
    difficulty: float,
    route_confidence: float,
    remaining_seconds: float | None,
    verification_seconds: float | None,
    free_capacity: float,
    max_implementation_models: int = 3,
) -> RoleAllocation:
    difficulty = max(0.0, min(1.0, float(difficulty or 0.0)))
    confidence = max(0.0, min(1.0, float(route_confidence or 0.0)))
    uncertainty = 1.0 - confidence
    capacity = max(0.0, min(1.0, float(free_capacity or 0.0)))
    pressure = budget_pressure(
        remaining_seconds=remaining_seconds,
        verification_seconds=verification_seconds,
    )

    implementation_models = 1
    reason = "single implementation model"
    if difficulty >= 0.55 and uncertainty >= 0.30 and capacity >= 0.45 and pressure < 0.70:
        implementation_models = 2
        reason = "difficult uncertain task benefits from independent implementation"
    if difficulty >= 0.80 and uncertainty >= 0.55 and capacity >= 0.80 and pressure < 0.35:
        implementation_models = 3
        reason = "high difficulty and uncertainty justify a wide implementation portfolio"

    implementation_models = max(
        1, min(3, max(1, int(max_implementation_models)), implementation_models)
    )
    require_planning = planning_required(
        difficulty=difficulty,
        remaining_seconds=remaining_seconds,
        verification_seconds=verification_seconds,
    )
    require_review = (
        difficulty >= 0.35
        or uncertainty >= 0.40
        or implementation_models > 1
    ) and pressure < 0.90

    return RoleAllocation(
        implementation_models=implementation_models,
        require_review=require_review,
        require_planning=require_planning,
        difficulty=difficulty,
        uncertainty=uncertainty,
        budget_pressure=pressure,
        reason=reason,
    )
