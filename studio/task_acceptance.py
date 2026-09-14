"""Deterministic acceptance gate for one objective-DAG task."""
from __future__ import annotations


def criteria_evidence(active_task: dict | None, review: dict | None) -> dict:
    criteria = []
    if isinstance(active_task, dict):
        criteria = [
            str(item).strip()
            for item in active_task.get("done_when", [])
            if str(item).strip()
        ]
    if not criteria:
        title = str(active_task.get("title") or "").strip() if isinstance(active_task, dict) else ""
        criteria = [title] if title else []

    rows = review.get("criteria") if isinstance(review, dict) else None
    if not isinstance(rows, list):
        return {
            "complete": False,
            "criteria": criteria,
            "missing": criteria,
            "failed": [],
            "evidence": [],
        }

    by_criterion = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        criterion = str(row.get("criterion") or "").strip()
        if not criterion or criterion in by_criterion:
            continue
        by_criterion[criterion] = {
            "criterion": criterion,
            "passed": row.get("passed") is True,
            "evidence": str(row.get("evidence") or "").strip()[:2000],
        }

    missing = [criterion for criterion in criteria if criterion not in by_criterion]
    failed = [
        criterion
        for criterion in criteria
        if criterion in by_criterion and by_criterion[criterion]["passed"] is not True
    ]
    evidence = [by_criterion[criterion] for criterion in criteria if criterion in by_criterion]
    return {
        "complete": not missing and not failed and bool(criteria),
        "criteria": criteria,
        "missing": missing,
        "failed": failed,
        "evidence": evidence,
    }


def accepted(
    *,
    verification: dict | None,
    review: dict | None,
    changed_files: list[str],
    active_task: dict | None = None,
) -> bool:
    if not isinstance(verification, dict) or verification.get("passed") is not True:
        return False
    if not isinstance(review, dict) or review.get("complete") is not True:
        return False
    if not bool([item for item in changed_files if isinstance(item, str) and item]):
        return False
    if active_task is not None:
        return criteria_evidence(active_task, review)["complete"] is True
    return True


def failure_reason(
    *,
    verification: dict | None,
    review: dict | None,
    active_task: dict | None = None,
) -> str:
    if not isinstance(verification, dict) or verification.get("passed") is not True:
        return "trusted verification failed"
    if not isinstance(review, dict) or review.get("complete") is not True:
        if isinstance(review, dict):
            reason=str(review.get("reason") or "").strip()
            if reason:
                return reason[:1000]
        return "task acceptance review incomplete"
    if active_task is not None:
        evidence = criteria_evidence(active_task, review)
        if evidence["missing"]:
            return "task acceptance criteria missing evidence: " + ", ".join(evidence["missing"])[:900]
        if evidence["failed"]:
            return "task acceptance criteria failed: " + ", ".join(evidence["failed"])[:900]
    return "task produced no publishable changes"
