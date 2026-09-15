"""Progress-gated heartbeat helper for claimed worker capacity."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from capacity_ledger import heartbeat


def progress_marker(project_out: Path | str) -> str:
    root = Path(project_out)
    candidates = [
        root / ".autonomy" / "execution-checkpoint.json",
        root / "generic-report.json",
        root / "project-report.json",
    ]
    digest = hashlib.sha256()
    seen = 0
    for path in candidates:
        if not path.is_file():
            continue
        try:
            payload = path.read_bytes()
        except OSError:
            continue
        digest.update(path.name.encode("utf-8"))
        digest.update(payload)
        seen += 1
    if not seen:
        return "initial"
    return digest.hexdigest()


def renew_if_progressed(
    ledger_path: Path | str,
    reservation_id: str,
    project_out: Path | str,
    *,
    now: float | None = None,
    ttl_seconds: int = 900,
) -> dict:
    return heartbeat(
        Path(ledger_path),
        reservation_id,
        progress_marker=progress_marker(project_out),
        now=now,
        ttl_seconds=ttl_seconds,
    )
