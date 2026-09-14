"""Derive advisory obsolescence candidates from runtime drift and benchmark evidence."""
from __future__ import annotations

import json
from pathlib import Path

from atomic_file import write_text as atomic_write_text

MIN_DRIFT_SCORE = 0.6

def _repo_drift(learning: dict) -> dict[str, dict]:
    alerts = learning.get("drift_alerts", []) if isinstance(learning, dict) else []
    out = {}
    for row in alerts:
        if not isinstance(row, dict) or row.get("type") != "repository":
            continue
        repo = row.get("repo")
        score = row.get("score")
        if isinstance(repo, str) and isinstance(score, (int, float)):
            out[repo] = row
    return out

def _recommendation_index(recommendations: dict) -> dict[str, dict]:
    rows = recommendations.get("matches", []) if isinstance(recommendations, dict) else []
    return {
        row["repo"]: row
        for row in rows
        if isinstance(row, dict) and isinstance(row.get("repo"), str)
    }

def evaluate(learning: dict, benchmark: dict, recommendations: dict, maintenance: dict[str, dict] | None = None) -> dict:
    drift = _repo_drift(learning)
    recs = _recommendation_index(recommendations)
    maintenance = maintenance if isinstance(maintenance, dict) else {}
    comparisons = benchmark.get("comparisons", []) if isinstance(benchmark, dict) else []

    candidates = []
    for row in comparisons:
        if not isinstance(row, dict) or not isinstance(row.get("current_repo"), str):
            continue
        current = row["current_repo"]
        drift_row = drift.get(current)
        if not drift_row:
            continue
        drift_score = drift_row.get("score")
        if not isinstance(drift_score, (int, float)) or float(drift_score) < MIN_DRIFT_SCORE:
            continue
        if row.get("migration_candidate") is not True:
            continue
        best = row.get("best_alternative")
        if not isinstance(best, str) or not best:
            continue

        current_meta = recs.get(current, {})
        alt_meta = recs.get(best, {})
        maintenance_row = maintenance.get(current, {})
        maintenance_signal = maintenance_row.get("status") if isinstance(maintenance_row, dict) else None
        if maintenance_signal not in {"active", "aging", "stale", "archived", "unknown"}:
            maintenance_signal = current_meta.get("maintenanceStatus")
        if maintenance_signal not in {"active", "aging", "stale", "archived", "unknown"}:
            maintenance_signal = "unknown"

        candidates.append({
            "repo": current,
            "status": "deprecation_candidate",
            "replacement_candidate": best,
            "drift_score": round(float(drift_score), 4),
            "success_delta": drift_row.get("success_delta"),
            "quality_delta": drift_row.get("quality_delta"),
            "benchmark_delta": next((
                alt.get("delta_vs_current")
                for alt in row.get("alternatives", [])
                if isinstance(alt, dict) and alt.get("repo") == best
            ), None),
            "maintenance_signal": maintenance_signal,
            "maintenance_evidence_available": maintenance_signal != "unknown",
            "maintenance_evidence": maintenance_row if isinstance(maintenance_row, dict) else {},
            "current_tier": current_meta.get("tier"),
            "replacement_tier": alt_meta.get("tier"),
            "framework": row.get("framework") or drift_row.get("framework"),
            "project_type": row.get("project_type") or drift_row.get("project_type"),
            "primary_domain": row.get("primary_domain") or drift_row.get("primary_domain"),
            "platform": row.get("platform") or (
                next((
                    value for value in current_meta.get("platforms", [])
                    if isinstance(value, str) and value
                ), None) if isinstance(current_meta.get("platforms"), list) else None
            ),
            "current_major_version": current_meta.get("majorVersion"),
            "replacement_major_version": alt_meta.get("majorVersion"),
            "reason": (
                "runtime degradation and benchmark evidence both favor an alternative"
                + ("; maintenance is also weak" if maintenance_signal in {"aging","stale","archived"} else
                   "; maintenance evidence should be reviewed before deprecation")
            ),
        })

    candidates.sort(
        key=lambda x: (
            float(x.get("drift_score", 0.0) or 0.0),
            float(x.get("benchmark_delta", 0.0) or 0.0),
        ),
        reverse=True,
    )
    return {
        "version": 2,
        "status": "evaluated",
        "advisory_only": True,
        "deprecation_candidates": candidates[:20],
        "policy": {
            "auto_deprecate": False,
            "auto_migrate": False,
            "minimum_drift_score": MIN_DRIFT_SCORE,
            "require_benchmark_migration_candidate": True,
            "require_maintenance_review_before_deprecation": True,
            "require_dependency_policy_approval": True,
        },
    }

def write(learning: dict, benchmark: dict, recommendations: dict, out: Path, maintenance: dict[str, dict] | None = None) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    result = evaluate(learning, benchmark, recommendations, maintenance=maintenance)
    atomic_write_text(
        out / "architecture-obsolescence.json",
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return result
