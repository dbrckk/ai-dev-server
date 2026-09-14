"""Aggregate health and activity for all autonomous project outputs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from runtime_health import inspect
from architecture_learning import summarize as summarize_architecture_learning


def collect(root: Path | str = "studio-output") -> dict:
    root = Path(root)
    projects = []
    if root.is_dir():
        for path in sorted(root.iterdir()):
            if not path.is_dir() or not (path / ".autonomy").exists():
                continue
            report = inspect(path)
            projects.append({
                "id": path.name,
                "status": report.get("status"),
                "runtime_status": report.get("runtime_status"),
                "attempt": report.get("attempt"),
                "checkpoint_entries": report.get("checkpoint_entries", 0),
                "active_leases": (report.get("leases") or {}).get("claims"),
                "telemetry_events": (report.get("telemetry") or {}).get("events", 0),
                "errors": report.get("errors", []),
            })
    architecture = summarize_architecture_learning(root)
    eligible = [
        row for row in architecture.get("rankings", [])
        if isinstance(row, dict) and row.get("eligible_for_advisory_bias") is True
    ]
    healthy = sum(1 for item in projects if item["status"] == "healthy")
    degraded = len(projects) - healthy
    running = sum(1 for item in projects if item.get("runtime_status") == "running")
    complete = sum(1 for item in projects if item.get("runtime_status") == "complete")
    blocked = sum(1 for item in projects if item.get("runtime_status") in {"blocked", "human_action_required"})
    return {
        "projects": projects,
        "architecture_learning": {
            "projects_observed": architecture.get("projects_observed", 0),
            "eligible_recommendations": len(eligible),
            "top_recommendations": eligible[:5],
        },
        "summary": {
            "total": len(projects),
            "healthy": healthy,
            "degraded": degraded,
            "running": running,
            "complete": complete,
            "blocked": blocked,
        },
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="AI Dev Server fleet dashboard")
    parser.add_argument("--root", default="studio-output")
    args = parser.parse_args(argv)
    report = collect(args.root)
    print(json.dumps(report, sort_keys=True))
    return 0 if report["summary"]["degraded"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
