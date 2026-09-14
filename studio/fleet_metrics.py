"""Persist bounded fleet health snapshots for trend analysis."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from atomic_file import write_text as atomic_write_text
from file_lock import exclusive
from fleet_dashboard import collect

MAX_SNAPSHOTS = 512


def load(path: Path) -> list[dict]:
    path = Path(path)
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return []
    if not isinstance(data, dict) or data.get("schema") != 1:
        return []
    rows = data.get("snapshots")
    return list(rows) if isinstance(rows, list) else []


def snapshot(root: Path | str = "studio-output", *, ts: float | None = None) -> dict:
    report = collect(root)
    summary = dict(report["summary"])
    summary["ts"] = round(time.time() if ts is None else float(ts), 3)
    summary["active_leases"] = sum(
        int(project.get("active_leases") or 0)
        for project in report["projects"]
        if isinstance(project.get("active_leases"), int)
    )
    summary["checkpoint_entries"] = sum(
        int(project.get("checkpoint_entries") or 0)
        for project in report["projects"]
    )
    summary["telemetry_events"] = sum(
        int(project.get("telemetry_events") or 0)
        for project in report["projects"]
    )
    return summary


def append(path: Path, row: dict) -> dict:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with exclusive(path):
        rows = load(path)
        rows.append(dict(row))
        rows = rows[-MAX_SNAPSHOTS:]
        atomic_write_text(
            path,
            json.dumps({"schema": 1, "snapshots": rows}, sort_keys=True),
            encoding="utf-8",
        )
    return {"snapshots": len(rows), "latest": rows[-1]}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Record AI Dev Server fleet metrics")
    parser.add_argument("--root", default="studio-output")
    parser.add_argument("--history", default="studio-output/fleet-metrics.json")
    args = parser.parse_args(argv)
    result = append(Path(args.history), snapshot(args.root))
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
