"""Persistent deterministic repair-task queue stored inside studio state."""
from __future__ import annotations

import hashlib
import json

MAX_TASKS = 64
MAX_ATTEMPTS = 4

ACTION_PRIORITY = {
    "human_action": 100,
    "satisfy_prerequisite": 90,
    "repair_code": 80,
    "retry_environment": 60,
    "investigate_unknown": 40,
    "complete": 0,
}


def _fingerprint(stage: str, action: str, blockers: list[str]) -> str:
    raw = json.dumps(
        {"stage": stage, "action": action, "blockers": sorted(set(blockers))},
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return hashlib.sha256(raw).hexdigest()[:16]


def _queue(state: dict) -> list[dict]:
    value = state.setdefault("repair_queue", [])
    if not isinstance(value, list):
        value = []
        state["repair_queue"] = value
    return value


def enqueue(
    state: dict,
    repair_plan: dict,
    *,
    dependencies: list[str] | None = None,
    estimated_model_calls: int = 0,
) -> dict | None:
    action = repair_plan.get("action")
    blockers = [
        blocker for blocker in repair_plan.get("blockers", [])
        if isinstance(blocker, str) and blocker
    ]
    stage = repair_plan.get("stage")
    if not isinstance(stage, str) or not stage or action == "complete":
        return None

    task_id = _fingerprint(stage, str(action), blockers)
    queue = _queue(state)
    for task in queue:
        if task.get("id") != task_id:
            continue
        task["seen_count"] = int(task.get("seen_count", 1)) + 1
        if task.get("status") == "completed":
            task["status"] = "retry"
            task["stagnation_count"] = int(task.get("stagnation_count", 0)) + 1
        elif task.get("status") != "superseded":
            task["stagnation_count"] = int(task.get("stagnation_count", 0)) + 1
        if int(task.get("stagnation_count", 0)) >= 2:
            task["strategy_generation"] = int(task.get("strategy_generation", 0)) + 1
            task["rotate_strategy"] = True
        task["priority"] = score_task(task)
        return task

    task = {
        "id": task_id,
        "stage": stage,
        "action": action,
        "blockers": sorted(set(blockers)),
        "status": "pending",
        "attempts": 0,
        "max_attempts": MAX_ATTEMPTS,
        "seen_count": 1,
        "stagnation_count": 0,
        "dependencies": sorted(set(dependencies or [])),
        "estimated_model_calls": max(0, int(estimated_model_calls)),
        "model_calls_spent": 0,
        "strategy_generation": 0,
    }
    task["priority"] = score_task(task)
    queue.append(task)
    if len(queue) > MAX_TASKS:
        terminal = [x for x in queue if x.get("status") in {"completed", "superseded"}]
        while len(queue) > MAX_TASKS and terminal:
            victim = terminal.pop(0)
            queue.remove(victim)
    return task


def score_task(task: dict) -> int:
    base = int(ACTION_PRIORITY.get(task.get("action"), 20))
    attempts = max(0, int(task.get("attempts", 0)))
    stagnation = max(0, int(task.get("stagnation_count", 0)))
    dependency_penalty = 20 if task.get("dependencies") else 0
    cost_penalty = min(15, max(0, int(task.get("estimated_model_calls", 0))) * 3)
    return max(0, base - attempts * 5 - stagnation * 3 - dependency_penalty - cost_penalty)


def next_task(state: dict) -> dict | None:
    queue = _queue(state)
    completed = {x.get("id") for x in queue if x.get("status") == "completed"}
    candidates = []
    for task in queue:
        if task.get("status") not in {"pending", "retry"}:
            continue
        if int(task.get("attempts", 0)) >= int(task.get("max_attempts", MAX_ATTEMPTS)):
            task["status"] = "exhausted"
            continue
        deps = set(task.get("dependencies", []))
        if deps - completed:
            continue
        task["priority"] = score_task(task)
        candidates.append(task)
    if not candidates:
        return None
    return sorted(candidates, key=lambda x: (-int(x.get("priority", 0)), x.get("id", "")))[0]


def begin_attempt(task: dict) -> dict:
    task["attempts"] = int(task.get("attempts", 0)) + 1
    task["status"] = "running"
    return task


def finish_attempt(
    task: dict,
    *,
    success: bool,
    model_calls: int = 0,
    improved: bool = True,
    providers_used: dict | None = None,
) -> dict:
    task["model_calls_spent"] = int(task.get("model_calls_spent", 0)) + max(0, int(model_calls))
    providers = providers_used or {}
    if isinstance(providers, dict):
        used = [name for name in providers.values() if isinstance(name, str) and name]
        if used:
            history = list(task.get("providers_history", []))
            history.extend(used)
            task["providers_history"] = history[-8:]
            task["last_provider"] = used[-1]
    if success:
        task["status"] = "completed"
        task["stagnation_count"] = 0
        return task
    if not improved:
        task["stagnation_count"] = int(task.get("stagnation_count", 0)) + 1
    if int(task.get("attempts", 0)) >= int(task.get("max_attempts", MAX_ATTEMPTS)):
        task["status"] = "exhausted"
    else:
        task["status"] = "retry"
    if int(task.get("stagnation_count", 0)) >= 2:
        task["strategy_generation"] = int(task.get("strategy_generation", 0)) + 1
        task["rotate_strategy"] = True
    task["priority"] = score_task(task)
    return task


def complete_stage_tasks(state: dict, stage: str) -> None:
    for task in _queue(state):
        if task.get("stage") == stage and task.get("status") not in {"completed", "superseded"}:
            task["status"] = "completed"


def summarize(state: dict) -> dict:
    queue = _queue(state)
    return {
        "total": len(queue),
        "pending": sum(1 for x in queue if x.get("status") in {"pending", "retry"}),
        "running": sum(1 for x in queue if x.get("status") == "running"),
        "completed": sum(1 for x in queue if x.get("status") == "completed"),
        "exhausted": sum(1 for x in queue if x.get("status") == "exhausted"),
        "model_calls_spent": sum(int(x.get("model_calls_spent", 0)) for x in queue),
        "next_task": (next_task(state) or {}).get("id"),
    }
