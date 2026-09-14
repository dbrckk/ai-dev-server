"""Crash-safe atomic persistence for small local state files."""
from __future__ import annotations

import os
from pathlib import Path
import tempfile


def write_bytes(path: Path, data: bytes) -> None:
    """Atomically replace *path* with *data* using a same-directory temp file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, raw_tmp = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    tmp = Path(raw_tmp)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
        # Persist the directory entry where supported. Some filesystems/platforms
        # reject directory fsync; the file replacement itself has already
        # completed safely in that case.
        try:
            dir_fd = os.open(path.parent, os.O_RDONLY)
        except OSError:
            return
        try:
            os.fsync(dir_fd)
        except OSError:
            pass
        finally:
            os.close(dir_fd)
    finally:
        tmp.unlink(missing_ok=True)


def write_text(path: Path, text: str, *, encoding: str = "utf-8") -> None:
    write_bytes(path, text.encode(encoding))
