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
) -> ExecutionBudget:
    """Choose conservative work depth from time and recent verification evidence."""
    remaining = None if remaining_seconds is None else max(0.0, float(remaining_seconds))
    previous_passed = bool(isinstance(previous_verification, dict) and previous_verification.get("passed") is True)

    if remaining is not None and remaining < 180:
        return ExecutionBudget(
            max_work_passes=1,
            agent_limit=0 if previous_passed else min(1, meta_agent_limit),
            reserve_seconds=60,
            mode="deadline_guard",
        )
    if previous_passed:
        return ExecutionBudget(
            max_work_passes=1,
            agent_limit=min(1, meta_agent_limit),
            reserve_seconds=90,
            mode="verification_close",
        )
    if not bootstrap_passed:
        return ExecutionBudget(
            max_work_passes=1,
            agent_limit=min(1, meta_agent_limit),
            reserve_seconds=120,
            mode="bootstrap_recovery",
        )
    if remaining is not None and remaining < 600:
        return ExecutionBudget(
            max_work_passes=1,
            agent_limit=min(1, meta_agent_limit),
            reserve_seconds=120,
            mode="time_constrained",
        )
    return ExecutionBudget(
        max_work_passes=2,
        agent_limit=min(2, meta_agent_limit),
        reserve_seconds=90,
        mode="normal",
    )
