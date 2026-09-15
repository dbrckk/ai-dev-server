"""Long-running bounded operations loop for AI Dev Server fleets."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import time

from fleet_dashboard import collect
from fleet_capacity import persist as persist_capacity_plan
from capacity_ledger import snapshot as capacity_ledger_snapshot
from fleet_maintenance import run as maintain
from fleet_metrics import append as append_metrics, snapshot
from fleet_regression import evaluate as evaluate_regression
from fleet_supervisor_apply import execute as apply_supervisor
from preemption_apply import execute as apply_preemption
from worker_reaper import classify as classify_worker_liveness

MIN_INTERVAL_SECONDS = 30.0


def tick(
    root: Path | str = "studio-output",
    request_dir: Path | str = "control/mobile-requests",
    *,
    apply_restarts: bool = False,
    apply_preemptions: bool = False,
    max_restarts: int = 2,
    history: Path | str | None = None,
) -> dict:
    root = Path(root)
    history = Path(history) if history is not None else root / "fleet-metrics.json"

    dashboard = collect(root)
    metric_row = snapshot(root)
    metrics = append_metrics(history, metric_row)
    regression = evaluate_regression(history)
    maintenance = maintain(root)
    worker_liveness = classify_worker_liveness(root)
    capacity = persist_capacity_plan(root, request_dir)
    preemption = apply_preemption(
        root,
        apply=apply_preemptions and not regression.get("regressed", False),
    )
    if preemption.get("preemptions_executed", 0):
        capacity = persist_capacity_plan(root, request_dir)
    capacity_ledger = capacity_ledger_snapshot(root / "capacity-ledger.json")

    supervisor = apply_supervisor(
        root,
        request_dir,
        apply=apply_restarts and not regression.get("regressed", False),
        max_restarts=max_restarts,
    )

    return {
        "dashboard": dashboard["summary"],
        "metrics": metrics,
        "regression": regression,
        "maintenance": maintenance["summary"],
        "worker_liveness": worker_liveness["summary"],
        "capacity": {
            **capacity["summary"],
            "rebalance": capacity.get("rebalance", {}),
            "ledger": capacity_ledger,
        },
        "preemption": preemption,
        "supervisor": {
            "apply": supervisor["apply"],
            "restarts_executed": supervisor["restarts_executed"],
            "results": supervisor["results"],
        },
    }


def run_loop(
    root: Path | str = "studio-output",
    request_dir: Path | str = "control/mobile-requests",
    *,
    interval_seconds: float = 300.0,
    apply_restarts: bool = False,
    apply_preemptions: bool = False,
    max_restarts: int = 2,
    iterations: int | None = None,
    sleep=time.sleep,
) -> list[dict]:
    interval = max(MIN_INTERVAL_SECONDS, float(interval_seconds))
    rows = []
    count = 0
    while iterations is None or count < max(0, int(iterations)):
        rows.append(
            tick(
                root,
                request_dir,
                apply_restarts=apply_restarts,
                apply_preemptions=apply_preemptions,
                max_restarts=max_restarts,
            )
        )
        count += 1
        if iterations is not None and count >= int(iterations):
            break
        sleep(interval)
    return rows


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="AI Dev Server fleet operations daemon")
    parser.add_argument("--root", default="studio-output")
    parser.add_argument("--request-dir", default="control/mobile-requests")
    parser.add_argument("--interval-seconds", type=float, default=300.0)
    parser.add_argument("--apply-restarts", action="store_true")
    parser.add_argument("--apply-preemptions", action="store_true")
    parser.add_argument("--max-restarts", type=int, default=2)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args(argv)

    if args.once:
        report = tick(
            args.root,
            args.request_dir,
            apply_restarts=args.apply_restarts,
            apply_preemptions=args.apply_preemptions,
            max_restarts=args.max_restarts,
        )
        print(json.dumps(report, sort_keys=True))
        return 1 if report["regression"].get("regressed") else 0

    run_loop(
        args.root,
        args.request_dir,
        interval_seconds=args.interval_seconds,
        apply_restarts=args.apply_restarts,
        apply_preemptions=args.apply_preemptions,
        max_restarts=args.max_restarts,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
