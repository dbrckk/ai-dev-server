"""Small inter-process advisory lock for local state files."""
from __future__ import annotations

from contextlib import contextmanager
import os
from pathlib import Path
import time

try:
    import fcntl
except ImportError:  # pragma: no cover - studio runners are Linux
    fcntl = None


@contextmanager
def exclusive(path: Path, *, timeout_seconds: float = 10.0, poll_seconds: float = 0.05):
    """Serialize writers using a sibling .lock file."""
    if fcntl is None:
        raise RuntimeError("inter-process file locking unavailable")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_name(path.name + ".lock")
    fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
    deadline = time.monotonic() + max(0.0, float(timeout_seconds))
    acquired = False
    try:
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                acquired = True
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise TimeoutError("state file lock timed out")
                time.sleep(max(0.001, float(poll_seconds)))
        yield
    finally:
        if acquired:
            fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)
