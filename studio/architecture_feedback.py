"""Apply conservative historical outcome evidence to advisory architecture rankings."""
from __future__ import annotations

import time

MIN_SAMPLES = 5
MAX_SCORE_BONUS = 3.0
MAX_STACK_SCORE_BONUS = 2.0
MAX_EVIDENCE_AGE_SECONDS = 30 * 24 * 60 * 60


def _learning_map(learning: dict, *, now: float) -> dict[tuple[str, str | None, str | None], dict]:
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
        row_framework = row.get("framework")
        row_framework = row_framework if isinstance(row_framework, str) and row_framework else None
        normalized_framework = framework if isinstance(framework, str) and framework else None
        if row_framework is not None and normalized_framework is not None and row_framework != normalized_framework:
            continue
        if row_framework is not None and normalized_framework is None:
            continue
        latest = row.get("latest_observed_at")
        if isinstance(latest, (int, float)) and now - float(latest) > MAX_EVIDENCE_AGE_SECONDS:
            continue
        domain = row.get("domain")
        domain = domain if isinstance(domain, str) and domain else None
        framework = row.get("framework")
        framework = framework if isinstance(framework, str) and framework else None
        out[(repo, domain, framework)] = row
    return out


def apply(
    recommendations: dict,
    learning: dict | None,
    *,
    framework: str | None = None,
    now: float | None = None,
) -> dict:
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
        normalized_framework = framework if isinstance(framework, str) and framework else None
        if isinstance(repo, str):
            history = evidence.get((repo, domain, normalized_framework))
            if history is None:
                history = evidence.get((repo, None, normalized_framework))
            if history is None:
                history = evidence.get((repo, domain, None))
            if history is None:
                history = evidence.get((repo, None, None))
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
                "framework": history.get("framework"),
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


def stack_adjustment(
    candidate_repo: str,
    chosen_repos: list[str],
    learning: dict | None,
    *,
    framework: str | None = None,
    now: float | None = None,
) -> dict:
    """Return a bounded synergy adjustment from verified historical stack outcomes."""
    if not isinstance(candidate_repo, str) or not candidate_repo:
        return {"bonus": 0.0, "evidence": []}
    if not isinstance(learning, dict):
        return {"bonus": 0.0, "evidence": []}
    rows = learning.get("stack_rankings")
    if not isinstance(rows, list):
        return {"bonus": 0.0, "evidence": []}

    now_value = time.time() if now is None else float(now)
    chosen = {x for x in chosen_repos if isinstance(x, str) and x}
    evidence = []
    weighted = 0.0
    total_weight = 0.0

    for row in rows:
        if not isinstance(row, dict):
            continue
        repos = row.get("repos")
        samples = row.get("samples")
        success_rate = row.get("success_rate")
        if not isinstance(repos, list) or candidate_repo not in repos:
            continue
        if not isinstance(samples, int) or samples < MIN_SAMPLES:
            continue
        if not isinstance(success_rate, (int, float)):
            continue
        latest = row.get("latest_observed_at")
        if isinstance(latest, (int, float)) and now_value - float(latest) > MAX_EVIDENCE_AGE_SECONDS:
            continue

        repo_set = {x for x in repos if isinstance(x, str)}
        overlap = len(chosen & repo_set)
        if chosen and overlap == 0:
            continue

        # Require at least candidate + one selected repo before claiming synergy.
        if chosen and overlap < 1:
            continue
        if not chosen:
            continue

        rate = max(0.0, min(1.0, float(success_rate)))
        centered = (rate - 0.5) * 2.0
        weight = min(1.0, samples / 10.0) * min(1.0, overlap / max(1, len(chosen)))
        weighted += centered * weight
        total_weight += weight
        evidence.append({
            "repos": sorted(repo_set)[:12],
            "samples": samples,
            "success_rate": rate,
            "overlap_with_selected": overlap,
        })

    if total_weight <= 0:
        return {"bonus": 0.0, "evidence": []}

    raw = (weighted / total_weight) * MAX_STACK_SCORE_BONUS
    bonus = max(-MAX_STACK_SCORE_BONUS, min(MAX_STACK_SCORE_BONUS, raw))
    return {
        "bonus": round(bonus, 4),
        "evidence": evidence[:5],
        "policy": {
            "minimum_samples": MIN_SAMPLES,
            "max_stack_score_bonus": MAX_STACK_SCORE_BONUS,
            "advisory_only": True,
        },
    }
