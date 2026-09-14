"""Persistent recovery gate for projects paused by verified stagnation."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from atomic_file import write_text as atomic_write_text
from file_lock import exclusive

SCHEMA = 1
RECOVERY_MULTIPLIER = 0.15


def _empty() -> dict:
    return {"schema": SCHEMA, "projects": {}}


def _load(path: Path) -> dict:
    if not path.is_file():
        return _empty()
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return _empty()
    if not isinstance(value, dict) or value.get("schema") != SCHEMA:
        return _empty()
    return {
        "schema": SCHEMA,
        "projects": value.get("projects") if isinstance(value.get("projects"), dict) else {},
    }


def fingerprint(context: dict) -> str:
    payload = json.dumps(context if isinstance(context, dict) else {}, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]


def evaluate(
    path: Path,
    *,
    project_id: str,
    paused: bool,
    context: dict,
) -> dict:
    project = str(project_id).strip()
    if not project:
        raise ValueError("project_id required")
    current = fingerprint(context)
    path = Path(path)
    with exclusive(path):
        data = _load(path)
        row = data["projects"].get(project, {})
        last_pause = str(row.get("pause_fingerprint") or "")
        last_attempt = str(row.get("last_recovery_fingerprint") or "")

        if not paused:
            data["projects"][project] = {
                "pause_fingerprint": "",
                "last_recovery_fingerprint": "",
            }
            atomic_write_text(path, json.dumps(data, sort_keys=True, indent=2) + "\n", encoding="utf-8")
            return {
                "recover": False,
                "reason": "not_paused",
                "capacity_multiplier": 1.0,
                "force_diversify": False,
                "fingerprint": current,
            }

        if not last_pause:
            data["projects"][project] = {
                "pause_fingerprint": current,
                "last_recovery_fingerprint": "",
            }
            recover = False
            reason = "pause_context_registered"
        elif current != last_pause and current != last_attempt:
            data["projects"][project] = {
                "pause_fingerprint": last_pause,
                "last_recovery_fingerprint": current,
            }
            recover = True
            reason = "material_context_change"
        else:
            recover = False
            reason = "no_new_recovery_signal"

        atomic_write_text(path, json.dumps(data, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        return {
            "recover": recover,
            "reason": reason,
            "capacity_multiplier": RECOVERY_MULTIPLIER if recover else 0.0,
            "force_diversify": recover,
            "fingerprint": current,
        }
