"""Persistent quick-gate cache scoped by project and toolchain fingerprint."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from atomic_file import write_text as atomic_write_text
from core import IMAGE, canonical

SCHEMA = 1
MAX_ENTRIES = 512


def _path() -> Path | None:
    raw = os.environ.get("STUDIO_QUICK_GATE_CACHE_PATH", "")
    return Path(raw) if raw else None


def toolchain_fingerprint() -> str:
    payload = {
        "schema": SCHEMA,
        "flutter_image": IMAGE,
        "quick_gate_contract": {
            "dependency": ["flutter", "pub", "get"],
            "analyze": ["flutter", "analyze", "--no-pub"],
            "test": ["flutter", "test", "--no-pub", "--exclude-tags=studio-visual"],
        },
    }
    return hashlib.sha256(canonical(payload).encode("utf-8")).hexdigest()


def load() -> dict:
    path = _path()
    if path is None or not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError):
        return {}
    if not isinstance(data, dict):
        return {}
    if data.get("schema") != SCHEMA:
        return {}
    if data.get("toolchain_fingerprint") != toolchain_fingerprint():
        return {}
    entries = data.get("entries")
    return dict(entries) if isinstance(entries, dict) else {}


def save(entries: dict) -> None:
    path = _path()
    if path is None:
        return
    trimmed = list(entries.items())[-MAX_ENTRIES:]
    payload = {
        "schema": SCHEMA,
        "toolchain_fingerprint": toolchain_fingerprint(),
        "entries": dict(trimmed),
    }
    atomic_write_text(path, canonical(payload))
