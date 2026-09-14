"""Apply conservative historical outcome evidence to advisory architecture rankings."""
from __future__ import annotations

import time

MIN_SAMPLES = 5
MAX_SCORE_BONUS = 3.0
MAX_EVIDENCE_AGE_SECONDS = 30 * 24 * 60 * 60


def _learning_map(learning: dict, *, now: float) -> dict[tuple[str, str | None], dict]:
    if not isinstance(learning, dict):
        return {}
    rows = learning.get("rankings")
    if not isinstance(rows, list):
        return {}
    out = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        repo = row.get("repo")
        if not isinstance(repo, str) or not repo:
            continue
        samples = row.get("samples")
        success_rate = row.get("success_rate")
        if not isinstance(samples, int) or samples < MIN_SAMPLES:
            continue
        if not isinstance(success_rate, (int, float)):
            continue
        latest = row.get("latest_observed_at")
        if isinstance(latest, (int, float)) and now - float(latest) > MAX_EVIDENCE_AGE_SECONDS:
            continue
        domain = row.get("domain")
        domain = domain if isinstance(domain, str) and domain else None
        out[(repo, domain)] = row
    return out


def apply(recommendations: dict, learning: dict | None, *, now: float | None = None) -> dict:
    if not isinstance(recommendations, dict):
        return {"matches": [], "feedback_applied": False}
    rows = recommendations.get("matches")
    rows = rows if isinstance(rows, list) else []
    now_value = time.time() if now is None else float(now)
    evidence = _learning_map(learning or {}, now=now_value)

    adjusted = []
    applied_count = 0
    for row in rows:
        if not isinstance(row, dict):
            continue
        item = dict(row)
        repo = item.get("repo")
        domain = item.get("domain")
        domain = domain if isinstance(domain, str) and domain else None
        history = None
        if isinstance(repo, str):
            history = evidence.get((repo, domain))
            if history is None:
                history = evidence.get((repo, None))
        base = item.get("score")
        base_score = float(base) if isinstance(base, (int, float)) else 0.0

        bonus = 0.0
        if history is not None:
            applied_count += 1
            success_rate = max(0.0, min(1.0, float(history["success_rate"])))
            centered = (success_rate - 0.5) * 2.0
            bonus = max(-MAX_SCORE_BONUS, min(MAX_SCORE_BONUS, centered * MAX_SCORE_BONUS))
            item["historical_evidence"] = {
                "domain": history.get("domain"),
                "samples": history["samples"],
                "success_rate": success_rate,
                "mean_model_calls": history.get("mean_model_calls"),
                "mean_cycles": history.get("mean_cycles"),
                "mean_blockers": history.get("mean_blockers"),
                "advisory_bonus": round(bonus, 4),
            }
        item["feedback_score"] = round(base_score + bonus, 4)
        adjusted.append(item)

    adjusted.sort(
        key=lambda row: (
            float(row.get("feedback_score", 0.0)),
            float(row.get("quality_score", 0.0) or 0.0),
        ),
        reverse=True,
    )
    result = dict(recommendations)
    result["matches"] = adjusted
    result["feedback_applied"] = applied_count > 0
    result["feedback_rows_applied"] = applied_count
    result["feedback_policy"] = {
        "minimum_samples": MIN_SAMPLES,
        "max_score_bonus": MAX_SCORE_BONUS,
        "advisory_only": True,
        "can_add_dependency": False,
        "max_evidence_age_seconds": MAX_EVIDENCE_AGE_SECONDS,
    }
    return result
