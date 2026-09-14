"""Conservative stagnation control for token-burning autonomous projects."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StagnationDecision:
    level: str
    capacity_multiplier: float
    force_diversify: bool
    pause: bool
    reason: str

    def as_dict(self) -> dict:
        return {
            "level": self.level,
            "capacity_multiplier": self.capacity_multiplier,
            "force_diversify": self.force_diversify,
            "pause": self.pause,
            "reason": self.reason,
        }


def decide(project_rows: list[dict]) -> StagnationDecision:
    mature = [
        row for row in project_rows
        if isinstance(row, dict) and int(row.get("samples", 0) or 0) >= 3
    ]
    if not mature:
        return StagnationDecision("normal", 1.0, False, False, "insufficient_evidence")

    max_failure_streak = max(
        max(0, int(row.get("failure_streak", 0) or 0))
        for row in mature
    )
    total_samples = sum(max(0, int(row.get("samples", 0) or 0)) for row in mature)
    recent_success = max(
        max(0.0, min(1.0, float(row.get("ema_success", 0.0) or 0.0)))
        for row in mature
    )

    if max_failure_streak >= 8 and total_samples >= 8 and recent_success <= 0.10:
        return StagnationDecision(
            "pause",
            0.0,
            True,
            True,
            "eight_consecutive_unverified_attempts",
        )
    if max_failure_streak >= 5 and recent_success <= 0.25:
        return StagnationDecision(
            "throttle",
            0.60,
            True,
            False,
            "five_consecutive_unverified_attempts",
        )
    if max_failure_streak >= 3:
        return StagnationDecision(
            "diversify",
            0.90,
            True,
            False,
            "three_consecutive_unverified_attempts",
        )
    return StagnationDecision("normal", 1.0, False, False, "verified_progress_present")


def summarize(efficiency_summary: dict) -> dict:
    rows = efficiency_summary.get("rows") if isinstance(efficiency_summary, dict) else None
    if not isinstance(rows, list):
        rows = []
    grouped = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        project = str(row.get("project_id") or "").strip()
        if project:
            grouped.setdefault(project, []).append(row)
    projects = {
        project: decide(project_rows).as_dict()
        for project, project_rows in grouped.items()
    }
    return {
        "projects": projects,
        "paused_projects": sum(1 for row in projects.values() if row["pause"]),
        "throttled_projects": sum(
            1 for row in projects.values() if row["level"] == "throttle"
        ),
        "diversifying_projects": sum(
            1 for row in projects.values() if row["force_diversify"]
        ),
    }
