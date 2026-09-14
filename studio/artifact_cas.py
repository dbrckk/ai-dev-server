"""Local content-addressable store with strict project isolation."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path

from artifact_cas_namespace import project_namespace, scoped_digest
from artifact_share_policy import validate_shareable_class
from artifact_cas_stats import forget as forget_stats, record as record_stats
from core import StudioError

MAX_CAS_BYTES = 64 * 1024 * 1024


def _root() -> Path | None:
    raw = os.environ.get("STUDIO_ARTIFACT_CAS_PATH", "")
    return Path(raw) if raw else None


def _project_id() -> str:
    raw = os.environ.get("STUDIO_PROJECT_ID", "")
    return raw if raw else "local-project"


def _scope_root(*, shareable: bool = False, artifact_class: str | None = None) -> Path:
    root = _root()
    if root is None:
        raise StudioError("Artifact CAS path unavailable")
    if shareable:
        shared_raw = os.environ.get("STUDIO_SHARED_ARTIFACT_CAS_PATH", "")
        shared_root = Path(shared_raw) if shared_raw else root / "shared"
        return shared_root / validate_shareable_class(artifact_class)
    return root / "private" / project_namespace(_project_id())


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def stats_digest(digest: str, *, shareable: bool = False, artifact_class: str | None = None) -> str:
    if shareable:
        artifact_class = validate_shareable_class(artifact_class)
        return hashlib.sha256(("shared\0" + artifact_class + "\0" + digest).encode("utf-8")).hexdigest()
    return scoped_digest(_project_id(), digest)


def blob_path(digest: str, *, shareable: bool = False, artifact_class: str | None = None) -> Path:
    if (
        not isinstance(digest, str)
        or len(digest) != 64
        or any(ch not in "0123456789abcdef" for ch in digest)
    ):
        raise StudioError("Artifact CAS digest invalid")
    root = _scope_root(shareable=shareable, artifact_class=artifact_class)
    return root / digest[:2] / digest[2:]


def put(
    data: bytes,
    *,
    rebuild_cost_seconds: float | None = None,
    shareable: bool = False,
    artifact_class: str | None = None,
) -> dict:
    if not isinstance(data, (bytes, bytearray)):
        raise StudioError("Artifact CAS payload invalid")
    data = bytes(data)
    digest = sha256(data)
    path = blob_path(digest, shareable=shareable, artifact_class=artifact_class)
    if path.is_file():
        existing = path.read_bytes()
        if sha256(existing) != digest:
            raise StudioError("Artifact CAS existing blob corrupted")
        record_stats(
            stats_digest(digest, shareable=shareable, artifact_class=artifact_class),
            size=len(data),
            hit=False,
            rebuild_cost_seconds=rebuild_cost_seconds,
        )
        return {"sha256": digest, "size": len(data)}
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_bytes(data)
    if sha256(tmp.read_bytes()) != digest:
        tmp.unlink(missing_ok=True)
        raise StudioError("Artifact CAS write verification failed")
    os.replace(tmp, path)
    if usage(shareable=shareable, artifact_class=artifact_class) > MAX_CAS_BYTES:
        path.unlink(missing_ok=True)
        try:
            path.parent.rmdir()
        except OSError:
            pass
        raise StudioError("Artifact CAS quota exceeded")
    record_stats(
        stats_digest(digest, shareable=shareable, artifact_class=artifact_class),
        size=len(data),
        hit=False,
        rebuild_cost_seconds=rebuild_cost_seconds,
    )
    return {"sha256": digest, "size": len(data)}


def get(digest: str, expected_size: int, *, shareable: bool = False, artifact_class: str | None = None) -> bytes:
    path = blob_path(digest, shareable=shareable, artifact_class=artifact_class)
    if not path.is_file() or path.is_symlink():
        raise StudioError("Artifact CAS blob missing")
    data = path.read_bytes()
    if len(data) != expected_size or sha256(data) != digest:
        raise StudioError("Artifact CAS blob verification failed")
    record_stats(stats_digest(digest, shareable=shareable, artifact_class=artifact_class), size=len(data), hit=True)
    return data


def usage(*, shareable: bool = False, artifact_class: str | None = None) -> int:
    root = _scope_root(shareable=shareable, artifact_class=artifact_class)
    if not root.is_dir():
        return 0
    total = 0
    for path in root.rglob("*"):
        if path.is_file() and not path.is_symlink() and not path.name.endswith(".tmp"):
            total += path.stat().st_size
    return total


def gc(referenced: set[str], *, shareable: bool = False, artifact_class: str | None = None) -> dict:
    root = _scope_root(shareable=shareable, artifact_class=artifact_class)
    if not root.is_dir():
        return {"removed": 0, "bytes_removed": 0, "bytes_after": 0}
    removed = 0
    bytes_removed = 0
    removed_digests = set()
    for path in sorted(root.rglob("*"), reverse=True):
        if path.is_file() and not path.is_symlink():
            rel = path.relative_to(root)
            digest = rel.parts[0] + "".join(rel.parts[1:])
            if path.name.endswith(".tmp") or digest not in referenced:
                size = path.stat().st_size
                path.unlink(missing_ok=True)
                removed += 1
                bytes_removed += size
                if len(digest) == 64:
                    removed_digests.add(stats_digest(digest, shareable=shareable, artifact_class=artifact_class))
        elif path.is_dir():
            try:
                path.rmdir()
            except OSError:
                pass
    after = usage(shareable=shareable, artifact_class=artifact_class)
    if after > MAX_CAS_BYTES:
        raise StudioError("Artifact CAS exceeds quota after GC")
    forget_stats(removed_digests)
    return {"removed": removed, "bytes_removed": bytes_removed, "bytes_after": after}
