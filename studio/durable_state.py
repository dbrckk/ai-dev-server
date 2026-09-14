"""Versioned, checksummed, crash-safe JSON state storage."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil

from atomic_file import write_text as atomic_write_text
from core import StudioError, canonical
from file_lock import exclusive

CURRENT_SCHEMA = 2


def _checksum(schema: int, value: dict) -> str:
    raw = canonical({"schema": schema, "value": value}).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _migrate(schema: int, value: dict) -> tuple[int, dict]:
    current = dict(value)
    version = int(schema)
    if version < 1:
        version = 1
    if version == 1:
        current.setdefault("migration_history", [])
        history = list(current["migration_history"])
        history.append({"from": 1, "to": 2})
        current["migration_history"] = history[-16:]
        version = 2
    if version != CURRENT_SCHEMA:
        raise StudioError("Unsupported durable state schema")
    return version, current


def load(path: Path, *, default: dict | None = None) -> dict:
    path = Path(path)
    if not path.is_file():
        return dict(default or {})
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        raise StudioError("Durable state is unreadable") from None
    if not isinstance(payload, dict):
        raise StudioError("Durable state envelope invalid")
    schema = payload.get("schema")
    value = payload.get("value")
    checksum = payload.get("sha256")
    if type(schema) is not int or not isinstance(value, dict) or not isinstance(checksum, str):
        raise StudioError("Durable state envelope invalid")
    if checksum != _checksum(schema, value):
        raise StudioError("Durable state checksum mismatch")
    schema, value = _migrate(schema, value)
    return value


def save(path: Path, value: dict) -> None:
    if not isinstance(value, dict):
        raise StudioError("Durable state value must be an object")
    path = Path(path)
    envelope = {
        "schema": CURRENT_SCHEMA,
        "value": value,
        "sha256": _checksum(CURRENT_SCHEMA, value),
    }
    with exclusive(path):
        if path.is_file():
            try:
                load(path)
            except StudioError:
                pass
            else:
                backup = path.with_name(path.name + ".bak")
                shutil.copyfile(path, backup)
        atomic_write_text(path, canonical(envelope), encoding="utf-8")


def load_recovering(path: Path, *, default: dict | None = None) -> dict:
    path = Path(path)
    try:
        return load(path, default=default)
    except StudioError:
        backup = path.with_name(path.name + ".bak")
        if not backup.is_file():
            raise
        value = load(backup)
        save(path, value)
        return value


def repair_from_backup(path: Path, backup: Path) -> dict:
    value = load(backup)
    save(path, value)
    return value
