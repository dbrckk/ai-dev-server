"""Calibrate provider/model routing from audited decisions and verified outcomes."""
from __future__ import annotations

import json
from pathlib import Path

from atomic_file import write_text as atomic_write_text


def _load(path: Path) -> dict:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def build(audit: dict, outcomes: list[dict]) -> dict:
    successful = [o for o in outcomes if isinstance(o, dict) and isinstance(o.get("outcome"), dict)]
    events = audit.get("events") if isinstance(audit, dict) else []
    routes = {}
    # Recent ordered attribution: each completed project outcome is matched to its
    # most recent audited winner. This remains conservative when exact call IDs are absent.
    winners = [
        e for e in events if isinstance(e, dict)
        and isinstance(e.get("winner"), str) and isinstance(e.get("winner_model"), str)
    ]
    for event, outcome in zip(reversed(winners), reversed(successful)):
        key = event["winner"] + "::" + event["winner_model"]
        row = routes.setdefault(key, {
            "provider": event["winner"], "model": event["winner_model"],
            "samples": 0, "quality_total": 0.0, "successes": 0,
        })
        observed = outcome["outcome"]
        quality = max(0.0, min(100.0, float(observed.get("quality_score", 0.0) or 0.0)))
        row["samples"] += 1
        row["quality_total"] += quality
        row["successes"] += int(observed.get("successful") is True)
    for row in routes.values():
        n = row["samples"]
        mean_quality = row.pop("quality_total") / max(1, n)
        # Strong neutral prior prevents sparse outcomes from dominating routing.
        posterior_quality = (mean_quality * n + 50.0 * 4.0) / (n + 4.0)
        confidence = min(1.0, n / 12.0)
        row["quality_score"] = round(posterior_quality, 6)
        row["success_rate"] = round((row["successes"] + 2.0) / (n + 4.0), 6)
        row["confidence"] = round(confidence, 6)
        row["routing_adjustment"] = round(
            max(-10.0, min(10.0, (posterior_quality - 50.0) / 5.0 * confidence)),
            6,
        )
    return {"schema": 1, "routes": routes}


def write(audit_path: Path, outcome_paths: list[Path], output_path: Path) -> dict:
    audit = _load(audit_path)
    outcomes = [_load(path) for path in outcome_paths]
    result = build(audit, outcomes)
    atomic_write_text(
        Path(output_path),
        json.dumps(result, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return result


def adjustment(summary: dict, provider: str, model: str) -> float:
    row = (summary.get("routes") or {}).get(str(provider) + "::" + str(model)) if isinstance(summary, dict) else None
    if not isinstance(row, dict):
        return 0.0
    return max(-10.0, min(10.0, float(row.get("routing_adjustment", 0.0) or 0.0)))
