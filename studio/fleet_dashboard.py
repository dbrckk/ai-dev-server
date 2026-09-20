"""Aggregate health and activity for all autonomous project outputs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from runtime_health import inspect
from architecture_learning import summarize as summarize_architecture_learning


def _asset_quality(path: Path) -> dict:
    source = path / "asset-forge-prefetch.json"
    if not source.is_file():
        return {
            "status": "not_available",
            "quality_status": "unknown",
            "batch": False,
            "routes": 0,
            "checked": 0,
            "regenerated": 0,
            "minimum_score": None,
        }
    try:
        value = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {
            "status": "unreadable",
            "quality_status": "unknown",
            "batch": False,
            "routes": 0,
            "checked": 0,
            "regenerated": 0,
            "minimum_score": None,
        }
    if not isinstance(value, dict):
        return {
            "status": "invalid",
            "quality_status": "unknown",
            "batch": False,
            "routes": 0,
            "checked": 0,
            "regenerated": 0,
            "minimum_score": None,
        }
    receipts = value.get("receipts")
    if not isinstance(receipts, list):
        one = value.get("receipt")
        receipts = [one] if isinstance(one, dict) else []
    summaries = [
        item.get("quality_summary")
        for item in receipts
        if isinstance(item, dict) and isinstance(item.get("quality_summary"), dict)
    ]
    scores = [
        float(summary["minimum_score"])
        for summary in summaries
        if isinstance(summary.get("minimum_score"), (int, float))
    ]
    return {
        "status": value.get("status"),
        "quality_status": value.get("quality_status") or "unknown",
        "batch": bool(value.get("batch")),
        "routes": len(value.get("routes") or []),
        "checked": sum(int(summary.get("checked") or 0) for summary in summaries),
        "regenerated": sum(int(summary.get("regenerated") or 0) for summary in summaries),
        "minimum_score": min(scores) if scores else None,
        "error_code": next(
            (
                item.get("error_code")
                for item in receipts
                if isinstance(item, dict) and item.get("error_code")
            ),
            None,
        ),
    }


def collect(root: Path | str = "studio-output") -> dict:
    root = Path(root)
    projects = []
    if root.is_dir():
        for path in sorted(root.iterdir()):
            if not path.is_dir() or not (path / ".autonomy").exists():
                continue
            report = inspect(path)
            asset_quality = _asset_quality(path)
            projects.append({
                "id": path.name,
                "status": report.get("status"),
                "runtime_status": report.get("runtime_status"),
                "attempt": report.get("attempt"),
                "checkpoint_entries": report.get("checkpoint_entries", 0),
                "active_leases": (report.get("leases") or {}).get("claims"),
                "telemetry_events": (report.get("telemetry") or {}).get("events", 0),
                "errors": report.get("errors", []),
                "visual_assets": asset_quality,
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
    quality_ok = sum(1 for item in projects if item["visual_assets"]["quality_status"] == "ok")
    quality_regenerated = sum(1 for item in projects if item["visual_assets"]["quality_status"] == "regenerated")
    quality_low = sum(1 for item in projects if item["visual_assets"]["quality_status"] == "low_quality")
    quality_unknown = len(projects) - quality_ok - quality_regenerated - quality_low
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
            "visual_quality_ok": quality_ok,
            "visual_quality_regenerated": quality_regenerated,
            "visual_quality_low": quality_low,
            "visual_quality_unknown": quality_unknown,
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
