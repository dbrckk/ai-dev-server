"""Strict cache for successful full candidate validation only."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from atomic_file import write_text as atomic_write_text
from core import IMAGE, canonical
from flutter_workspace import snapshot as flutter_snapshot
from file_lock import exclusive

SCHEMA = 1
MAX_ENTRIES = 128

FULL_GATE_CONTRACT = [
    ["flutter", "pub", "get"],
    ["flutter", "analyze", "--no-pub"],
    ["flutter", "test", "--no-pub", "--exclude-tags=studio-visual"],
    ["flutter", "test", "--no-pub", "--update-goldens", "test/__studio_visual_test.dart"],
    ["flutter", "build", "apk", "--debug", "--no-pub"],
]


def _path() -> Path | None:
    raw = os.environ.get("STUDIO_FULL_GATE_CACHE_PATH", "")
    return Path(raw) if raw else None


def _hash_json(value) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def _native_fingerprint(root: Path) -> str:
    rows = []
    for folder in ("android", "ios"):
        base = root / folder
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.is_symlink() or path.name == "local.properties":
                continue
            rel = path.relative_to(root).as_posix()
            rows.append({
                "path": rel,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            })
    return _hash_json(rows)


def validation_key(root: Path, *, app_name: str, journeys: list[dict]) -> str:
    root = root.resolve()
    template = Path(__file__).with_name("visual_test.dart")
    template_hash = (
        hashlib.sha256(template.read_bytes()).hexdigest()
        if template.is_file()
        else "missing"
    )
    payload = {
        "schema": SCHEMA,
        "flutter_image": IMAGE,
        "full_gate_contract": FULL_GATE_CONTRACT,
        "app_name": app_name,
        "journeys": journeys,
        "editable_workspace": flutter_snapshot(root),
        "native_fingerprint": _native_fingerprint(root),
        "visual_probe_sha256": template_hash,
    }
    return _hash_json(payload)


def load() -> dict:
    path = _path()
    if path is None or not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}
    if not isinstance(data, dict) or data.get("schema") != SCHEMA:
        return {}
    if data.get("flutter_image") != IMAGE:
        return {}
    entries = data.get("entries")
    if not isinstance(entries, dict):
        return {}
    return {
        key: row
        for key, row in entries.items()
        if isinstance(key, str)
        and len(key) == 64
        and isinstance(row, dict)
        and row.get("passed") is True
    }


def save(entries: dict) -> None:
    path = _path()
    if path is None:
        return
    with exclusive(path):
        merged = load()
        merged.update(entries)
        clean = [
            (key, {"passed": True})
            for key, row in merged.items()
            if isinstance(key, str)
            and len(key) == 64
            and isinstance(row, dict)
            and row.get("passed") is True
        ][-MAX_ENTRIES:]
        clean_entries = dict(clean)
        entries.clear()
        entries.update(clean_entries)
        payload = {
            "schema": SCHEMA,
            "flutter_image": IMAGE,
            "entries": clean_entries,
        }
        atomic_write_text(path, canonical(payload), encoding="utf-8")


def hit(entries: dict, key: str) -> bool:
    row = entries.get(key)
    return isinstance(row, dict) and row.get("passed") is True


def record_success(entries: dict, key: str) -> None:
    entries[key] = {"passed": True}
