"""Minimal durable operational telemetry for autonomous runs."""
from __future__ import annotations

import json
import os
from pathlib import Path
import time

try:
    from .core import canonical
    from .file_lock import exclusive
except ImportError:
    from core import canonical
    from file_lock import exclusive

MAX_EVENT_BYTES = 64 * 1024


def _path() -> Path | None:
    raw = os.environ.get("STUDIO_TELEMETRY_PATH", "").strip()
    return Path(raw) if raw else None


def emit(kind: str, **fields) -> None:
    path = _path()
    if path is None:
        return
    event = {
        "ts": round(time.time(), 3),
        "kind": str(kind),
        **fields,
    }
    raw = canonical(event).encode("utf-8")
    if len(raw) > MAX_EVENT_BYTES:
        raise ValueError("telemetry event too large")
    path.parent.mkdir(parents=True, exist_ok=True)
    with exclusive(path):
        with path.open("ab") as handle:
            handle.write(raw + b"\n")
            handle.flush()
            os.fsync(handle.fileno())


def summarize(path: Path) -> dict:
    path = Path(path)
    if not path.is_file():
        return {"events": 0, "kinds": {}, "last_ts": None}
    kinds = {}
    count = 0
    last_ts = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        count += 1
        kind = str(event.get("kind", "unknown"))
        kinds[kind] = kinds.get(kind, 0) + 1
        ts = event.get("ts")
        if isinstance(ts, (int, float)):
            last_ts = ts
    return {"events": count, "kinds": kinds, "last_ts": last_ts}
