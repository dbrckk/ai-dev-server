"""Deterministic supervisor decisions for autonomous project runtimes."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from fleet_dashboard import collect


RESTARTABLE_RUNTIME = {"running", "deferred", "failed"}
NON_RESTARTABLE_RUNTIME = {"complete", "human_action_required", "blocked"}


def plan(root: Path | str = "studio-output") -> dict:
    dashboard = collect(root)
    actions = []
    for project in dashboard["projects"]:
        runtime = project.get("runtime_status")
        errors = list(project.get("errors") or [])
        if project.get("status") == "healthy":
            action = "none"
            reason = "healthy"
        elif runtime in NON_RESTARTABLE_RUNTIME:
            action = "inspect"
            reason = "terminal_or_human_state"
        elif any(err.startswith("runtime_state:") or err.startswith("leases:") for err in errors):
            action = "quarantine"
            reason = "state_integrity_failure"
        elif runtime in RESTARTABLE_RUNTIME or runtime is None:
            action = "restart"
            reason = "recoverable_degradation"
        else:
            action = "inspect"
            reason = "unknown_state"
        actions.append({
            "id": project["id"],
            "action": action,
            "reason": reason,
            "runtime_status": runtime,
            "errors": errors,
        })
    return {
        "actions": actions,
        "summary": {
            "restart": sum(1 for x in actions if x["action"] == "restart"),
            "quarantine": sum(1 for x in actions if x["action"] == "quarantine"),
            "inspect": sum(1 for x in actions if x["action"] == "inspect"),
            "none": sum(1 for x in actions if x["action"] == "none"),
        },
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="AI Dev Server supervisor plan")
    parser.add_argument("--root", default="studio-output")
    args = parser.parse_args(argv)
    report = plan(args.root)
    print(json.dumps(report, sort_keys=True))
    return 1 if report["summary"]["quarantine"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
