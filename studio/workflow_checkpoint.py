"""Crash-resumable idempotency checkpoints for expensive workflow operations."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from atomic_file import write_text as atomic_write_text
from core import canonical
from file_lock import exclusive

SCHEMA = 1
MAX_ENTRIES = 256
MAX_BYTES = 4 * 1024 * 1024


def _path() -> Path | None:
    raw = os.environ.get("STUDIO_CHECKPOINT_PATH", "").strip()
    return Path(raw) if raw else None


def operation_key(kind: str, payload: dict) -> str:
    raw = canonical({
        "schema": SCHEMA,
        "kind": str(kind),
        "payload": payload,
    }).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _load_path(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}
    if not isinstance(data, dict) or data.get("schema") != SCHEMA:
        return {}
    entries = data.get("entries")
    return dict(entries) if isinstance(entries, dict) else {}


def load() -> dict:
    path = _path()
    return {} if path is None else _load_path(path)


def get(key: str) -> dict | None:
    row = load().get(key)
    if not isinstance(row, dict) or row.get("status") != "completed":
        return None
    value = row.get("value")
    return value if isinstance(value, dict) else None


def put(key: str, value: dict, *, kind: str) -> None:
    path = _path()
    if path is None:
        return
    if not isinstance(key, str) or len(key) != 64 or not isinstance(value, dict):
        raise ValueError("workflow checkpoint invalid")
    with exclusive(path):
        entries = _load_path(path)
        if key in entries:
            entries.pop(key)
        entries[key] = {
            "status": "completed",
            "kind": str(kind),
            "value": value,
        }
        entries = dict(list(entries.items())[-MAX_ENTRIES:])
        payload = {"schema": SCHEMA, "entries": entries}
        raw = canonical(payload)
        if len(raw.encode("utf-8")) > MAX_BYTES:
            while entries and len(canonical({"schema": SCHEMA, "entries": entries}).encode("utf-8")) > MAX_BYTES:
                entries.pop(next(iter(entries)))
            payload = {"schema": SCHEMA, "entries": entries}
        atomic_write_text(path, canonical(payload), encoding="utf-8")


def discard(key: str) -> None:
    path = _path()
    if path is None:
        return
    with exclusive(path):
        entries = _load_path(path)
        if key not in entries:
            return
        entries.pop(key, None)
        atomic_write_text(
            path,
            canonical({"schema": SCHEMA, "entries": entries}),
            encoding="utf-8",
        )
