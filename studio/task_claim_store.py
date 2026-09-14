"""Cross-process task claim registry backed by a locked JSON file."""
from __future__ import annotations

import json
import os
from pathlib import Path
import time

from atomic_file import write_text as atomic_write_text
from core import canonical
from file_lock import exclusive

SCHEMA = 1


def _path() -> Path | None:
    raw = os.environ.get("STUDIO_TASK_LEASE_PATH", "").strip()
    return Path(raw) if raw else None


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}
    if not isinstance(data, dict) or data.get("schema") != SCHEMA:
        return {}
    claims = data.get("claims")
    return dict(claims) if isinstance(claims, dict) else {}


def claim(task_id: str, owner: str, token: str, expires_at: float, *, now: float | None = None) -> None:
    path = _path()
    if path is None:
        return
    now_value = time.time() if now is None else float(now)
    with exclusive(path):
        claims = _read(path)
        current = claims.get(task_id)
        if isinstance(current, dict):
            current_owner = current.get("owner")
            current_token = current.get("token")
            current_expires = current.get("expires_at")
            if (
                isinstance(current_expires, (int, float))
                and float(current_expires) > now_value
                and (current_owner != owner or current_token != token)
            ):
                raise RuntimeError("task already claimed by another worker")
        claims[task_id] = {
            "owner": owner,
            "token": token,
            "expires_at": float(expires_at),
        }
        atomic_write_text(path, canonical({"schema": SCHEMA, "claims": claims}))


def heartbeat(task_id: str, owner: str, token: str, expires_at: float, *, now: float | None = None) -> None:
    path = _path()
    if path is None:
        return
    now_value = time.time() if now is None else float(now)
    with exclusive(path):
        claims = _read(path)
        current = claims.get(task_id)
        if not isinstance(current, dict):
            raise RuntimeError("task claim missing")
        if current.get("owner") != owner or current.get("token") != token:
            raise RuntimeError("task claim ownership mismatch")
        current_expires = current.get("expires_at")
        if not isinstance(current_expires, (int, float)) or float(current_expires) <= now_value:
            raise RuntimeError("task claim expired")
        current["expires_at"] = float(expires_at)
        atomic_write_text(path, canonical({"schema": SCHEMA, "claims": claims}))


def release(task_id: str, owner: str | None = None, token: str | None = None) -> None:
    path = _path()
    if path is None:
        return
    with exclusive(path):
        claims = _read(path)
        current = claims.get(task_id)
        if not isinstance(current, dict):
            return
        if owner is not None and current.get("owner") != owner:
            raise RuntimeError("task claim ownership mismatch")
        if token is not None and current.get("token") != token:
            raise RuntimeError("task claim token mismatch")
        claims.pop(task_id, None)
        atomic_write_text(path, canonical({"schema": SCHEMA, "claims": claims}))
