"""Apply bounded supervisor restart decisions to recoverable autonomous projects."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import tempfile
import time

from ci_runner import _run_project_for_queue, bounded_run
from fleet_supervisor import plan
from queue import matrix

DEFAULT_MAX_RESTARTS = 2


def execute(
    root: Path | str = "studio-output",
    request_dir: Path | str = "control/mobile-requests",
    *,
    apply: bool = False,
    max_restarts: int = DEFAULT_MAX_RESTARTS,
    runner=bounded_run,
    clock=time.monotonic,
) -> dict:
    root = Path(root)
    request_dir = Path(request_dir)
    decisions = plan(root)
    projects = {row["id"]: row for row in matrix(request_dir)}
    results = []
    restarted = 0
    deadline = clock() + 70 * 60
    baseline_sha = os.environ.get("GITHUB_SHA") or os.environ.get("CIRCLE_SHA1")

    for decision in decisions["actions"]:
        project_id = decision["id"]
        action = decision["action"]
        row = {
            "id": project_id,
            "planned_action": action,
            "executed": False,
            "status": None,
        }

        if action != "restart":
            row["status"] = "skipped_" + action
            results.append(row)
            continue
        if restarted >= max(0, int(max_restarts)):
            row["status"] = "restart_budget_exhausted"
            results.append(row)
            continue
        project = projects.get(project_id)
        if project is None:
            row["status"] = "request_missing"
            results.append(row)
            continue
        if not apply:
            row["status"] = "dry_run"
            results.append(row)
            continue

        restarted += 1
        with tempfile.TemporaryDirectory(prefix="studio-supervisor-") as work:
            try:
                result = _run_project_for_queue(
                    project,
                    root / project_id,
                    work,
                    runner,
                    deadline,
                    clock,
                    baseline_sha,
                )
                row["executed"] = True
                row["status"] = result.get("status", "unknown")
                row["next_stage"] = result.get("next_stage")
            except Exception as exc:
                row["executed"] = True
                row["status"] = "restart_error"
                row["error"] = type(exc).__name__
        results.append(row)

    return {
        "apply": bool(apply),
        "max_restarts": max(0, int(max_restarts)),
        "restarts_executed": sum(1 for row in results if row["executed"]),
        "results": results,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Apply AI Dev Server supervisor decisions")
    parser.add_argument("--root", default="studio-output")
    parser.add_argument("--request-dir", default="control/mobile-requests")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--max-restarts", type=int, default=DEFAULT_MAX_RESTARTS)
    args = parser.parse_args(argv)
    report = execute(
        args.root,
        args.request_dir,
        apply=args.apply,
        max_restarts=args.max_restarts,
    )
    print(json.dumps(report, sort_keys=True))
    return 1 if any(row["status"] == "restart_error" for row in report["results"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
