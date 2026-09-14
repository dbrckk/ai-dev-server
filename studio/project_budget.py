"""Persistent project-wide model budget and repair-efficiency accounting."""
from __future__ import annotations

DEFAULT_REPAIR_RESERVE = 12
MIN_GAIN_PER_CALL = 0.15
STAGNANT_BRANCH_CALL_LIMIT = 4


def configure(state: dict, req: dict) -> dict:
    max_calls = int(req.get("max_calls", 12))
    max_cycles = int(req.get("max_cycles", 5))
    total_limit = int(req.get("max_project_model_calls", max_calls * max_cycles + DEFAULT_REPAIR_RESERVE))
    repair_limit = int(req.get("max_project_repair_calls", min(DEFAULT_REPAIR_RESERVE, total_limit)))
    current = state.get("project_budget")
    if not isinstance(current, dict):
        current = {}
    current.setdefault("model_calls_spent", 0)
    current.setdefault("repair_calls_spent", 0)
    current.setdefault("successful_repairs", 0)
    current.setdefault("failed_repairs", 0)
    current.setdefault("diagnostic_gain", 0.0)
    current["model_call_limit"] = total_limit
    current["repair_call_limit"] = repair_limit
    state["project_budget"] = current
    return current


def remaining(state: dict, *, repair: bool = False) -> int:
    budget = state.get("project_budget", {})
    if repair:
        return max(
            0,
            int(budget.get("repair_call_limit", 0))
            - int(budget.get("repair_calls_spent", 0)),
        )
    return max(
        0,
        int(budget.get("model_call_limit", 0))
        - int(budget.get("model_calls_spent", 0)),
    )


def can_spend(state: dict, calls: int = 1, *, repair: bool = False) -> bool:
    calls = max(0, int(calls))
    if remaining(state) < calls:
        return False
    if repair and remaining(state, repair=True) < calls:
        return False
    return True


def record_calls(state: dict, calls: int, *, repair: bool = False) -> dict:
    calls = max(0, int(calls))
    budget = state.setdefault("project_budget", {})
    budget["model_calls_spent"] = int(budget.get("model_calls_spent", 0)) + calls
    if repair:
        budget["repair_calls_spent"] = int(budget.get("repair_calls_spent", 0)) + calls
    return budget


def record_repair_outcome(
    state: dict,
    *,
    success: bool,
    calls: int,
    blockers_before: int,
    blockers_after: int,
) -> dict:
    budget = record_calls(state, calls, repair=True)
    if success:
        budget["successful_repairs"] = int(budget.get("successful_repairs", 0)) + 1
    else:
        budget["failed_repairs"] = int(budget.get("failed_repairs", 0)) + 1
    gain = max(0, int(blockers_before) - int(blockers_after))
    budget["diagnostic_gain"] = float(budget.get("diagnostic_gain", 0.0)) + float(gain)
    return budget


def branch_efficiency(task: dict) -> float:
    calls = max(0, int(task.get("model_calls_spent", 0)))
    if calls == 0:
        return 1.0
    improvements = max(0, int(task.get("improvement_count", 0)))
    return improvements / calls


def branch_should_stop(task: dict) -> bool:
    calls = max(0, int(task.get("model_calls_spent", 0)))
    if calls < STAGNANT_BRANCH_CALL_LIMIT:
        return False
    return branch_efficiency(task) < MIN_GAIN_PER_CALL


def apply_capacity_limit(state: dict, capacity_plan: dict, *, explicit_limit: bool) -> dict:
    budget = state.setdefault("project_budget", {})
    if not isinstance(capacity_plan, dict):
        return budget
    effective = capacity_plan.get("effective_limit")
    if not isinstance(effective, int) or effective < 1:
        return budget
    if explicit_limit:
        return budget
    current = int(budget.get("model_call_limit", effective))
    budget["model_call_limit"] = max(current, effective)
    budget["capacity_scaling"] = dict(capacity_plan)
    return budget


def budget_status(state: dict) -> dict:
    budget = state.get("project_budget", {})
    total_limit = int(budget.get("model_call_limit", 0))
    total_spent = int(budget.get("model_calls_spent", 0))
    repair_limit = int(budget.get("repair_call_limit", 0))
    repair_spent = int(budget.get("repair_calls_spent", 0))
    gain = float(budget.get("diagnostic_gain", 0.0))
    return {
        "model_calls_spent": total_spent,
        "model_call_limit": total_limit,
        "model_calls_remaining": max(0, total_limit - total_spent),
        "repair_calls_spent": repair_spent,
        "repair_call_limit": repair_limit,
        "repair_calls_remaining": max(0, repair_limit - repair_spent),
        "successful_repairs": int(budget.get("successful_repairs", 0)),
        "failed_repairs": int(budget.get("failed_repairs", 0)),
        "diagnostic_gain": gain,
        "exhausted": total_spent >= total_limit or repair_spent >= repair_limit,
    }
