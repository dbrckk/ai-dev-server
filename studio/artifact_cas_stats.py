"""Usage statistics and retention scoring for artifact CAS blobs."""
from __future__ import annotations

import json
import os
from pathlib import Path


SCHEMA = 1


def _path() -> Path | None:
    raw = os.environ.get("STUDIO_ARTIFACT_CAS_STATS_PATH", "")
    return Path(raw) if raw else None


def load() -> dict:
    path = _path()
    if path is None or not path.is_file():
        return {"schema": SCHEMA, "clock": 0, "blobs": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {"schema": SCHEMA, "clock": 0, "blobs": {}}
    if (
        not isinstance(data, dict)
        or data.get("schema") != SCHEMA
        or type(data.get("clock")) is not int
        or not isinstance(data.get("blobs"), dict)
    ):
        return {"schema": SCHEMA, "clock": 0, "blobs": {}}
    return data


def save(data: dict) -> None:
    path = _path()
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, sort_keys=True), encoding="utf-8")


def record(
    digest: str,
    *,
    size: int,
    hit: bool,
    rebuild_cost_seconds: float | None = None,
) -> dict:
    data = load()
    data["clock"] = int(data.get("clock", 0)) + 1
    blobs = data.setdefault("blobs", {})
    row = blobs.setdefault(digest, {
        "hits": 0,
        "last_used": 0,
        "size": int(size),
        "rebuild_cost_seconds": 0.0,
    })
    row["size"] = int(size)
    row["last_used"] = data["clock"]
    if hit:
        row["hits"] = int(row.get("hits", 0)) + 1
    if rebuild_cost_seconds is not None:
        row["rebuild_cost_seconds"] = max(
            float(row.get("rebuild_cost_seconds", 0.0)),
            max(0.0, float(rebuild_cost_seconds)),
        )
    save(data)
    return row


def retention_score(digest: str) -> float:
    data = load()
    row = data.get("blobs", {}).get(digest)
    if not isinstance(row, dict):
        return 0.0
    hits = max(0, int(row.get("hits", 0)))
    cost = max(0.0, float(row.get("rebuild_cost_seconds", 0.0)))
    size = max(1, int(row.get("size", 1)))
    clock = max(1, int(data.get("clock", 1)))
    last_used = max(0, int(row.get("last_used", 0)))
    recency = max(0.0, 1.0 - ((clock - last_used) / max(1.0, float(clock))))
    value = (hits * 12.0) + (cost * 2.0) + (recency * 8.0)
    return value / max(1.0, size / (1024.0 * 1024.0))


def forget(digests: set[str]) -> None:
    if not digests:
        return
    data = load()
    blobs = data.get("blobs", {})
    for digest in digests:
        blobs.pop(digest, None)
    save(data)
