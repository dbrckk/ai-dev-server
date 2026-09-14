"""Aggregate release confidence from verified objective-DAG evidence."""
from __future__ import annotations


def assess(dag_summary: dict | None, verification: dict | None) -> dict:
    if not isinstance(dag_summary, dict) or dag_summary.get("complete") is not True:
        return {
            "score": 0,
            "level": "incomplete",
            "weak_tasks": [],
            "ready_for_final_review": False,
        }
    if not isinstance(verification, dict) or verification.get("passed") is not True:
        return {
            "score": 0,
            "level": "unverified",
            "weak_tasks": [],
            "ready_for_final_review": False,
        }

    tasks = [task for task in dag_summary.get("tasks", []) if isinstance(task, dict)]
    if not tasks:
        return {
            "score": 0,
            "level": "unknown",
            "weak_tasks": [],
            "ready_for_final_review": False,
        }

    weighted_total = 0.0
    weight_total = 0.0
    weak = []
    for task in tasks:
        critical = bool(task.get("critical", False))
        confidence = task.get("confidence")
        value = int(confidence) if type(confidence) is int else 0
        minimum = 85 if critical else 65
        weight = 2.0 if critical else 1.0
        weighted_total += value * weight
        weight_total += weight
        if value < minimum:
            weak.append({
                "id": task.get("id"),
                "title": task.get("title"),
                "critical": critical,
                "confidence": confidence,
                "minimum": minimum,
                "gap": minimum - value,
            })

    weak.sort(key=lambda item: (-item["gap"], not item["critical"], str(item["id"])))
    score = int(round(weighted_total / max(1.0, weight_total)))
    if score >= 90 and not weak:
        level = "high"
    elif score >= 75 and not weak:
        level = "medium"
    else:
        level = "low"

    return {
        "score": score,
        "level": level,
        "weak_tasks": weak,
        "ready_for_final_review": not weak and score >= 75,
    }
