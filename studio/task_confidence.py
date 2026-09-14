"""Confidence scoring for verified objective DAG tasks."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TaskConfidence:
    score: int
    level: str
    factors: dict

    def as_dict(self) -> dict:
        return {"score": self.score, "level": self.level, "factors": self.factors}


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def score(
    *,
    verification: dict | None,
    semantic_context: dict | None,
    fragility: dict | None,
    dependency: dict | None,
    task_attempts: int,
) -> TaskConfidence:
    passed = isinstance(verification, dict) and verification.get("passed") is True
    if not passed:
        return TaskConfidence(
            score=0,
            level="unverified",
            factors={"verification_passed": False},
        )

    value = 70.0
    factors: dict[str, object] = {"verification_passed": True, "base": 70}

    stability_confirmed = verification.get("stability_confirmed") is True
    if stability_confirmed:
        value += 10
    factors["stability_confirmed"] = stability_confirmed

    recent_attempts = []
    if isinstance(semantic_context, dict):
        recent_attempts = [
            item for item in semantic_context.get("recent_attempts", [])
            if isinstance(item, dict)
        ]
    failed_recent = sum(1 for item in recent_attempts if item.get("status") != "verified")
    retry_penalty = min(18, failed_recent * 6 + max(0, int(task_attempts) - 1) * 2)
    value -= retry_penalty
    factors["retry_penalty"] = retry_penalty
    factors["failed_recent_attempts"] = failed_recent

    fragility_risk = 0.0
    fragility_level = "unknown"
    if isinstance(fragility, dict):
        fragility_risk = float(fragility.get("max_risk", 0.0) or 0.0)
        fragility_level = str(fragility.get("level", "unknown"))
    fragility_penalty = round(_clamp(fragility_risk, 0.0, 1.0) * 12, 2)
    value -= fragility_penalty
    factors["fragility_level"] = fragility_level
    factors["fragility_penalty"] = fragility_penalty

    coupling = 0
    if isinstance(dependency, dict):
        coupling = max(0, int(dependency.get("max_coupling", 0) or 0))
    coupling_penalty = min(10, coupling)
    value -= coupling_penalty
    factors["max_coupling"] = coupling
    factors["coupling_penalty"] = coupling_penalty

    targeted = verification.get("targeted_precheck") if isinstance(verification, dict) else None
    impacted_tests = []
    if isinstance(verification, dict):
        impact = verification.get("targeted_impact")
        if isinstance(impact, dict):
            impacted_tests = impact.get("impacted_tests", []) if isinstance(impact.get("impacted_tests"), list) else []
    targeted_bonus = 0
    if impacted_tests:
        if isinstance(targeted, dict) and targeted.get("passed") is True:
            targeted_bonus = 5
        elif not isinstance(targeted, dict) or targeted.get("status") == "unsupported":
            targeted_bonus = 0
        else:
            targeted_bonus = -5
    value += targeted_bonus
    factors["impacted_test_count"] = len(impacted_tests)
    factors["targeted_test_adjustment"] = targeted_bonus

    semantic_verified = bool(
        isinstance(semantic_context, dict)
        and semantic_context.get("last_status") == "verified"
    )
    if semantic_verified:
        value += 3
    factors["semantic_verified_evidence"] = semantic_verified

    final_score = int(round(_clamp(value)))
    if final_score >= 85:
        level = "high"
    elif final_score >= 70:
        level = "medium"
    else:
        level = "low"
    return TaskConfidence(score=final_score, level=level, factors=factors)


def can_unlock_critical(confidence: dict | TaskConfidence, *, minimum: int = 85) -> bool:
    if isinstance(confidence, TaskConfidence):
        value = confidence.score
    elif isinstance(confidence, dict):
        value = int(confidence.get("score", 0) or 0)
    else:
        return False
    return value >= minimum
