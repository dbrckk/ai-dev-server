"""Adaptive execution budgeting for bounded autonomous project loops."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionBudget:
    max_work_passes: int
    agent_limit: int
    reserve_seconds: int
    mode: str

    def as_dict(self) -> dict:
        return {
            "max_work_passes": self.max_work_passes,
            "agent_limit": self.agent_limit,
            "reserve_seconds": self.reserve_seconds,
            "mode": self.mode,
        }


def choose_budget(
    *,
    remaining_seconds: float | None,
    previous_verification: dict | None,
    bootstrap_passed: bool,
    meta_agent_limit: int,
    predicted_work_passes: int | None = None,
    predicted_agent_limit: int | None = None,
    predicted_reserve_seconds: int | None = None,
) -> ExecutionBudget:
    """Choose conservative work depth from time and recent verification evidence."""
    remaining = None if remaining_seconds is None else max(0.0, float(remaining_seconds))
    previous_passed = bool(isinstance(previous_verification, dict) and previous_verification.get("passed") is True)

    predicted_work_passes = 2 if predicted_work_passes is None else max(1, min(2, int(predicted_work_passes)))
    predicted_agent_limit = meta_agent_limit if predicted_agent_limit is None else max(0, min(meta_agent_limit, int(predicted_agent_limit)))
    predicted_reserve_seconds = 90 if predicted_reserve_seconds is None else max(60, min(900, int(predicted_reserve_seconds)))

    if remaining is not None and remaining < max(180, predicted_reserve_seconds + 90):
        return ExecutionBudget(
            max_work_passes=1,
            agent_limit=0 if previous_passed else min(1, predicted_agent_limit),
            reserve_seconds=min(predicted_reserve_seconds, max(60, int(remaining // 2))),
            mode="deadline_guard",
        )
    if previous_passed:
        return ExecutionBudget(
            max_work_passes=1,
            agent_limit=min(1, predicted_agent_limit),
            reserve_seconds=max(90, predicted_reserve_seconds),
            mode="verification_close",
        )
    if not bootstrap_passed:
        return ExecutionBudget(
            max_work_passes=1,
            agent_limit=min(1, meta_agent_limit),
            reserve_seconds=max(120, predicted_reserve_seconds),
            mode="bootstrap_recovery",
        )
    if remaining is not None and remaining < 600:
        return ExecutionBudget(
            max_work_passes=1,
            agent_limit=min(1, meta_agent_limit),
            reserve_seconds=max(120, predicted_reserve_seconds),
            mode="time_constrained",
        )
    return ExecutionBudget(
        max_work_passes=predicted_work_passes,
        agent_limit=min(predicted_agent_limit, meta_agent_limit),
        reserve_seconds=predicted_reserve_seconds,
        mode="normal",
    )
