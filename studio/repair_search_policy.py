"""Adaptive depth policy for bounded repair search."""
from __future__ import annotations

MIN_EXPANSION_VALUE = 8.0
MIN_REFINEMENT_VALUE = 10.0


def branch_cost(row: dict) -> int:
    return max(0, int(row.get("estimated_model_calls", 0)))


def expected_value(row: dict) -> float:
    success = max(0.0, min(1.0, float(row.get("conservative_success_rate", 0.5))))
    risk = max(0.0, min(1.0, float(row.get("risk", 0.4))))
    seconds = max(0.0, float(row.get("estimated_seconds", 30.0)))
    calls = branch_cost(row)
    return (
        success * 100.0
        - risk * 25.0
        - min(20.0, seconds / 15.0)
        - calls * 5.0
    )


def should_expand(
    *,
    current_winner: dict | None,
    candidate_row: dict,
    remaining_model_calls: int,
) -> bool:
    calls = branch_cost(candidate_row)
    if calls > remaining_model_calls:
        return False
    value = expected_value(candidate_row)
    if current_winner is None:
        return value >= MIN_EXPANSION_VALUE
    current = float(current_winner.get("candidate_score", -1_000_000.0))
    # Once a verified winner exists, only spend more if learned evidence is
    # materially strong; candidate_score has a 1000-point verified baseline.
    return value >= MIN_EXPANSION_VALUE and current < 1010.0


def should_refine(
    *,
    failure_present: bool,
    refinement_model_calls: int,
    remaining_model_calls: int,
    strategy_row: dict,
) -> bool:
    if not failure_present:
        return False
    if refinement_model_calls > remaining_model_calls:
        return False
    return expected_value(strategy_row) >= MIN_REFINEMENT_VALUE


def should_continue_after_quick_failure(
    *,
    next_step_model_calls: int,
    remaining_model_calls: int,
    strategy_row: dict,
) -> bool:
    if next_step_model_calls > remaining_model_calls:
        return False
    # Continuing a broken intermediate state is only justified for strategies
    # with meaningful expected value. This lets a later agent/model repair an
    # intermediate compile/test regression without blindly exploring.
    return expected_value(strategy_row) >= MIN_EXPANSION_VALUE
