"""Detect fleet health regressions between the two latest snapshots."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from fleet_metrics import load


def compare(previous: dict, current: dict) -> dict:
    regressions = []
    if int(current.get("degraded", 0)) > int(previous.get("degraded", 0)):
        regressions.append("degraded_projects_increased")
    if int(current.get("blocked", 0)) > int(previous.get("blocked", 0)):
        regressions.append("blocked_projects_increased")
    if int(current.get("healthy", 0)) < int(previous.get("healthy", 0)):
        regressions.append("healthy_projects_decreased")
    if int(current.get("active_leases", 0)) > int(previous.get("active_leases", 0)) + 2:
        regressions.append("active_leases_spike")
    return {
        "regressed": bool(regressions),
        "regressions": regressions,
        "previous": previous,
        "current": current,
    }


def evaluate(path: Path | str) -> dict:
    rows = load(Path(path))
    if len(rows) < 2:
        return {
            "regressed": False,
            "regressions": [],
            "previous": None,
            "current": rows[-1] if rows else None,
            "insufficient_history": True,
        }
    result = compare(rows[-2], rows[-1])
    result["insufficient_history"] = False
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Detect AI Dev Server fleet regressions")
    parser.add_argument("--history", default="studio-output/fleet-metrics.json")
    args = parser.parse_args(argv)
    report = evaluate(args.history)
    print(json.dumps(report, sort_keys=True))
    return 1 if report["regressed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
