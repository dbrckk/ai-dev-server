"""Independent deterministic preflight validation for architecture decisions."""
from __future__ import annotations

import json
from pathlib import Path

from atomic_file import write_text as atomic_write_text

MAX_REVIEW_ROWS = 24
MIN_OVERLAP_RATIO = 0.5


def _clean_rows(recommendations: dict) -> list[dict]:
    if not isinstance(recommendations, dict):
        return []
    rows = recommendations.get("matches")
    if not isinstance(rows, list):
        return []
    out = []
    for row in rows[:MAX_REVIEW_ROWS]:
        if not isinstance(row, dict):
            continue
        repo = row.get("repo")
        if not isinstance(repo, str) or not repo:
            continue
        avoid = row.get("avoid_when")
        if isinstance(avoid, list) and avoid:
            continue
        out.append(dict(row))
    return out


def _baseline_score(row: dict, primary_domain: str | None) -> float:
    raw = row.get("score")
    score = float(raw) if isinstance(raw, (int, float)) else 0.0
    quality = row.get("quality_score")
    if isinstance(quality, (int, float)):
        score += max(0.0, min(10.0, float(quality))) * 0.15
    if primary_domain and row.get("domain") == primary_domain:
        score += 0.5
    return round(score, 4)


def _baseline_rank(recommendations: dict, primary_domain: str | None) -> list[dict]:
    rows = _clean_rows(recommendations)
    ranked = [
        {
            "repo": row["repo"],
            "baseline_score": _baseline_score(row, primary_domain),
            "domain": row.get("domain"),
            "quality_score": row.get("quality_score"),
        }
        for row in rows
    ]
    ranked.sort(
        key=lambda item: (
            item["baseline_score"],
            float(item.get("quality_score", 0.0) or 0.0),
            item["repo"],
        ),
        reverse=True,
    )
    return ranked


def validate(decision: dict, recommendations: dict) -> dict:
    decision = decision if isinstance(decision, dict) else {}
    chosen = decision.get("chosen")
    chosen = chosen if isinstance(chosen, list) else []
    chosen_repos = [
        item.get("repo")
        for item in chosen
        if isinstance(item, dict) and isinstance(item.get("repo"), str)
    ]
    constraints = decision.get("constraints")
    constraints = constraints if isinstance(constraints, dict) else {}
    primary_domain = constraints.get("primary_domain")
    primary_domain = primary_domain if isinstance(primary_domain, str) and primary_domain else None

    baseline = _baseline_rank(recommendations, primary_domain)
    baseline_repos = [item["repo"] for item in baseline[: max(1, len(chosen_repos))]]
    top_matches = bool(chosen_repos and baseline_repos and chosen_repos[0] == baseline_repos[0])

    if chosen_repos:
        overlap = len(set(chosen_repos) & set(baseline_repos))
        overlap_ratio = overlap / max(1, len(set(chosen_repos)))
    else:
        overlap = 0
        overlap_ratio = 1.0

    policy = decision.get("autonomy_policy")
    policy = policy if isinstance(policy, dict) else {}
    requested_mode = policy.get("validation_mode", "standard")
    validation_required = policy.get("validation_required") is True

    converged = top_matches and overlap_ratio >= MIN_OVERLAP_RATIO
    if not validation_required:
        verdict = "pass"
        reason = "planner confidence is high; independent baseline is informational"
    elif converged:
        verdict = "pass"
        reason = "independent baseline sufficiently converges with planner selection"
    else:
        verdict = "hold"
        reason = "independent baseline does not sufficiently converge with planner selection"

    return {
        "schema": 1,
        "status": "validated",
        "verdict": verdict,
        "architecture_changes_allowed": verdict == "pass",
        "normal_code_changes_allowed": True,
        "validation_required": validation_required,
        "validation_mode": requested_mode,
        "independent_method": "raw_recommendation_quality_domain_baseline",
        "historical_feedback_used": False,
        "stack_feedback_used": False,
        "top_choice_matches": top_matches,
        "chosen_repositories": chosen_repos,
        "baseline_repositories": baseline_repos,
        "overlap_count": overlap,
        "overlap_ratio": round(overlap_ratio, 4),
        "minimum_overlap_ratio": MIN_OVERLAP_RATIO,
        "reason": reason,
        "baseline_ranking": baseline[:12],
    }


def write(decision: dict, recommendations: dict, out: Path) -> dict:
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    result = validate(decision, recommendations)
    atomic_write_text(
        out / "architecture-preflight.json",
        json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return result
