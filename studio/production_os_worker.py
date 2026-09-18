"""Production-OS worker bridge helpers for AI Dev Server."""
from __future__ import annotations

import hashlib
import re
from typing import Any


def _project_id(job_key: str) -> str:
    digest = hashlib.sha256(str(job_key).encode("utf-8")).hexdigest()[:24]
    return "pos-" + digest


def _app_name(repository: str) -> str:
    name = str(repository).rsplit("/", 1)[-1].lower()
    name = re.sub(r"[^a-z0-9_]+", "_", name).strip("_")
    if not name or not name[0].isalpha():
        name = "app_" + name
    if len(name) < 3:
        name = (name + "_app")[:40]
    return name[:40]


def _brief(task: str, final_goal: str) -> str:
    task = str(task or "").strip()
    final_goal = str(final_goal or "").strip()
    value = task or final_goal
    if len(value) >= 20:
        return value[:24000]
    expanded = (
        f"Complete this repository objective: {value}. "
        f"Final goal: {final_goal or value}."
    )
    return expanded[:24000]


def build_studio_request(job: dict[str, Any]) -> dict[str, Any]:
    """Convert one claimed Production-OS job to the trusted Studio request."""
    if not isinstance(job, dict):
        raise ValueError("Production-OS job must be an object")
    payload = job.get("payload")
    if not isinstance(payload, dict):
        raise ValueError("Production-OS job payload missing")
    handoff = payload.get("handoff")
    if not isinstance(handoff, dict):
        raise ValueError("Production-OS handoff missing")

    repository = str(
        handoff.get("repository")
        or job.get("repository")
        or ""
    ).strip()
    task = str(handoff.get("task") or job.get("task") or "").strip()
    final_goal = str(handoff.get("final_goal") or task).strip()
    workflow_id = str(payload.get("workflow_id") or "").strip()
    workflow_task_id = str(payload.get("workflow_task_id") or "").strip()
    job_key = str(job.get("key") or "").strip()

    if not all((repository, task, workflow_id, workflow_task_id, job_key)):
        raise ValueError("Production-OS job correlation is incomplete")

    request = {
        "id": _project_id(job_key),
        "target_repo": repository,
        "app_name": _app_name(repository),
        "brief": _brief(task, final_goal),
        "enabled": True,
        "production_os": {
            "workflow_id": workflow_id,
            "workflow_task_id": workflow_task_id,
        },
    }
    preference = str(handoff.get("agent_preference") or "auto").strip()
    if preference:
        request["agent_preference"] = preference
    return request


def _result_payload(result: dict[str, Any]) -> dict[str, Any]:
    usage = result.get("usage")
    evidence = result.get("evidence")
    return {
        "usage": dict(usage) if isinstance(usage, dict) else {},
        "evidence": dict(evidence) if isinstance(evidence, dict) else {},
        "ai_dev_server_status": str(result.get("status") or "unknown"),
    }


def completion_payload(
    key: str,
    worker_id: str,
    result: dict[str, Any],
    *,
    duration_seconds: float,
) -> dict[str, Any]:
    return {
        "key": str(key),
        "worker_id": str(worker_id),
        "duration_seconds": max(0.0, float(duration_seconds)),
        "capabilities": ["software-development", "repo-analysis"],
        "result": _result_payload(result),
    }


def failure_payload(
    key: str,
    worker_id: str,
    result: dict[str, Any],
    *,
    duration_seconds: float,
) -> dict[str, Any]:
    status = str(result.get("status") or "failed")
    next_stage = result.get("evidence", {}).get("next_stage") if isinstance(
        result.get("evidence"), dict
    ) else None
    reason = status if not next_stage else f"{status}: {next_stage}"
    return {
        "key": str(key),
        "worker_id": str(worker_id),
        "duration_seconds": max(0.0, float(duration_seconds)),
        "capabilities": ["software-development", "repo-analysis"],
        "reason": reason[:1000],
        "result": _result_payload(result),
    }
