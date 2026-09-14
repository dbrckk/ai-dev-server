"""Operational V1 gate combining host readiness and optional project runtime health."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from readiness import check as readiness_check
from runtime_health import inspect as runtime_health


def evaluate(root: Path | str = ".", project_out: Path | str | None = None) -> dict:
    readiness = readiness_check(root=root, project_out=project_out)
    runtime = runtime_health(project_out) if project_out is not None else None

    failures = []
    if not readiness["ready"]:
        failures.extend("readiness:" + item for item in readiness["failed"])
    if runtime is not None and runtime["status"] != "healthy":
        failures.extend("runtime:" + item for item in runtime["errors"])

    if failures:
        verdict = "blocked"
    elif runtime is None:
        verdict = "ready"
    else:
        verdict = "operational"

    return {
        "verdict": verdict,
        "ready": verdict in {"ready", "operational"},
        "readiness": readiness,
        "runtime": runtime,
        "failures": failures,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="AI Dev Server V1 operational gate")
    parser.add_argument("--root", default=".")
    parser.add_argument("--project-out")
    args = parser.parse_args(argv)
    report = evaluate(args.root, args.project_out)
    print(json.dumps(report, sort_keys=True))
    return 0 if report["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
