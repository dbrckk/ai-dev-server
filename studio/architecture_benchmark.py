"""Compare selected architecture repositories with known alternatives using bounded evidence."""
from __future__ import annotations

import json
from pathlib import Path

from atomic_file import write_text as atomic_write_text

MIN_MIGRATION_DELTA = 8.0

def _index(recommendations: dict) -> dict[str, dict]:
    rows = recommendations.get("matches", []) if isinstance(recommendations, dict) else []
    return {
        row["repo"]: row for row in rows
        if isinstance(row, dict) and isinstance(row.get("repo"), str)
    }

def _num(value, default=0.0) -> float:
    return float(value) if isinstance(value, (int, float)) else default

def _candidate_score(row: dict, *, selected: bool, review: bool, blocker_count: int) -> float:
    selection = _num(row.get("selection_score", row.get("score")), 0.0)
    quality = _num(row.get("quality_score"), 0.0) * 3.0
    tier = {"core": 8.0, "recommended": 5.0, "specialized": 2.0, "audit": -5.0}.get(row.get("tier"), 0.0)
    score = selection * 0.65 + quality + tier
    if selected and review:
        score -= min(18.0, blocker_count * 4.0)
    if row.get("avoid_when"):
        score -= 12.0
    return round(score, 3)

def benchmark(decision: dict, evaluation: dict, recommendations: dict) -> dict:
    rec_index = _index(recommendations)
    review = isinstance(evaluation, dict) and evaluation.get("verdict") == "review"
    blockers = evaluation.get("blockers", []) if isinstance(evaluation, dict) else []
    blocker_count = len(blockers) if isinstance(blockers, list) else 0

    constraints = decision.get("constraints") if isinstance(decision, dict) and isinstance(decision.get("constraints"), dict) else {}
    comparisons = []
    for chosen in decision.get("chosen", [])[:8] if isinstance(decision, dict) else []:
        if not isinstance(chosen, dict) or not isinstance(chosen.get("repo"), str):
            continue
        current = dict(chosen)
        current_score = _candidate_score(current, selected=True, review=review, blocker_count=blocker_count)
        alternatives = []
        for alt_name in chosen.get("alternatives", [])[:8]:
            alt = rec_index.get(alt_name)
            if not alt:
                alternatives.append({
                    "repo": alt_name,
                    "status": "metadata_unavailable",
                    "benchmark_score": None,
                })
                continue
            alt_score = _candidate_score(alt, selected=False, review=review, blocker_count=blocker_count)
            alternatives.append({
                "repo": alt_name,
                "status": "scored",
                "benchmark_score": alt_score,
                "quality_score": alt.get("quality_score"),
                "tier": alt.get("tier"),
                "capabilities": alt.get("capabilities", [])[:12],
                "delta_vs_current": round(alt_score - current_score, 3),
            })
        scored = [x for x in alternatives if isinstance(x.get("benchmark_score"), (int, float))]
        best = max(scored, key=lambda x: x["benchmark_score"]) if scored else None
        migration = bool(
            review and best and best["benchmark_score"] - current_score >= MIN_MIGRATION_DELTA
        )
        comparisons.append({
            "current_repo": chosen["repo"],
            "framework": constraints.get("framework"),
            "project_type": constraints.get("project_type"),
            "primary_domain": constraints.get("primary_domain"),
            "platform": constraints.get("platform"),
            "current_score": current_score,
            "alternatives": alternatives,
            "best_alternative": best["repo"] if best else None,
            "migration_candidate": migration,
            "migration_reason": (
                f"alternative exceeds current score by at least {MIN_MIGRATION_DELTA} under observed blockers"
                if migration else "retain unless stronger runtime evidence is produced"
            ),
        })

    migration_candidates = [x for x in comparisons if x["migration_candidate"]]
    return {
        "version": 2,
        "status": "benchmarked",
        "advisory_only": True,
        "evaluation_verdict": evaluation.get("verdict") if isinstance(evaluation, dict) else None,
        "comparisons": comparisons,
        "migration_candidates": migration_candidates,
        "policy": {
            "auto_migrate": False,
            "require_isolated_benchmark": True,
            "require_dependency_policy_approval": True,
            "minimum_score_delta": MIN_MIGRATION_DELTA,
        },
    }

def write(decision: dict, evaluation: dict, recommendations: dict, out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    result = benchmark(decision, evaluation, recommendations)
    atomic_write_text(
        out / "architecture-benchmark.json",
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return result
