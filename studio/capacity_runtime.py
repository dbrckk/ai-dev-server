"""Read per-project capacity envelopes produced by the fleet scheduler."""
from __future__ import annotations

import json
from pathlib import Path


def project_envelope(path: Path | str | None, project_id: str | None) -> int | None:
    if not path or not project_id:
        return None
    target = Path(path)
    if not target.is_file():
        return None
    try:
        value = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    if not isinstance(value, dict):
        return None
    rows = value.get("projects")
    if not isinstance(rows, list):
        return None
    for row in rows:
        if not isinstance(row, dict) or row.get("id") != project_id:
            continue
        raw = row.get("token_envelope")
        if type(raw) is int and raw >= 0:
            return raw
        return None
    return None
