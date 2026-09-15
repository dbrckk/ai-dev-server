"""Deterministic, checkpoint-aware preemption planning for fleet admission."""
from __future__ import annotations

MIN_SCORE_DELTA = 0.10
MIN_PRIORITY_DELTA = 20
PREEMPTIBLE_RUNTIME = {"running", "deferred", "failed"}
SAFE_CHECKPOINT_PHASES = {"published", "complete", "verified"}


def _by_id(rows):
    return {
        str(row.get("id")): row
        for row in rows
        if isinstance(row, dict) and isinstance(row.get("id"), str) and row.get("id")
    }


def plan(capacity_plan: dict, runtime_evidence: dict | None = None) -> dict:
    projects = capacity_plan.get("projects") if isinstance(capacity_plan, dict) else None
    admission = capacity_plan.get("admission") if isinstance(capacity_plan, dict) else None
    decisions = admission.get("decisions") if isinstance(admission, dict) else None
    if not isinstance(projects, list) or not isinstance(decisions, list):
        return {"schema": 1, "actions": [], "summary": {"preempt": 0, "blocked": 0}}

    project_by_id = _by_id(projects)
    evidence_by_id = runtime_evidence if isinstance(runtime_evidence, dict) else {}
    admitted = [row for row in decisions if isinstance(row, dict) and row.get("admitted") is True]
    waiting = [
        row for row in decisions
        if isinstance(row, dict)
        and row.get("admitted") is False
        and row.get("reason") == "fleet_admission_slots_saturated"
    ]

    victims = []
    for row in admitted:
        project = project_by_id.get(row.get("id"), {})
        runtime = str(project.get("status") or "")
        evidence = evidence_by_id.get(row.get("id"), {})
        phase = str(evidence.get("checkpoint_phase") or "")
        checkpoint_ok = bool(evidence.get("checkpoint_valid")) and phase in SAFE_CHECKPOINT_PHASES
        if (
            row.get("critical")
            or row.get("recovery_active")
            or runtime not in PREEMPTIBLE_RUNTIME
            or not checkpoint_ok
        ):
            continue
        victims.append({
            "id": row["id"],
            "score": float(row.get("score", 0.0) or 0.0),
            "priority": int(project.get("priority", 50) or 50),
            "checkpoint_phase": phase,
        })

    victims.sort(key=lambda row: (row["score"], row["priority"], row["id"]))
    waiting.sort(key=lambda row: (-float(row.get("score", 0.0) or 0.0), row["id"]))

    actions = []
    used_victims = set()
    for contender in waiting:
        contender_project = project_by_id.get(contender.get("id"), {})
        contender_score = float(contender.get("score", 0.0) or 0.0)
        contender_priority = int(contender_project.get("priority", 50) or 50)
        victim = next(
            (
                row for row in victims
                if row["id"] not in used_victims
                and contender_score >= row["score"] + MIN_SCORE_DELTA
                and contender_priority >= row["priority"] + MIN_PRIORITY_DELTA
            ),
            None,
        )
        if victim is None:
            actions.append({
                "contender_id": contender["id"],
                "action": "keep_deferred",
                "reason": "no_safe_lower_value_victim",
            })
            continue
        used_victims.add(victim["id"])
        actions.append({
            "contender_id": contender["id"],
            "victim_id": victim["id"],
            "action": "preempt",
            "reason": "higher_value_waiting_project",
            "contender_score": round(contender_score, 6),
            "victim_score": round(victim["score"], 6),
            "priority_delta": contender_priority - victim["priority"],
            "checkpoint_phase": victim["checkpoint_phase"],
        })

    return {
        "schema": 1,
        "actions": actions,
        "summary": {
            "preempt": sum(1 for row in actions if row["action"] == "preempt"),
            "blocked": sum(1 for row in actions if row["action"] != "preempt"),
            "safe_victims": len(victims),
            "waiting": len(waiting),
        },
    }
