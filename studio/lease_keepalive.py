"""Periodic renewal helper for long-running leased tasks."""
from __future__ import annotations

from contextlib import contextmanager
import threading

from task_lease import heartbeat


@contextmanager
def keepalive(task: dict, *, interval_seconds: float = 120.0, lease_seconds: int = 3600):
    owner = task.get("lease_owner")
    token = task.get("lease_token")
    if not isinstance(owner, str) or not owner or not isinstance(token, str) or not token:
        yield
        return

    stop = threading.Event()
    errors = []

    def renew():
        while not stop.wait(max(1.0, float(interval_seconds))):
            try:
                heartbeat(
                    task,
                    owner=owner,
                    token=token,
                    lease_seconds=lease_seconds,
                )
            except Exception as exc:
                errors.append(exc)
                stop.set()
                return

    worker = threading.Thread(target=renew, name="studio-lease-keepalive", daemon=True)
    worker.start()
    try:
        yield
        if errors:
            raise RuntimeError("task lease keepalive failed") from errors[0]
    finally:
        stop.set()
        worker.join(timeout=5)
