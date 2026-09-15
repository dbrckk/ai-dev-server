"""Classify expired worker reservations and surface recoverable capacity."""
from __future__ import annotations

import json
from pathlib import Path

from atomic_file import write_text as atomic_write_text
from capacity_ledger import detailed_snapshot, load

REPORT_FILE = "worker-liveness.json"


def _project_status(root: Path, project_id: str) -> str:
    for name in ("generic-report.json", "project-report.json"):
        path = root / project_id / name
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            continue
        if isinstance(value, dict) and isinstance(value.get("status"), str):
            return value["status"]
    return ""


def classify(root: Path | str = "studio-output", *, now: float | None = None) -> dict:
    root = Path(root)
    ledger_path = root / "capacity-ledger.json"
    snap = detailed_snapshot(ledger_path, now=now)
    data = load(ledger_path)
    rows = []
    for event in data.get("reap_events", []):
        if not isinstance(event, dict):
            continue
        project_id = str(event.get("project_id") or "")
        kind = str(event.get("kind") or "")
        status = _project_status(root, project_id)
        if status in {"complete", "published", "verified"}:
            classification = "completed"
        elif kind == "preemption_admission_lease":
            classification = "orphaned"
        elif int(event.get("heartbeat_count", 0) or 0) > 0:
            classification = "stalled"
        else:
            classification = "crashed"
        rows.append({
            **event,
            "project_status": status or None,
            "classification": classification,
            "recoverable_tokens": max(0, int(event.get("reserved_tokens", 0) or 0)),
        })
    report = {
        "schema": 1,
        "summary": {
            "expired": len(rows),
            "completed": sum(1 for row in rows if row["classification"] == "completed"),
            "crashed": sum(1 for row in rows if row["classification"] == "crashed"),
            "stalled": sum(1 for row in rows if row["classification"] == "stalled"),
            "orphaned": sum(1 for row in rows if row["classification"] == "orphaned"),
            "recoverable_tokens": sum(row["recoverable_tokens"] for row in rows),
            "reaped_this_pass": int(snap.get("reaped", 0) or 0),
        },
        "workers": rows[-512:],
    }
    atomic_write_text(
        root / REPORT_FILE,
        json.dumps(report, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return report
