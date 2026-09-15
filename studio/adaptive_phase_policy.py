"""Fail-closed phase gating for adaptive autonomous orchestration."""
from __future__ import annotations


def planning_phase_decision(
    *,
    require_planning: bool,
    brief: str,
) -> dict:
    """Decide whether a model planning call is worth its round budget.

    A skipped planning call still produces the stable plan schema consumed by
    downstream implementation. Invalid or missing objective text fails closed
    to model planning rather than inventing a plan without a usable objective.
    """
    if require_planning:
        return {
            "launch_model": True,
            "plan": None,
            "reason": "adaptive planning required",
        }

    if not isinstance(brief, str) or not brief.strip():
        return {
            "launch_model": True,
            "plan": None,
            "reason": "invalid brief requires model planning",
        }

    objective = brief.strip()
    return {
        "launch_model": False,
        "reason": "adaptive policy skipped model planning",
        "plan": {
            "objective": objective,
            "work_items": [
                "Implement the requested objective using the existing repository architecture."
            ],
            "done_when": [
                "Trusted verification passes and no objective-specific work remains."
            ],
            "adaptive_skipped": True,
        },
    }


def review_phase_decision(
    *,
    require_review: bool,
    verification: dict,
    review_remaining: float,
) -> dict:
    """Decide whether a model review must run after trusted verification.

    Skipping the model reviewer is allowed only for rounds the adaptive role
    allocator marked low risk. Trusted verification remains authoritative: a
    failed or ambiguous verification can never be converted into completion.
    """
    try:
        remaining = max(0.0, float(review_remaining))
    except (TypeError, ValueError):
        remaining = 0.0

    if require_review:
        if remaining < 30.0:
            return {
                "launch_model": False,
                "review": {
                    "complete": False,
                    "remaining": ["review quota exhausted"],
                    "reason": (
                        "trusted model review was required but its phase quota "
                        "was exhausted"
                    ),
                    "adaptive_skipped": False,
                },
            }
        return {"launch_model": True, "review": None}

    verification_passed = (
        isinstance(verification, dict) and verification.get("passed") is True
    )
    return {
        "launch_model": False,
        "review": {
            "complete": verification_passed,
            "remaining": [] if verification_passed else ["trusted verification failed"],
            "reason": (
                "adaptive role allocation skipped model review after trusted verification"
                if verification_passed
                else "adaptive model review was skipped, but trusted verification did not pass"
            ),
            "adaptive_skipped": True,
        },
    }
