"""Bounded, credential-free audit log for provider routing decisions."""
from __future__ import annotations

import json
import os
import tempfile
import time
from pathlib import Path

MAX_EVENTS = 512


def append(path: Path, event: dict, *, now: float | None = None) -> dict:
    path = Path(path)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        value = {"schema": 1, "events": []}
    if not isinstance(value, dict) or not isinstance(value.get("events"), list):
        value = {"schema": 1, "events": []}
    clean = {
        "ts": time.time() if now is None else float(now),
        "role": str(event.get("role") or ""),
        "screenshots": bool(event.get("screenshots")),
        "winner": event.get("winner"),
        "winner_model": event.get("winner_model"),
        "candidates": event.get("candidates") if isinstance(event.get("candidates"), list) else [],
        "rejected": event.get("rejected") if isinstance(event.get("rejected"), list) else [],
    }
    value["events"].append(clean)
    value["events"] = value["events"][-MAX_EVENTS:]
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, sort_keys=True, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass
    return clean
