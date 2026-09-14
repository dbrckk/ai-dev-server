"""Worker lease primitives for resumable repair tasks."""
from __future__ import annotations

import json
import os
from pathlib import Path
import socket
import time
import uuid

from task_claim_store import claim as persist_claim, heartbeat as persist_heartbeat, release as persist_release

DEFAULT_LEASE_SECONDS = 60 * 60
MIN_LEASE_SECONDS = 30
MAX_LEASE_SECONDS = 60 * 60


def _validate_persisted_lease_state() -> None:
    raw = os.environ.get("STUDIO_TASK_LEASE_PATH", "").strip()
    if not raw:
        return
    path = Path(raw)
    if not path.is_file():
        return
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        raise RuntimeError("task lease state is unreadable") from None
    if not isinstance(data, dict) or data.get("schema") != 1 or not isinstance(data.get("claims"), dict):
        raise RuntimeError("task lease state is invalid")


def worker_id() -> str:
    configured = os.environ.get("STUDIO_WORKER_ID", "").strip()
    if configured:
        return configured[:128]
    run_id = os.environ.get("STUDIO_RUN_ID", "").strip()
    if run_id:
        return ("run-" + run_id)[:128]
    return f"{socket.gethostname()}:{os.getpid()}"[:128]


def _now(value: float | None = None) -> float:
    return float(time.time() if value is None else value)


def _duration(value: int | float | None) -> int:
    if value is None:
        return DEFAULT_LEASE_SECONDS
    return max(MIN_LEASE_SECONDS, min(MAX_LEASE_SECONDS, int(value)))


def active(task: dict, *, now: float | None = None) -> bool:
    if task.get("status") != "running":
        return False
    owner = task.get("lease_owner")
    expires = task.get("lease_expires_at")
    return (
        isinstance(owner, str)
        and bool(owner)
        and isinstance(expires, (int, float))
        and float(expires) > _now(now)
    )


def expired(task: dict, *, now: float | None = None) -> bool:
    return task.get("status") == "running" and not active(task, now=now)


def claim(
    task: dict,
    *,
    owner: str | None = None,
    lease_seconds: int | float | None = None,
    now: float | None = None,
) -> dict:
    _validate_persisted_lease_state()
    now_value = _now(now)
    owner = (owner or worker_id()).strip()
    if not owner:
        raise ValueError("lease owner required")
    current_owner = task.get("lease_owner")
    if active(task, now=now_value) and current_owner != owner:
        raise RuntimeError("task already leased by another worker")

    duration = _duration(lease_seconds)
    token = uuid.uuid4().hex
    task["lease_owner"] = owner[:128]
    task["lease_token"] = token
    task["lease_started_at"] = now_value
    task["lease_heartbeat_at"] = now_value
    task["lease_expires_at"] = now_value + duration
    task_id = task.get("id")
    if isinstance(task_id, str) and task_id:
        persist_claim(task_id, task["lease_owner"], token, task["lease_expires_at"], now=now_value)
    return task


def heartbeat(
    task: dict,
    *,
    owner: str,
    token: str,
    lease_seconds: int | float | None = None,
    now: float | None = None,
) -> dict:
    _validate_persisted_lease_state()
    now_value = _now(now)
    if task.get("lease_owner") != owner or task.get("lease_token") != token:
        raise RuntimeError("task lease ownership mismatch")
    if expired(task, now=now_value):
        raise RuntimeError("task lease expired")
    duration = _duration(lease_seconds)
    task["lease_heartbeat_at"] = now_value
    task["lease_expires_at"] = now_value + duration
    task_id = task.get("id")
    if isinstance(task_id, str) and task_id:
        persist_heartbeat(task_id, owner, token, task["lease_expires_at"], now=now_value)
    return task


def release(task: dict, *, owner: str | None = None, token: str | None = None) -> dict:
    _validate_persisted_lease_state()
    if owner is not None and task.get("lease_owner") not in {None, owner}:
        raise RuntimeError("task lease ownership mismatch")
    if token is not None and task.get("lease_token") not in {None, token}:
        raise RuntimeError("task lease token mismatch")
    task_id = task.get("id")
    current_owner = task.get("lease_owner")
    current_token = task.get("lease_token")
    if isinstance(task_id, str) and task_id:
        persist_release(task_id, owner=current_owner if owner is None else owner, token=current_token if token is None else token)
    for key in (
        "lease_owner",
        "lease_token",
        "lease_started_at",
        "lease_heartbeat_at",
        "lease_expires_at",
    ):
        task.pop(key, None)
    return task


def recover(task: dict, *, now: float | None = None) -> bool:
    if not expired(task, now=now):
        return False
    release(task)
    task["status"] = "retry"
    task["lease_recovery_count"] = int(task.get("lease_recovery_count", 0)) + 1
    return True
