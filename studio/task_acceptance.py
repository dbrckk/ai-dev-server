"""Deterministic acceptance gate for one objective-DAG task."""
from __future__ import annotations


def accepted(*, verification: dict | None, review: dict | None, changed_files: list[str]) -> bool:
    if not isinstance(verification, dict) or verification.get("passed") is not True:
        return False
    if not isinstance(review, dict) or review.get("complete") is not True:
        return False
    return bool([item for item in changed_files if isinstance(item, str) and item])


def failure_reason(*, verification: dict | None, review: dict | None) -> str:
    if not isinstance(verification, dict) or verification.get("passed") is not True:
        return "trusted verification failed"
    if not isinstance(review, dict) or review.get("complete") is not True:
        if isinstance(review, dict):
            reason=str(review.get("reason") or "").strip()
            if reason:
                return reason[:1000]
        return "task acceptance review incomplete"
    return "task produced no publishable changes"
