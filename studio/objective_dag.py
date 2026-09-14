"""Persistent objective DAG for resumable generic-project subgoals."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path

VERSION = 1
_STATES = {"blocked", "ready", "running", "verified", "failed"}
MAX_TASKS = 64
MAX_TASK_ATTEMPTS = 3


class ObjectiveDagError(ValueError):
    pass


def _canonical(value: dict) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def objective_fingerprint(brief: str) -> str:
    if not isinstance(brief, str) or not brief.strip():
        raise ObjectiveDagError("objective brief invalid")
    return hashlib.sha256(" ".join(brief.split()).encode("utf-8")).hexdigest()


def _seal(value: dict) -> dict:
    item = dict(value)
    item.pop("sha256", None)
    item["sha256"] = hashlib.sha256(_canonical(item)).hexdigest()
    return item


def _normalized_tasks(plan: dict) -> list[dict]:
    explicit = plan.get("tasks") if isinstance(plan, dict) else None
    tasks = []
    if isinstance(explicit, list) and explicit:
        for index, raw in enumerate(explicit, 1):
            if not isinstance(raw, dict):
                raise ObjectiveDagError("objective task invalid")
            task_id = str(raw.get("id") or f"task-{index}").strip()
            title = str(raw.get("title") or raw.get("work") or "").strip()
            deps = raw.get("depends_on", [])
            done_when = raw.get("done_when", [])
            if not task_id or not title or not isinstance(deps, list) or not isinstance(done_when, list):
                raise ObjectiveDagError("objective task fields invalid")
            tasks.append({
                "id": task_id,
                "title": title,
                "depends_on": sorted(set(str(x).strip() for x in deps if str(x).strip())),
                "critical": bool(raw.get("critical", False)),
                "done_when": [
                    str(item).strip()
                    for item in done_when
                    if str(item).strip()
                ][:12],
            })
    else:
        work_items = plan.get("work_items", []) if isinstance(plan, dict) else []
        if not isinstance(work_items, list):
            raise ObjectiveDagError("objective work items invalid")
        previous = None
        for index, item in enumerate(work_items, 1):
            title = str(item).strip()
            if not title:
                continue
            task_id = f"task-{index}"
            tasks.append({
                "id": task_id,
                "title": title,
                "depends_on": [previous] if previous else [],
                "critical": False,
                "done_when": [title],
            })
            previous = task_id

    if not tasks:
        objective = str(plan.get("objective", "")).strip() if isinstance(plan, dict) else ""
        if objective:
            tasks = [{"id": "task-1", "title": objective, "depends_on": [], "critical": False, "done_when": [objective]}]
    if not tasks or len(tasks) > MAX_TASKS:
        raise ObjectiveDagError("objective task count invalid")
    return tasks


def _validate_acyclic(tasks: list[dict]) -> None:
    ids = [task["id"] for task in tasks]
    if len(set(ids)) != len(ids):
        raise ObjectiveDagError("objective task ids duplicated")
    known = set(ids)
    dependencies = {}
    for task in tasks:
        deps = task["depends_on"]
        if task["id"] in deps or any(dep not in known for dep in deps):
            raise ObjectiveDagError("objective task dependency invalid")
        dependencies[task["id"]] = set(deps)

    remaining = {key: set(value) for key, value in dependencies.items()}
    resolved = set()
    while remaining:
        ready = sorted(key for key, deps in remaining.items() if deps <= resolved)
        if not ready:
            raise ObjectiveDagError("objective task graph cyclic")
        for key in ready:
            resolved.add(key)
            remaining.pop(key)


def new(project_id: str, brief: str, plan: dict, base_sha: str) -> dict:
    if not isinstance(project_id, str) or not project_id.strip():
        raise ObjectiveDagError("objective project invalid")
    if not isinstance(base_sha, str) or len(base_sha) != 40:
        raise ObjectiveDagError("objective base sha invalid")
    tasks = _normalized_tasks(plan)
    _validate_acyclic(tasks)
    rows = []
    for task in tasks:
        rows.append({
            **task,
            "state": "ready" if not task["depends_on"] else "blocked",
            "critical": bool(task.get("critical", False)),
            "confidence": None,
            "done_when": list(task.get("done_when", [])),
            "attempts": 0,
            "last_commit": None,
            "last_error": None,
        })
    return _seal({
        "version": VERSION,
        "project_id": project_id,
        "objective_sha256": objective_fingerprint(brief),
        "created_from_sha": base_sha,
        "head_sha": base_sha,
        "tasks": rows,
    })


def validate(value: dict) -> dict:
    if not isinstance(value, dict):
        raise ObjectiveDagError("objective dag invalid")
    digest = value.get("sha256")
    if not isinstance(digest, str) or len(digest) != 64:
        raise ObjectiveDagError("objective dag digest invalid")
    unsigned = dict(value)
    unsigned.pop("sha256", None)
    if hashlib.sha256(_canonical(unsigned)).hexdigest() != digest:
        raise ObjectiveDagError("objective dag integrity failure")
    if value.get("version") != VERSION:
        raise ObjectiveDagError("objective dag version invalid")
    if not isinstance(value.get("project_id"), str) or not value["project_id"]:
        raise ObjectiveDagError("objective dag project invalid")
    if not isinstance(value.get("objective_sha256"), str) or len(value["objective_sha256"]) != 64:
        raise ObjectiveDagError("objective fingerprint invalid")
    for key in ("created_from_sha", "head_sha"):
        if not isinstance(value.get(key), str) or len(value[key]) != 40:
            raise ObjectiveDagError("objective dag sha invalid")
    tasks = value.get("tasks")
    if not isinstance(tasks, list) or not tasks or len(tasks) > MAX_TASKS:
        raise ObjectiveDagError("objective dag tasks invalid")
    structural = []
    for task in tasks:
        if not isinstance(task, dict):
            raise ObjectiveDagError("objective dag task invalid")
        if task.get("state") not in _STATES:
            raise ObjectiveDagError("objective dag state invalid")
        attempts = task.get("attempts")
        if type(attempts) is not int or attempts < 0:
            raise ObjectiveDagError("objective dag attempts invalid")
        confidence = task.get("confidence")
        if confidence is not None and (type(confidence) is not int or confidence < 0 or confidence > 100):
            raise ObjectiveDagError("objective dag confidence invalid")
        done_when = task.get("done_when", [])
        if not isinstance(done_when, list) or any(not isinstance(item, str) or not item for item in done_when):
            raise ObjectiveDagError("objective dag done_when invalid")
        structural.append({
            "id": task.get("id"),
            "title": task.get("title"),
            "depends_on": task.get("depends_on"),
            "critical": bool(task.get("critical", False)),
            "done_when": done_when,
        })
    _validate_acyclic(structural)
    return value


def resume(value: dict, *, project_id: str, brief: str, head_sha: str) -> dict:
    validate(value)
    if value["project_id"] != project_id or value["objective_sha256"] != objective_fingerprint(brief):
        raise ObjectiveDagError("objective dag identity mismatch")
    rows = []
    for task in value["tasks"]:
        item = dict(task)
        if item["state"] == "running":
            item["state"] = "ready"
        rows.append(item)
    refreshed = dict(value)
    refreshed["head_sha"] = head_sha
    refreshed["tasks"] = rows
    return refresh(_seal(refreshed))


def refresh(value: dict) -> dict:
    unsigned = dict(value)
    unsigned.pop("sha256", None)
    tasks = [dict(task) for task in unsigned["tasks"]]
    verified = {task["id"] for task in tasks if task["state"] == "verified"}
    task_by_id = {task["id"]: task for task in tasks}
    for task in tasks:
        if task["state"] in {"verified", "running", "failed"}:
            continue
        dependencies_verified = set(task["depends_on"]) <= verified
        confidence_ok = True
        if task.get("critical") and dependencies_verified:
            confidence_ok = all(
                int(task_by_id[dep].get("confidence") or 0) >= 85
                for dep in task["depends_on"]
            )
        task["state"] = "ready" if dependencies_verified and confidence_ok else "blocked"
    unsigned["tasks"] = tasks
    return _seal(unsigned)


def next_task(value: dict) -> dict | None:
    validate(value)
    refreshed = refresh(value)
    ready = [task for task in refreshed["tasks"] if task["state"] == "ready"]
    failed = [
        task for task in refreshed["tasks"]
        if task["state"] == "failed" and task["attempts"] < MAX_TASK_ATTEMPTS
    ]
    candidates = ready or failed
    if not candidates:
        return None
    return dict(sorted(candidates, key=lambda task: (task["attempts"], task["id"]))[0])


def mark_running(value: dict, task_id: str) -> dict:
    validate(value)
    unsigned = dict(value)
    unsigned.pop("sha256", None)
    tasks = [dict(task) for task in unsigned["tasks"]]
    found = False
    for task in tasks:
        if task["id"] != task_id:
            continue
        if task["state"] not in {"ready", "failed"}:
            raise ObjectiveDagError("objective task not runnable")
        if task["attempts"] >= MAX_TASK_ATTEMPTS:
            raise ObjectiveDagError("objective task retry budget exhausted")
        task["state"] = "running"
        task["attempts"] += 1
        task["last_error"] = None
        found = True
    if not found:
        raise ObjectiveDagError("objective task missing")
    unsigned["tasks"] = tasks
    return _seal(unsigned)


def mark_verified(value: dict, task_id: str, *, commit: str, confidence: int | None = None) -> dict:
    validate(value)
    if not isinstance(commit, str) or len(commit) != 40:
        raise ObjectiveDagError("objective task commit invalid")
    if confidence is not None and (type(confidence) is not int or confidence < 0 or confidence > 100):
        raise ObjectiveDagError("objective task confidence invalid")
    unsigned = dict(value)
    unsigned.pop("sha256", None)
    tasks = [dict(task) for task in unsigned["tasks"]]
    found = False
    for task in tasks:
        if task["id"] == task_id:
            task["state"] = "verified"
            task["last_commit"] = commit
            task["last_error"] = None
            task["confidence"] = confidence
            found = True
    if not found:
        raise ObjectiveDagError("objective task missing")
    unsigned["head_sha"] = commit
    unsigned["tasks"] = tasks
    return refresh(_seal(unsigned))


def mark_failed(value: dict, task_id: str, *, error: str) -> dict:
    validate(value)
    unsigned = dict(value)
    unsigned.pop("sha256", None)
    tasks = [dict(task) for task in unsigned["tasks"]]
    found = False
    for task in tasks:
        if task["id"] == task_id:
            task["state"] = "failed"
            task["last_error"] = str(error)[:1000]
            found = True
    if not found:
        raise ObjectiveDagError("objective task missing")
    unsigned["tasks"] = tasks
    return _seal(unsigned)


def summary(value: dict) -> dict:
    validate(value)
    refreshed = refresh(value)
    counts = {state: 0 for state in sorted(_STATES)}
    for task in refreshed["tasks"]:
        counts[task["state"]] += 1
    current = next_task(refreshed)
    task_by_id = {task["id"]: task for task in refreshed["tasks"]}
    confidence_blockers = []
    for task in refreshed["tasks"]:
        if task["state"] != "blocked" or not task.get("critical"):
            continue
        for dep_id in task["depends_on"]:
            dep = task_by_id[dep_id]
            if dep["state"] == "verified" and int(dep.get("confidence") or 0) < 85:
                confidence_blockers.append({
                    "critical_task": task["id"],
                    "dependency": dep_id,
                    "confidence": dep.get("confidence"),
                })
    stalled = [
        {
            "id": task["id"],
            "title": task["title"],
            "attempts": task["attempts"],
            "last_error": task.get("last_error"),
        }
        for task in refreshed["tasks"]
        if task["state"] == "failed" and task["attempts"] >= MAX_TASK_ATTEMPTS
    ]
    return {
        "counts": counts,
        "complete": counts["verified"] == len(refreshed["tasks"]),
        "next_task": current,
        "stalled_tasks": stalled,
        "confidence_blockers": confidence_blockers,
        "tasks": [
            {
                "id": task["id"],
                "title": task["title"],
                "depends_on": task["depends_on"],
                "critical": bool(task.get("critical", False)),
                "done_when": list(task.get("done_when", [])),
                "confidence": task.get("confidence"),
                "state": task["state"],
                "attempts": task["attempts"],
            }
            for task in refreshed["tasks"]
        ],
    }


def save(path: Path, value: dict) -> None:
    validate(value)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, sort_keys=True, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass


def load(path: Path) -> dict:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ObjectiveDagError("objective dag unreadable") from exc
    return validate(value)


def task_context(value: dict, task_id: str) -> dict:
    """Return bounded context for one resumable objective task."""
    validate(value)
    tasks = {task["id"]: task for task in value["tasks"]}
    task = tasks.get(task_id)
    if task is None:
        raise ObjectiveDagError("objective task missing")
    dependencies = []
    for dep_id in task["depends_on"]:
        dep = tasks[dep_id]
        dependencies.append({
            "id": dep["id"],
            "title": dep["title"],
            "state": dep["state"],
            "last_commit": dep.get("last_commit"),
            "confidence": dep.get("confidence"),
        })
    return {
        "id": task["id"],
        "title": task["title"],
        "state": task["state"],
        "attempts": task["attempts"],
        "depends_on": task["depends_on"],
        "critical": bool(task.get("critical", False)),
        "done_when": list(task.get("done_when", [])),
        "confidence": task.get("confidence"),
        "verified_dependencies": dependencies,
    }


def append_amendments(value: dict, items: list[str]) -> dict:
    """Append review-derived work after a fully verified DAG."""
    validate(value)
    clean = [str(item).strip() for item in items if str(item).strip()]
    if not clean:
        raise ObjectiveDagError("objective amendment items invalid")
    unsigned = dict(value)
    unsigned.pop("sha256", None)
    tasks = [dict(task) for task in unsigned["tasks"]]
    if any(task["state"] != "verified" for task in tasks):
        raise ObjectiveDagError("objective amendments require verified DAG")
    if len(tasks) + len(clean) > MAX_TASKS:
        raise ObjectiveDagError("objective task count invalid")

    all_previous = [task["id"] for task in tasks]
    prefix_index = 1
    existing = {task["id"] for task in tasks}
    previous_new = None
    for title in clean:
        while f"amendment-{prefix_index}" in existing:
            prefix_index += 1
        task_id = f"amendment-{prefix_index}"
        dependencies = [previous_new] if previous_new else list(all_previous)
        tasks.append({
            "id": task_id,
            "title": title,
            "depends_on": dependencies,
            "state": "ready" if not dependencies or all(dep in all_previous for dep in dependencies) else "blocked",
            "critical": False,
            "done_when": [title],
            "confidence": None,
            "attempts": 0,
            "last_commit": None,
            "last_error": None,
        })
        existing.add(task_id)
        previous_new = task_id
        prefix_index += 1

    unsigned["tasks"] = tasks
    return refresh(_seal(unsigned))


def reopen_confidence_dependency(value: dict, task_id: str, *, minimum: int = 85, reason: str | None = None) -> dict:
    """Re-open a verified low-confidence task for one bounded revalidation attempt."""
    validate(value)
    if type(minimum) is not int or minimum < 0 or minimum > 100:
        raise ObjectiveDagError("objective confidence threshold invalid")
    unsigned = dict(value)
    unsigned.pop("sha256", None)
    tasks = [dict(task) for task in unsigned["tasks"]]
    found = False
    for task in tasks:
        if task["id"] != task_id:
            continue
        if task["state"] != "verified":
            raise ObjectiveDagError("confidence dependency is not verified")
        if int(task.get("confidence") or 0) >= minimum:
            raise ObjectiveDagError("confidence dependency already sufficient")
        if task["attempts"] >= MAX_TASK_ATTEMPTS:
            raise ObjectiveDagError("objective task retry budget exhausted")
        task["state"] = "ready"
        task["last_error"] = str(reason or "revalidation required for confidence gate")[:1000]
        found = True
    if not found:
        raise ObjectiveDagError("objective task missing")
    unsigned["tasks"] = tasks
    return refresh(_seal(unsigned))


def invalidate_confidence(value: dict, task_ids: list[str]) -> dict:
    """Invalidate confidence evidence while preserving historical verified state."""
    validate(value)
    targets = {str(task_id) for task_id in task_ids if task_id}
    if not targets:
        return value
    unsigned = dict(value)
    unsigned.pop("sha256", None)
    tasks = [dict(task) for task in unsigned["tasks"]]
    known = {task["id"] for task in tasks}
    unknown = targets - known
    if unknown:
        raise ObjectiveDagError("objective confidence task missing")
    for task in tasks:
        if task["id"] in targets and task["state"] == "verified":
            task["confidence"] = None
            task["last_error"] = "confidence invalidated by affected downstream change"
    unsigned["tasks"] = tasks
    return refresh(_seal(unsigned))
