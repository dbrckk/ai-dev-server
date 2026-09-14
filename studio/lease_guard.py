"""Background lease renewal for long-running task operations."""
from __future__ import annotations

from contextlib import contextmanager
import threading

from task_lease import DEFAULT_LEASE_SECONDS, heartbeat


@contextmanager
def maintain(task: dict | None, *, lease_seconds: int = DEFAULT_LEASE_SECONDS, interval_seconds: float | None = None):
    if not isinstance(task, dict):
        yield
        return
    owner = task.get("lease_owner")
    token = task.get("lease_token")
    if not isinstance(owner, str) or not owner or not isinstance(token, str) or not token:
        yield
        return

    interval = float(interval_seconds if interval_seconds is not None else max(5.0, lease_seconds / 3.0))
    stop = threading.Event()
    errors: list[BaseException] = []

    def run():
        while not stop.wait(interval):
            try:
                heartbeat(task, owner=owner, token=token, lease_seconds=lease_seconds)
            except BaseException as exc:
                errors.append(exc)
                stop.set()
                return

    thread = threading.Thread(target=run, name="studio-task-lease-heartbeat", daemon=True)
    thread.start()
    try:
        yield
        if errors:
            raise RuntimeError("task lease heartbeat failed") from errors[0]
    finally:
        stop.set()
        thread.join(timeout=max(1.0, min(interval, 5.0)))
