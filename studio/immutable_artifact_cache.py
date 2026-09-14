"""Immutable artifact cache bound to a full validation key."""
from __future__ import annotations

import base64
import hashlib
import json
import os
from pathlib import Path

from core import StudioError, canonical

SCHEMA = 1
MAX_ENTRIES = 32
MAX_TOTAL_BYTES = 64 * 1024 * 1024
APK_REL = "build/app/outputs/flutter-apk/app-debug.apk"
GOLDEN_DIR = "test/goldens"


def _path() -> Path | None:
    raw = os.environ.get("STUDIO_ARTIFACT_CACHE_PATH", "")
    return Path(raw) if raw else None


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_artifacts(root: Path) -> dict[str, bytes]:
    root = root.resolve()
    files: dict[str, bytes] = {}
    apk = root / APK_REL
    if apk.is_file() and not apk.is_symlink():
        files[APK_REL] = apk.read_bytes()
    goldens = root / GOLDEN_DIR
    if goldens.is_dir():
        for path in sorted(goldens.glob("*.png")):
            if path.is_file() and not path.is_symlink():
                files[path.relative_to(root).as_posix()] = path.read_bytes()
    return files


def capture(root: Path, validation_key: str) -> dict:
    if not isinstance(validation_key, str) or len(validation_key) != 64:
        raise StudioError("Artifact cache validation key invalid")
    files = _read_artifacts(root)
    apk = files.get(APK_REL)
    if apk is None or len(apk) <= 1000:
        raise StudioError("Validated artifact cache requires debug APK")
    goldens = [rel for rel in files if rel.startswith(GOLDEN_DIR + "/") and rel.endswith(".png")]
    if not goldens:
        raise StudioError("Validated artifact cache requires goldens")
    total = sum(len(data) for data in files.values())
    if total > MAX_TOTAL_BYTES:
        raise StudioError("Validated artifact set exceeds cache size limit")
    return {
        "validation_key": validation_key,
        "files": {
            rel: {
                "sha256": _sha(data),
                "size": len(data),
                "content_base64": base64.b64encode(data).decode("ascii"),
            }
            for rel, data in files.items()
        },
    }


def verify_entry(entry: dict, validation_key: str) -> dict[str, bytes]:
    if not isinstance(entry, dict) or set(entry) != {"validation_key", "files"}:
        raise StudioError("Artifact cache entry invalid")
    if entry.get("validation_key") != validation_key:
        raise StudioError("Artifact cache validation key mismatch")
    rows = entry.get("files")
    if not isinstance(rows, dict) or not rows:
        raise StudioError("Artifact cache files invalid")
    decoded: dict[str, bytes] = {}
    total = 0
    for rel, meta in rows.items():
        if (
            not isinstance(rel, str)
            or not isinstance(meta, dict)
            or set(meta) != {"sha256", "size", "content_base64"}
            or not isinstance(meta["sha256"], str)
            or len(meta["sha256"]) != 64
            or type(meta["size"]) is not int
            or meta["size"] < 0
            or not isinstance(meta["content_base64"], str)
        ):
            raise StudioError("Artifact cache file metadata invalid")
        if rel != APK_REL and not (rel.startswith(GOLDEN_DIR + "/") and rel.endswith(".png")):
            raise StudioError("Artifact cache path outside approved outputs")
        try:
            data = base64.b64decode(meta["content_base64"], validate=True)
        except ValueError:
            raise StudioError("Artifact cache base64 invalid") from None
        if len(data) != meta["size"] or _sha(data) != meta["sha256"]:
            raise StudioError("Artifact cache digest mismatch")
        total += len(data)
        if total > MAX_TOTAL_BYTES:
            raise StudioError("Artifact cache payload exceeds size limit")
        decoded[rel] = data
    if APK_REL not in decoded or len(decoded[APK_REL]) <= 1000:
        raise StudioError("Artifact cache missing valid debug APK")
    return decoded


def restore(root: Path, entry: dict, validation_key: str) -> dict:
    files = verify_entry(entry, validation_key)
    root = root.resolve()
    restored = []
    for rel, data in files.items():
        path = root / rel
        if not path.resolve().is_relative_to(root):
            raise StudioError("Artifact cache path escape")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        if _sha(path.read_bytes()) != _sha(data):
            raise StudioError("Artifact cache restore verification failed")
        restored.append(rel)
    return {
        "restored": sorted(restored),
        "apk_sha256": _sha(files[APK_REL]),
    }


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
    entries = data.get("entries")
    return dict(entries) if isinstance(entries, dict) else {}


def save(entries: dict) -> None:
    path = _path()
    if path is None:
        return
    items = list(entries.items())[-MAX_ENTRIES:]
    payload = {"schema": SCHEMA, "entries": dict(items)}
    raw = canonical(payload).encode("utf-8")
    if len(raw) > MAX_TOTAL_BYTES * 2:
        raise StudioError("Artifact cache index exceeds storage limit")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
