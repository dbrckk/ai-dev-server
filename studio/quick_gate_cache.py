"""Run-local cache for deterministic quick validation results."""
from __future__ import annotations

import hashlib
import json


def delta_hash(files: list[dict]) -> str:
    normalized = []
    for item in files:
        if not isinstance(item, dict):
            continue
        path = item.get("path")
        content = item.get("content")
        if isinstance(path, str) and isinstance(content, str):
            normalized.append({"path": path, "content": content})
    raw = json.dumps(
        sorted(normalized, key=lambda item: item["path"]),
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def cache_key(delta_digest: str, gate: str, targets: list[str] | None = None) -> str:
    raw = json.dumps(
        {
            "delta": delta_digest,
            "gate": gate,
            "targets": sorted(targets or []),
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def get(cache: dict, key: str) -> dict | None:
    value = cache.get(key)
    return dict(value) if isinstance(value, dict) else None


def put(cache: dict, key: str, *, passed: bool, logs: list[dict]) -> None:
    cache[key] = {
        "passed": passed is True,
        "logs": list(logs),
    }
