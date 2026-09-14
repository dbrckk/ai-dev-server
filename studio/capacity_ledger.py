"""Crash-safe token reservation ledger for concurrent autonomous projects."""
from __future__ import annotations

import json
import time
import uuid
from pathlib import Path

from atomic_file import write_text as atomic_write_text
from file_lock import exclusive

SCHEMA = 1
DEFAULT_TTL_SECONDS = 900
MAX_RESERVATIONS = 4096


def _empty() -> dict:
    return {"schema": SCHEMA, "reservations": {}, "consumed": {}}


def _load_unlocked(path: Path) -> dict:
    path = Path(path)
    if not path.is_file():
        return _empty()
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return _empty()
    if not isinstance(value, dict) or value.get("schema") != SCHEMA:
        return _empty()
    reservations = value.get("reservations")
    consumed = value.get("consumed")
    return {
        "schema": SCHEMA,
        "reservations": reservations if isinstance(reservations, dict) else {},
        "consumed": consumed if isinstance(consumed, dict) else {},
    }


def load(path: Path) -> dict:
    return _load_unlocked(Path(path))


def _save_unlocked(path: Path, data: dict) -> None:
    atomic_write_text(
        Path(path),
        json.dumps(data, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def _reap(data: dict, now: float) -> int:
    reservations = data.setdefault("reservations", {})
    expired = [
        key for key, row in reservations.items()
        if not isinstance(row, dict) or float(row.get("expires_at", 0.0) or 0.0) <= now
    ]
    for key in expired:
        reservations.pop(key, None)
    return len(expired)


def reserved_tokens(data: dict, *, provider: str | None = None, project_id: str | None = None) -> int:
    total = 0
    for row in (data.get("reservations") or {}).values():
        if not isinstance(row, dict):
            continue
        if provider is not None and row.get("provider") != provider:
            continue
        if project_id is not None and row.get("project_id") != project_id:
            continue
        total += max(0, int(row.get("reserved_tokens", 0) or 0))
    return total


def consumed_tokens(data: dict, *, project_id: str | None = None, provider: str | None = None) -> int:
    total = 0
    for key, value in (data.get("consumed") or {}).items():
        if not isinstance(key, str):
            continue
        try:
            project, provider_name = key.split("::", 1)
        except ValueError:
            continue
        if project_id is not None and project != project_id:
            continue
        if provider is not None and provider_name != provider:
            continue
        total += max(0, int(value or 0))
    return total


def reserve(
    path: Path,
    *,
    project_id: str,
    provider: str,
    estimated_tokens: int,
    provider_remaining_tokens: int | None,
    project_envelope_tokens: int | None = None,
    ttl_seconds: int = DEFAULT_TTL_SECONDS,
    now: float | None = None,
) -> dict:
    project = str(project_id).strip()
    provider_name = str(provider).strip()
    if not project or not provider_name:
        raise ValueError("project_id and provider are required")
    estimate = max(1, int(estimated_tokens))
    ttl = max(30, int(ttl_seconds))
    current = time.time() if now is None else float(now)
    path = Path(path)

    with exclusive(path):
        data = _load_unlocked(path)
        reaped = _reap(data, current)
        provider_reserved = reserved_tokens(data, provider=provider_name)
        project_reserved = reserved_tokens(data, project_id=project)
        project_consumed = consumed_tokens(data, project_id=project)

        if provider_remaining_tokens is not None:
            remaining = max(0, int(provider_remaining_tokens))
            if provider_reserved + estimate > remaining:
                _save_unlocked(path, data)
                return {
                    "admitted": False,
                    "reason": "provider_capacity_reserved",
                    "provider_reserved_tokens": provider_reserved,
                    "project_reserved_tokens": project_reserved,
                    "project_consumed_tokens": project_consumed,
                    "reaped": reaped,
                }

        if project_envelope_tokens is not None:
            envelope = max(0, int(project_envelope_tokens))
            if project_consumed + project_reserved + estimate > envelope:
                _save_unlocked(path, data)
                return {
                    "admitted": False,
                    "reason": "project_envelope_exhausted",
                    "provider_reserved_tokens": provider_reserved,
                    "project_reserved_tokens": project_reserved,
                    "project_consumed_tokens": project_consumed,
                    "project_envelope_tokens": envelope,
                    "reaped": reaped,
                }

        token = uuid.uuid4().hex
        data["reservations"][token] = {
            "project_id": project,
            "provider": provider_name,
            "reserved_tokens": estimate,
            "created_at": current,
            "expires_at": current + ttl,
        }
        if len(data["reservations"]) > MAX_RESERVATIONS:
            ordered = sorted(
                data["reservations"].items(),
                key=lambda item: float((item[1] or {}).get("created_at", 0.0)),
            )
            for key, _ in ordered[: len(data["reservations"]) - MAX_RESERVATIONS]:
                data["reservations"].pop(key, None)
        _save_unlocked(path, data)
        return {
            "admitted": True,
            "reason": "reserved",
            "reservation_id": token,
            "reserved_tokens": estimate,
            "provider_reserved_tokens": provider_reserved + estimate,
            "project_reserved_tokens": project_reserved + estimate,
            "project_consumed_tokens": project_consumed,
            "reaped": reaped,
        }


def settle(
    path: Path,
    reservation_id: str,
    *,
    actual_tokens: int,
    now: float | None = None,
) -> dict:
    path = Path(path)
    current = time.time() if now is None else float(now)
    actual = max(0, int(actual_tokens))
    with exclusive(path):
        data = _load_unlocked(path)
        _reap(data, current)
        row = data["reservations"].pop(str(reservation_id), None)
        if not isinstance(row, dict):
            _save_unlocked(path, data)
            return {"settled": False, "reason": "reservation_missing"}
        project = str(row["project_id"])
        provider = str(row["provider"])
        key = project + "::" + provider
        data["consumed"][key] = max(0, int(data["consumed"].get(key, 0) or 0)) + actual
        _save_unlocked(path, data)
        return {
            "settled": True,
            "project_id": project,
            "provider": provider,
            "reserved_tokens": max(0, int(row.get("reserved_tokens", 0) or 0)),
            "actual_tokens": actual,
            "released_tokens": max(0, int(row.get("reserved_tokens", 0) or 0) - actual),
        }


def release(path: Path, reservation_id: str, *, now: float | None = None) -> dict:
    path = Path(path)
    current = time.time() if now is None else float(now)
    with exclusive(path):
        data = _load_unlocked(path)
        _reap(data, current)
        row = data["reservations"].pop(str(reservation_id), None)
        _save_unlocked(path, data)
        if not isinstance(row, dict):
            return {"released": False, "reason": "reservation_missing"}
        return {
            "released": True,
            "project_id": row.get("project_id"),
            "provider": row.get("provider"),
            "released_tokens": max(0, int(row.get("reserved_tokens", 0) or 0)),
        }



def reservations_by_provider(data: dict) -> dict[str, int]:
    result = {}
    for row in (data.get("reservations") or {}).values():
        if not isinstance(row, dict):
            continue
        provider = str(row.get("provider") or "").strip()
        if not provider:
            continue
        result[provider] = result.get(provider, 0) + max(
            0, int(row.get("reserved_tokens", 0) or 0)
        )
    return result


def usage_by_project(data: dict) -> dict[str, dict]:
    projects = {}
    for row in (data.get("reservations") or {}).values():
        if not isinstance(row, dict):
            continue
        project = str(row.get("project_id") or "").strip()
        if not project:
            continue
        item = projects.setdefault(project, {"reserved_tokens": 0, "consumed_tokens": 0})
        item["reserved_tokens"] += max(0, int(row.get("reserved_tokens", 0) or 0))
    for key, value in (data.get("consumed") or {}).items():
        if not isinstance(key, str) or "::" not in key:
            continue
        project, _provider = key.split("::", 1)
        if not project:
            continue
        item = projects.setdefault(project, {"reserved_tokens": 0, "consumed_tokens": 0})
        item["consumed_tokens"] += max(0, int(value or 0))
    for project, item in projects.items():
        item["committed_tokens"] = item["reserved_tokens"] + item["consumed_tokens"]
    return projects


def detailed_snapshot(path: Path, *, now: float | None = None) -> dict:
    current = time.time() if now is None else float(now)
    path = Path(path)
    with exclusive(path):
        data = _load_unlocked(path)
        reaped = _reap(data, current)
        _save_unlocked(path, data)
    return {
        "active_reservations": len(data["reservations"]),
        "reserved_tokens": reserved_tokens(data),
        "consumed_tokens": consumed_tokens(data),
        "reservations_by_provider": reservations_by_provider(data),
        "usage_by_project": usage_by_project(data),
        "reaped": reaped,
    }

def snapshot(path: Path, *, now: float | None = None) -> dict:
    current = time.time() if now is None else float(now)
    path = Path(path)
    with exclusive(path):
        data = _load_unlocked(path)
        reaped = _reap(data, current)
        _save_unlocked(path, data)
    return {
        "active_reservations": len(data["reservations"]),
        "reserved_tokens": reserved_tokens(data),
        "consumed_tokens": consumed_tokens(data),
        "reaped": reaped,
    }
