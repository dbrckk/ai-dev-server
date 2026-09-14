"""Append-only local audit log for explicit CAS promotions."""
from __future__ import annotations

import json
import os
from pathlib import Path

from artifact_cas_namespace import project_namespace

MAX_RECORDS = 512


def _path() -> Path | None:
    raw = os.environ.get("STUDIO_ARTIFACT_CAS_AUDIT_PATH", "")
    return Path(raw) if raw else None


def load() -> list[dict]:
    path = _path()
    if path is None or not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return []
    if not isinstance(data, list):
        return []
    return [row for row in data if isinstance(row, dict)][-MAX_RECORDS:]


def record(*, project_id: str, artifact_class: str, digest: str, size: int) -> dict:
    rows = load()
    row = {
        "sequence": (int(rows[-1].get("sequence", 0)) + 1) if rows else 1,
        "project_namespace": project_namespace(project_id),
        "artifact_class": artifact_class,
        "sha256": digest,
        "size": int(size),
    }
    rows.append(row)
    rows = rows[-MAX_RECORDS:]
    path = _path()
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(rows, sort_keys=True), encoding="utf-8")
    return row
