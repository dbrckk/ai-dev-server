"""Semantic checkpoints for resumable objective DAG tasks."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path

VERSION = 1
MAX_TASKS = 64
MAX_ATTEMPTS_PER_TASK = 6


class TaskSemanticCheckpointError(ValueError):
    pass


def _canonical(value: dict) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _seal(value: dict) -> dict:
    item = dict(value)
    item.pop("sha256", None)
    item["sha256"] = hashlib.sha256(_canonical(item)).hexdigest()
    return item


def new(project_id: str, objective_sha256: str, base_sha: str) -> dict:
    if not isinstance(project_id, str) or not project_id.strip():
        raise TaskSemanticCheckpointError("task semantic project invalid")
    if not isinstance(objective_sha256, str) or len(objective_sha256) != 64:
        raise TaskSemanticCheckpointError("task semantic objective invalid")
    if not isinstance(base_sha, str) or len(base_sha) != 40:
        raise TaskSemanticCheckpointError("task semantic base sha invalid")
    return _seal({
        "version": VERSION,
        "project_id": project_id,
        "objective_sha256": objective_sha256,
        "head_sha": base_sha,
        "tasks": {},
    })


def validate(value: dict) -> dict:
    if not isinstance(value, dict):
        raise TaskSemanticCheckpointError("task semantic checkpoint invalid")
    digest = value.get("sha256")
    if not isinstance(digest, str) or len(digest) != 64:
        raise TaskSemanticCheckpointError("task semantic digest invalid")
    unsigned = dict(value)
    unsigned.pop("sha256", None)
    if hashlib.sha256(_canonical(unsigned)).hexdigest() != digest:
        raise TaskSemanticCheckpointError("task semantic integrity failure")
    if value.get("version") != VERSION:
        raise TaskSemanticCheckpointError("task semantic version invalid")
    if not isinstance(value.get("project_id"), str) or not value["project_id"]:
        raise TaskSemanticCheckpointError("task semantic project invalid")
    if not isinstance(value.get("objective_sha256"), str) or len(value["objective_sha256"]) != 64:
        raise TaskSemanticCheckpointError("task semantic objective invalid")
    if not isinstance(value.get("head_sha"), str) or len(value["head_sha"]) != 40:
        raise TaskSemanticCheckpointError("task semantic head sha invalid")
    tasks = value.get("tasks")
    if not isinstance(tasks, dict) or len(tasks) > MAX_TASKS:
        raise TaskSemanticCheckpointError("task semantic tasks invalid")
    for task_id, row in tasks.items():
        if not isinstance(task_id, str) or not task_id or not isinstance(row, dict):
            raise TaskSemanticCheckpointError("task semantic task invalid")
        attempts = row.get("attempts", [])
        if not isinstance(attempts, list) or len(attempts) > MAX_ATTEMPTS_PER_TASK:
            raise TaskSemanticCheckpointError("task semantic attempts invalid")
        for attempt in attempts:
            if not isinstance(attempt, dict):
                raise TaskSemanticCheckpointError("task semantic attempt invalid")
            commit = attempt.get("commit")
            if commit is not None and (not isinstance(commit, str) or len(commit) != 40):
                raise TaskSemanticCheckpointError("task semantic commit invalid")
            if not isinstance(attempt.get("changed_files", []), list):
                raise TaskSemanticCheckpointError("task semantic files invalid")
            if not isinstance(attempt.get("models", []), list):
                raise TaskSemanticCheckpointError("task semantic models invalid")
            if not isinstance(attempt.get("agents", []), list):
                raise TaskSemanticCheckpointError("task semantic agents invalid")
    return value


def resume(
    value: dict,
    *,
    project_id: str,
    objective_sha256: str,
    head_sha: str,
) -> dict:
    validate(value)
    if (
        value.get("project_id") != project_id
        or value.get("objective_sha256") != objective_sha256
    ):
        return new(project_id, objective_sha256, head_sha)
    unsigned = dict(value)
    unsigned.pop("sha256", None)
    unsigned["head_sha"] = head_sha
    return _seal(unsigned)


def record(
    value: dict,
    *,
    task_id: str,
    task_title: str,
    commit: str | None,
    status: str,
    changed_files: list[str],
    impacted_tests: list[str],
    models: list[dict],
    agents: list[str],
    failure_signature: str | None,
    verification: dict | None,
    dependency_context: dict | None,
) -> dict:
    validate(value)
    if not isinstance(task_id, str) or not task_id:
        raise TaskSemanticCheckpointError("task semantic task id invalid")
    if status not in {"verified", "failed", "rejected", "deferred"}:
        raise TaskSemanticCheckpointError("task semantic status invalid")
    if commit is not None and (not isinstance(commit, str) or len(commit) != 40):
        raise TaskSemanticCheckpointError("task semantic commit invalid")
    unsigned = dict(value)
    unsigned.pop("sha256", None)
    tasks = {key: dict(row) for key, row in unsigned["tasks"].items()}
    row = dict(tasks.get(task_id, {
        "title": task_title,
        "attempts": [],
        "last_status": None,
        "last_commit": None,
    }))
    attempt = {
        "status": status,
        "commit": commit,
        "changed_files": sorted(set(str(x) for x in changed_files if x))[:100],
        "impacted_tests": sorted(set(str(x) for x in impacted_tests if x))[:100],
        "models": [
            {
                "provider": str(item.get("provider") or ""),
                "model": str(item.get("model") or ""),
            }
            for item in models if isinstance(item, dict)
        ][:20],
        "agents": sorted(set(str(x) for x in agents if x))[:20],
        "failure_signature": failure_signature,
        "verification": {
            "status": verification.get("status"),
            "passed": verification.get("passed"),
            "elapsed_seconds": verification.get("elapsed_seconds"),
            "stability_confirmed": verification.get("stability_confirmed"),
        } if isinstance(verification, dict) else None,
        "dependency_context": {
            "level": dependency_context.get("level"),
            "max_coupling": dependency_context.get("max_coupling"),
            "impacted_tests": dependency_context.get("impacted_tests", [])[:50],
        } if isinstance(dependency_context, dict) else None,
    }
    attempts = list(row.get("attempts", []))
    attempts.append(attempt)
    row["title"] = task_title
    row["attempts"] = attempts[-MAX_ATTEMPTS_PER_TASK:]
    row["last_status"] = status
    row["last_commit"] = commit
    tasks[task_id] = row
    unsigned["tasks"] = tasks
    if commit is not None:
        unsigned["head_sha"] = commit
    return _seal(unsigned)


def task_context(value: dict, task_id: str) -> dict | None:
    validate(value)
    row = value.get("tasks", {}).get(task_id)
    if not isinstance(row, dict):
        return None
    attempts = row.get("attempts", [])
    return {
        "title": row.get("title"),
        "last_status": row.get("last_status"),
        "last_commit": row.get("last_commit"),
        "recent_attempts": attempts[-3:],
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
        raise TaskSemanticCheckpointError("task semantic checkpoint unreadable") from exc
    return validate(value)


def retry_policy(value: dict, task_id: str) -> dict:
    """Derive bounded task-local routing diversification from recent failed attempts."""
    validate(value)
    row = value.get("tasks", {}).get(task_id)
    if not isinstance(row, dict):
        return {
            "failed_attempts": 0,
            "avoid_agents": [],
            "avoid_providers": [],
            "avoid_models": [],
            "repeated_failure_signature": None,
        }
    attempts = [
        attempt for attempt in row.get("attempts", [])
        if isinstance(attempt, dict) and attempt.get("status") != "verified"
    ][-3:]
    agents = set()
    providers = set()
    models = set()
    signatures = []
    for attempt in attempts:
        agents.update(str(x) for x in attempt.get("agents", []) if x)
        for model in attempt.get("models", []):
            if not isinstance(model, dict):
                continue
            provider = str(model.get("provider") or "").strip()
            model_name = str(model.get("model") or "").strip()
            if provider:
                providers.add(provider)
            if model_name:
                models.add(model_name)
        signature = attempt.get("failure_signature")
        if isinstance(signature, str) and len(signature) == 64:
            signatures.append(signature)
    repeated_signature = None
    if len(signatures) >= 2 and len(set(signatures[-2:])) == 1:
        repeated_signature = signatures[-1]
    return {
        "failed_attempts": len(attempts),
        "avoid_agents": sorted(agents),
        "avoid_providers": sorted(providers),
        "avoid_models": sorted(models),
        "repeated_failure_signature": repeated_signature,
    }


def stagnation_guard(value: dict, task_id: str) -> dict:
    validate(value)
    row = value.get("tasks", {}).get(task_id)
    if not isinstance(row, dict):
        return {"active": False, "blocked_file_set": [], "failure_signature": None}
    attempts = [
        attempt for attempt in row.get("attempts", [])
        if isinstance(attempt, dict) and attempt.get("status") != "verified"
    ][-2:]
    if len(attempts) < 2:
        return {"active": False, "blocked_file_set": [], "failure_signature": None}
    signatures = [attempt.get("failure_signature") for attempt in attempts]
    file_sets = [sorted(set(attempt.get("changed_files", []))) for attempt in attempts]
    if (
        signatures[0]
        and signatures[0] == signatures[1]
        and file_sets[0]
        and file_sets[0] == file_sets[1]
    ):
        return {
            "active": True,
            "blocked_file_set": file_sets[0],
            "failure_signature": signatures[0],
        }
    return {"active": False, "blocked_file_set": [], "failure_signature": None}


def reject_stagnant_surface(guard: dict, changed_files: list[str]) -> bool:
    if not isinstance(guard, dict) or guard.get("active") is not True:
        return False
    return sorted(set(changed_files)) == sorted(set(guard.get("blocked_file_set", [])))


def affected_verified_tasks(value: dict, changed_files: list[str], dependency_graph: dict | None) -> list[str]:
    """Return previously verified tasks whose evidence surface is affected by new changes."""
    validate(value)
    changed = {str(x) for x in changed_files if x}
    if not changed:
        return []
    edges = dependency_graph.get("edges", {}) if isinstance(dependency_graph, dict) else {}
    reverse = dependency_graph.get("reverse", {}) if isinstance(dependency_graph, dict) else {}
    affected = set(changed)
    frontier = list(changed)
    depth = 0
    while frontier and depth < 2 and len(affected) < 300:
        nxt = []
        for rel in frontier:
            for neighbor in [*edges.get(rel, []), *reverse.get(rel, [])]:
                if neighbor not in affected:
                    affected.add(neighbor)
                    nxt.append(neighbor)
        frontier = nxt
        depth += 1

    task_ids = []
    for task_id, row in value.get("tasks", {}).items():
        if not isinstance(row, dict) or row.get("last_status") != "verified":
            continue
        attempts = row.get("attempts", [])
        verified_attempt = next(
            (attempt for attempt in reversed(attempts) if isinstance(attempt, dict) and attempt.get("status") == "verified"),
            None,
        )
        if not isinstance(verified_attempt, dict):
            continue
        evidence_files = set(verified_attempt.get("changed_files", []))
        evidence_tests = set(verified_attempt.get("impacted_tests", []))
        if affected & (evidence_files | evidence_tests):
            task_ids.append(task_id)
    return sorted(task_ids)
