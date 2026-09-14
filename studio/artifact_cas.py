"""Local content-addressable store for immutable candidate artifacts."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path

from core import StudioError

MAX_CAS_BYTES = 64 * 1024 * 1024


def _root() -> Path | None:
    raw = os.environ.get("STUDIO_ARTIFACT_CAS_PATH", "")
    return Path(raw) if raw else None


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def blob_path(digest: str) -> Path:
    root = _root()
    if root is None:
        raise StudioError("Artifact CAS path unavailable")
    if not isinstance(digest, str) or len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
        raise StudioError("Artifact CAS digest invalid")
    return root / digest[:2] / digest[2:]


def put(data: bytes) -> dict:
    if not isinstance(data, (bytes, bytearray)):
        raise StudioError("Artifact CAS payload invalid")
    data = bytes(data)
    digest = sha256(data)
    path = blob_path(digest)
    if path.is_file():
        existing = path.read_bytes()
        if sha256(existing) != digest:
            raise StudioError("Artifact CAS existing blob corrupted")
        return {"sha256": digest, "size": len(data)}
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_bytes(data)
    if sha256(tmp.read_bytes()) != digest:
        tmp.unlink(missing_ok=True)
        raise StudioError("Artifact CAS write verification failed")
    os.replace(tmp, path)
    return {"sha256": digest, "size": len(data)}


def get(digest: str, expected_size: int) -> bytes:
    path = blob_path(digest)
    if not path.is_file() or path.is_symlink():
        raise StudioError("Artifact CAS blob missing")
    data = path.read_bytes()
    if len(data) != expected_size or sha256(data) != digest:
        raise StudioError("Artifact CAS blob verification failed")
    return data


def usage() -> int:
    root = _root()
    if root is None or not root.is_dir():
        return 0
    total = 0
    for path in root.rglob("*"):
        if path.is_file() and not path.is_symlink() and not path.name.endswith(".tmp"):
            total += path.stat().st_size
    return total


def gc(referenced: set[str]) -> dict:
    root = _root()
    if root is None or not root.is_dir():
        return {"removed": 0, "bytes_removed": 0, "bytes_after": 0}
    removed = 0
    bytes_removed = 0
    for path in sorted(root.rglob("*"), reverse=True):
        if path.is_file() and not path.is_symlink():
            rel = path.relative_to(root)
            digest = rel.parts[0] + "".join(rel.parts[1:])
            if path.name.endswith(".tmp") or digest not in referenced:
                size = path.stat().st_size
                path.unlink(missing_ok=True)
                removed += 1
                bytes_removed += size
        elif path.is_dir():
            try:
                path.rmdir()
            except OSError:
                pass
    after = usage()
    if after > MAX_CAS_BYTES:
        raise StudioError("Artifact CAS exceeds quota after GC")
    return {"removed": removed, "bytes_removed": bytes_removed, "bytes_after": after}
