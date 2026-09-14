"""Apply conservative historical outcome evidence to advisory architecture rankings."""
from __future__ import annotations

import time

MIN_SAMPLES = 5
MAX_SCORE_BONUS = 3.0
MAX_STACK_SCORE_BONUS = 2.0
MAX_EVIDENCE_AGE_SECONDS = 30 * 24 * 60 * 60
SUCCESS_WEIGHT = 0.6
QUALITY_WEIGHT = 0.4
UNCERTAINTY_BLEND = 0.5

def _context_weight(row: dict, framework: str | None, project_type: str | None, primary_domain: str | None) -> float:
    """Down-weight legacy/generic evidence; full bonus requires matching context."""
    requested = (framework, project_type, primary_domain)
    fields = ("framework", "project_type", "primary_domain")
    explicit = 0
    for field, expected in zip(fields, requested):
        value = row.get(field)
        if isinstance(value, str) and value:
            if expected is not None and value != expected:
                return 0.0
            explicit += 1
    return min(1.0, 0.25 + explicit * 0.25)



def _learning_map(learning: dict, *, now: float) -> dict[tuple[str, str | None, str | None, str | None, str | None], dict]:
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
        framework = row.get("framework")
        framework = framework if isinstance(framework, str) and framework else None
        project_type = row.get("project_type")
        project_type = project_type if isinstance(project_type, str) and project_type else None
        primary_domain = row.get("primary_domain")
        primary_domain = primary_domain if isinstance(primary_domain, str) and primary_domain else None
        out[(repo, domain, framework, project_type, primary_domain)] = row
    return out


def apply(
    recommendations: dict,
    learning: dict | None,
    *,
    framework: str | None = None,
    project_type: str | None = None,
    primary_domain: str | None = None,
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
        normalized_project_type = project_type if isinstance(project_type, str) and project_type else None
        normalized_primary_domain = primary_domain if isinstance(primary_domain, str) and primary_domain else None
        if isinstance(repo, str):
            # Context-aware runs only consume evidence from the same context.
            # Legacy unscoped evidence remains usable only for legacy/unscoped callers.
            if any(x is not None for x in (
                domain,
                normalized_framework,
                normalized_project_type,
                normalized_primary_domain,
            )):
                keys = [
                    (
                        repo,
                        domain,
                        normalized_framework,
                        normalized_project_type,
                        normalized_primary_domain,
                    ),
                ]
            else:
                keys = [(repo, None, None, None, None)]
            for key in keys:
                history = evidence.get(key)
                if history is not None:
                    break
        base = item.get("score")
        base_score = float(base) if isinstance(base, (int, float)) else 0.0

        bonus = 0.0
        if history is not None:
            applied_count += 1
            success_rate = max(0.0, min(1.0, float(history["success_rate"])))
            posterior = history.get("posterior_success_rate")
            posterior_rate = max(0.0, min(1.0, float(posterior))) if isinstance(posterior, (int, float)) else success_rate
            wilson = history.get("wilson_lower_95")
            wilson_rate = max(0.0, min(1.0, float(wilson))) if isinstance(wilson, (int, float)) else posterior_rate
            conservative_success = UNCERTAINTY_BLEND * posterior_rate + (1.0 - UNCERTAINTY_BLEND) * wilson_rate
            mean_quality = history.get("quality_shrunk_mean", history.get("mean_quality_score"))
            quality_rate = (
                max(0.0, min(1.0, float(mean_quality) / 100.0))
                if isinstance(mean_quality, (int, float))
                else conservative_success
            )
            confidence = history.get("evidence_confidence")
            confidence = max(0.0, min(1.0, float(confidence))) if isinstance(confidence, (int, float)) else 1.0
            combined_rate = SUCCESS_WEIGHT * conservative_success + QUALITY_WEIGHT * quality_rate
            centered = (combined_rate - 0.5) * 2.0
            context_weight = _context_weight(history, normalized_framework, normalized_project_type, normalized_primary_domain)
            bonus = max(-MAX_SCORE_BONUS, min(MAX_SCORE_BONUS, centered * MAX_SCORE_BONUS * context_weight * confidence))
            item["historical_evidence"] = {
                "domain": history.get("domain"),
                "framework": history.get("framework"),
                "project_type": history.get("project_type"),
                "primary_domain": history.get("primary_domain"),
                "samples": history["samples"],
                "success_rate": success_rate,
                "posterior_success_rate": history.get("posterior_success_rate"),
                "wilson_lower_95": history.get("wilson_lower_95"),
                "conservative_success_rate": round(conservative_success, 4),
                "evidence_confidence": round(confidence, 4),
                "mean_model_calls": history.get("mean_model_calls"),
                "mean_cycles": history.get("mean_cycles"),
                "mean_blockers": history.get("mean_blockers"),
                "mean_quality_score": history.get("mean_quality_score"),
                "combined_outcome_rate": round(combined_rate, 4),
                "advisory_bonus": round(bonus, 4),
                "context_weight": round(context_weight, 4),
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
        "success_weight": SUCCESS_WEIGHT,
        "quality_weight": QUALITY_WEIGHT,
        "uncertainty_blend": UNCERTAINTY_BLEND,
    }
    return result


def stack_adjustment(
    candidate_repo: str,
    chosen_repos: list[str],
    learning: dict | None,
    *,
    framework: str | None = None,
    project_type: str | None = None,
    primary_domain: str | None = None,
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
        row_framework = row.get("framework")
        row_framework = row_framework if isinstance(row_framework, str) and row_framework else None
        normalized_framework = framework if isinstance(framework, str) and framework else None
        normalized_project_type = project_type if isinstance(project_type, str) and project_type else None
        normalized_primary_domain = primary_domain if isinstance(primary_domain, str) and primary_domain else None
        row_project_type = row.get("project_type")
        row_project_type = row_project_type if isinstance(row_project_type, str) and row_project_type else None
        row_primary_domain = row.get("primary_domain")
        row_primary_domain = row_primary_domain if isinstance(row_primary_domain, str) and row_primary_domain else None

        requested_context = (
            normalized_framework,
            normalized_project_type,
            normalized_primary_domain,
        )
        row_context = (
            row_framework,
            row_project_type,
            row_primary_domain,
        )
        if any(value is not None for value in requested_context):
            if row_context != requested_context:
                continue
        elif any(value is not None for value in row_context):
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
        mean_quality = row.get("mean_quality_score")
        quality_rate = (
            max(0.0, min(1.0, float(mean_quality) / 100.0))
            if isinstance(mean_quality, (int, float))
            else rate
        )
        combined_rate = SUCCESS_WEIGHT * rate + QUALITY_WEIGHT * quality_rate
        centered = (combined_rate - 0.5) * 2.0
        context_weight = _context_weight(row, normalized_framework, normalized_project_type, normalized_primary_domain)
        if context_weight <= 0:
            continue
        weight = min(1.0, samples / 10.0) * min(1.0, overlap / max(1, len(chosen))) * context_weight
        weighted += centered * weight
        total_weight += weight
        evidence.append({
            "repos": sorted(repo_set)[:12],
            "samples": samples,
            "success_rate": rate,
            "mean_quality_score": row.get("mean_quality_score"),
            "combined_outcome_rate": round(combined_rate, 4),
            "overlap_with_selected": overlap,
            "framework": row_framework,
            "project_type": row_project_type,
            "primary_domain": row_primary_domain,
            "context_weight": round(context_weight, 4),
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
            "success_weight": SUCCESS_WEIGHT,
            "quality_weight": QUALITY_WEIGHT,
        },
    }
