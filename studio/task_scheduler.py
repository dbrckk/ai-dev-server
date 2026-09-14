"""Global repair scheduler over the persistent queue and pipeline state."""
from __future__ import annotations

from project_budget import branch_efficiency, budget_status
from repair_queue import recover_expired_leases

TERMINAL = {"completed", "superseded", "exhausted"}
RELEASE_STAGE_ORDER = (
    "release_build",
    "real_device",
    "capability_qa",
    "performance_qa",
    "native_qa",
    "notification_qa",
    "billing_qa",
    "platform_view_qa",
    "store_metadata",
    "artwork_qa",
    "privacy_policy",
    "security_scan",
    "play_publish",
)
PREVIEW_STAGES = {"preview_validation", "code_review", "visual_review", "preview"}


def _completed_ids(state: dict) -> set[str]:
    queue = state.get("repair_queue", [])
    if not isinstance(queue, list):
        return set()
    return {
        task.get("id")
        for task in queue
        if isinstance(task, dict) and task.get("status") == "completed"
    }


def _dependencies_ready(task: dict, completed: set[str]) -> bool:
    deps = task.get("dependencies", [])
    return isinstance(deps, list) and not (set(deps) - completed)


def _budget_feasible(state: dict, task: dict) -> bool:
    action = task.get("action")
    estimate = max(0, int(task.get("estimated_model_calls", 0)))
    budget = budget_status(state)
    if estimate > int(budget.get("model_calls_remaining", 0)):
        return False
    if action == "repair_code" and estimate > int(budget.get("repair_calls_remaining", 0)):
        return False
    return True


def _pipeline_ready(state: dict, task: dict) -> bool:
    stage = task.get("stage")
    if stage in PREVIEW_STAGES:
        return state.get("status") not in {"finished"}
    if stage not in RELEASE_STAGE_ORDER:
        return True
    if state.get("validation_contract") != 2:
        return False
    release = state.get("release_evidence", {})
    index = RELEASE_STAGE_ORDER.index(stage)
    for prior in RELEASE_STAGE_ORDER[:index]:
        if prior in {"performance_qa", "native_qa", "notification_qa", "billing_qa", "platform_view_qa"}:
            required = (
                state.get("release_evidence", {})
                .get("capability_qa", {})
                .get("required_qa_stages", [])
            )
            if prior not in required:
                continue
        evidence = release.get(prior)
        if not isinstance(evidence, dict) or evidence.get("passed") is not True:
            return False
    return True


def _score(task: dict) -> float:
    priority = float(task.get("priority", 0))
    attempts = max(0, int(task.get("attempts", 0)))
    stagnation = max(0, int(task.get("stagnation_count", 0)))
    estimate = max(0, int(task.get("estimated_model_calls", 0)))
    efficiency = branch_efficiency(task)
    return priority + min(15.0, efficiency * 10.0) - attempts * 1.5 - stagnation * 2.0 - estimate


def candidates(state: dict) -> list[dict]:
    recover_expired_leases(state)
    queue = state.get("repair_queue", [])
    if not isinstance(queue, list):
        return []
    completed = _completed_ids(state)
    result = []
    for task in queue:
        if not isinstance(task, dict):
            continue
        if task.get("status") in TERMINAL or task.get("status") not in {"pending", "retry"}:
            continue
        if task.get("action") not in {"repair_code", "retry_environment", "satisfy_prerequisite"}:
            continue
        if not _dependencies_ready(task, completed):
            continue
        if not _budget_feasible(state, task):
            continue
        if not _pipeline_ready(state, task):
            continue
        result.append(task)
    return result


def select(state: dict) -> dict | None:
    ready = candidates(state)
    if not ready:
        return None
    return sorted(
        ready,
        key=lambda task: (-_score(task), str(task.get("id", ""))),
    )[0]


def dispatch(state: dict) -> dict:
    task = select(state)
    if task is None:
        return {
            "task_id": None,
            "stage": None,
            "action": None,
            "score": None,
            "reason": "no_runnable_repair_task",
        }
    return {
        "task_id": task.get("id"),
        "stage": task.get("stage"),
        "action": task.get("action"),
        "score": round(_score(task), 3),
        "reason": "highest_scoring_runnable_task",
    }


def pipeline_stage_for_task(task: dict | None) -> str | None:
    if not isinstance(task, dict):
        return None
    action = task.get("action")
    blockers = set(task.get("blockers", []))
    if action == "satisfy_prerequisite" and blockers & {
        "release_apk_missing",
        "release_artifact_rebuild_required",
    }:
        return "release_build"
    stage = task.get("stage")
    if stage in PREVIEW_STAGES:
        return "preview"
    if stage in RELEASE_STAGE_ORDER:
        return stage
    return None
