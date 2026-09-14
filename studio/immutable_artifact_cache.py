"""Immutable artifact cache bound to a full validation key."""
from __future__ import annotations

import json
import os
from pathlib import Path

from artifact_cas import blob_path as cas_blob_path, gc as cas_gc, get as cas_get, put as cas_put, usage as cas_usage
from artifact_cas_stats import retention_score
from core import StudioError, canonical

SCHEMA = 2
MAX_ENTRIES = 32
MAX_TOTAL_BYTES = 64 * 1024 * 1024
APK_REL = "build/app/outputs/flutter-apk/app-debug.apk"
GOLDEN_DIR = "test/goldens"


def _path() -> Path | None:
    raw = os.environ.get("STUDIO_ARTIFACT_CACHE_PATH", "")
    return Path(raw) if raw else None


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


def capture(root: Path, validation_key: str, *, rebuild_cost_seconds: float = 0.0, entries: dict | None = None) -> dict:
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
    if entries is not None:
        _admit_under_quota(entries, files, rebuild_cost_seconds, validation_key)
    return {
        "validation_key": validation_key,
        "files": {
            rel: cas_put(data, rebuild_cost_seconds=rebuild_cost_seconds)
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
            or set(meta) != {"sha256", "size"}
            or not isinstance(meta["sha256"], str)
            or len(meta["sha256"]) != 64
            or type(meta["size"]) is not int
            or meta["size"] < 0
        ):
            raise StudioError("Artifact cache file metadata invalid")
        if rel != APK_REL and not (rel.startswith(GOLDEN_DIR + "/") and rel.endswith(".png")):
            raise StudioError("Artifact cache path outside approved outputs")
        data = cas_get(meta["sha256"], meta["size"])
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
    apk_sha256 = None
    for rel, data in files.items():
        path = root / rel
        if not path.resolve().is_relative_to(root):
            raise StudioError("Artifact cache path escape")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        meta = entry["files"][rel]
        restored_bytes = path.read_bytes()
        if len(restored_bytes) != meta["size"]:
            raise StudioError("Artifact cache restore verification failed")
        restored.append(rel)
        if rel == APK_REL:
            apk_sha256 = meta["sha256"]
    return {
        "restored": sorted(restored),
        "apk_sha256": apk_sha256,
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


def _referenced_digests(entries: dict) -> set[str]:
    result = set()
    for entry in entries.values():
        if not isinstance(entry, dict):
            continue
        files = entry.get("files")
        if not isinstance(files, dict):
            continue
        for meta in files.values():
            if isinstance(meta, dict):
                digest = meta.get("sha256")
                if isinstance(digest, str) and len(digest) == 64:
                    result.add(digest)
    return result



def touch(entries: dict, validation_key: str) -> None:
    if validation_key in entries:
        value = entries.pop(validation_key)
        entries[validation_key] = value

def _entry_value(entry: dict) -> float:
    files = entry.get("files", {}) if isinstance(entry, dict) else {}
    scores = []
    for meta in files.values():
        if not isinstance(meta, dict):
            continue
        digest = meta.get("sha256")
        if isinstance(digest, str) and len(digest) == 64:
            scores.append(retention_score(digest))
    return sum(scores)


def _trim_by_value(entries: dict) -> dict:
    ranked = []
    order = {key: index for index, key in enumerate(entries)}
    for key, entry in entries.items():
        if not isinstance(entry, dict):
            continue
        ranked.append((
            -_entry_value(entry),
            -order[key],
            key,
            entry,
        ))
    ranked.sort()

    kept = {}
    kept_digests = set()
    used_bytes = 0
    for _, _, key, entry in ranked:
        if len(kept) >= MAX_ENTRIES:
            continue
        files = entry.get("files", {})
        new_bytes = 0
        new_digests = set()
        valid = True
        for meta in files.values():
            if not isinstance(meta, dict):
                valid = False
                break
            digest = meta.get("sha256")
            size = meta.get("size")
            if not isinstance(digest, str) or len(digest) != 64 or type(size) is not int or size < 0:
                valid = False
                break
            if digest not in kept_digests:
                new_digests.add(digest)
                new_bytes += size
        if not valid or used_bytes + new_bytes > MAX_TOTAL_BYTES:
            continue
        kept[key] = entry
        kept_digests.update(new_digests)
        used_bytes += new_bytes
    return kept


def save(entries: dict) -> None:
    path = _path()
    if path is None:
        return
    trimmed = _trim_by_value(entries)
    entries.clear()
    entries.update(trimmed)
    payload = {"schema": SCHEMA, "entries": trimmed}
    raw = canonical(payload).encode("utf-8")
    if len(raw) > 2 * 1024 * 1024:
        raise StudioError("Artifact cache index exceeds storage limit")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    cas_gc(_referenced_digests(trimmed))
