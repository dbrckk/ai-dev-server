"""Global admission decisions for autonomous project execution."""
from __future__ import annotations

DEFAULT_MAX_STANDARD_ADMISSIONS = 3
MIN_USEFUL_ROUND_TOKENS = 16_000


def _score(row: dict) -> float:
    priority = max(1, min(100, int(row.get("priority", 50)))) / 100.0
    success = max(
        0.05,
        min(0.95, float(row.get("predicted_success_probability", 0.50) or 0.50)),
    )
    efficiency = max(
        0.75,
        min(1.25, float(row.get("efficiency_multiplier", 1.0) or 1.0)),
    )
    reliability = max(
        0.75,
        min(1.25, float(row.get("reliability_multiplier", 1.0) or 1.0)),
    )
    requested = max(1, int(row.get("requested_tokens", 1) or 1))
    envelope = max(0, int(row.get("token_envelope", 0) or 0))
    coverage = min(1.0, envelope / requested)
    continuity = 1.10 if row.get("status") in {"running", "deferred", "failed"} else 1.0
    return round(priority * success * efficiency * reliability * (0.25 + 0.75 * coverage) * continuity, 6)


def decide(projects: list[dict], *, max_standard_admissions: int = DEFAULT_MAX_STANDARD_ADMISSIONS) -> dict:
    slots = max(1, int(max_standard_admissions))
    decisions = []
    ordinary = []

    for raw in projects:
        if not isinstance(raw, dict):
            continue
        row = dict(raw)
        project_id = str(row.get("id") or "").strip()
        if not project_id:
            continue
        envelope = max(0, int(row.get("token_envelope", 0) or 0))
        requested = max(1, int(row.get("requested_tokens", 1) or 1))
        score = _score(row)

        base = {
            "id": project_id,
            "score": score,
            "token_envelope": envelope,
            "requested_tokens": requested,
            "critical": bool(row.get("critical")),
            "recovery_active": bool(row.get("recovery_active")),
        }

        if row.get("capacity_paused") or envelope <= 0:
            decisions.append({
                **base,
                "admitted": False,
                "action": "defer",
                "reason": "capacity_unavailable",
            })
            continue

        if row.get("recovery_active"):
            decisions.append({
                **base,
                "admitted": True,
                "action": "admit_recovery",
                "reason": "bounded_recovery_probe",
            })
            continue

        if row.get("critical"):
            decisions.append({
                **base,
                "admitted": True,
                "action": "admit_critical",
                "reason": "critical_phase_has_capacity",
            })
            continue

        useful_floor = min(requested, MIN_USEFUL_ROUND_TOKENS)
        if envelope < useful_floor:
            decisions.append({
                **base,
                "admitted": False,
                "action": "defer",
                "reason": "insufficient_useful_round_capacity",
            })
            continue

        ordinary.append({**base, "row": row})

    ordinary.sort(key=lambda item: (-item["score"], -int(item["row"].get("priority", 50)), item["id"]))
    cutoff_score = ordinary[slots - 1]["score"] if len(ordinary) >= slots else None
    for index, item in enumerate(ordinary):
        admitted = index < slots
        decisions.append({
            **{k: v for k, v in item.items() if k != "row"},
            "admitted": admitted,
            "action": "admit" if admitted else "defer",
            "reason": "ranked_within_admission_slots" if admitted else "fleet_admission_slots_saturated",
            "rank": index + 1,
            "preemption_candidate": bool(
                not admitted
                and cutoff_score is not None
                and item["score"] > 0
            ),
        })

    decisions.sort(key=lambda row: (not row["admitted"], -row["score"], row["id"]))
    return {
        "schema": 1,
        "max_standard_admissions": slots,
        "decisions": decisions,
        "summary": {
            "projects": len(decisions),
            "admitted": sum(1 for row in decisions if row["admitted"]),
            "deferred": sum(1 for row in decisions if not row["admitted"]),
            "recovery": sum(1 for row in decisions if row["action"] == "admit_recovery"),
            "critical": sum(1 for row in decisions if row["action"] == "admit_critical"),
        },
    }


def decision_for(report: dict, project_id: str) -> dict | None:
    rows = report.get("decisions") if isinstance(report, dict) else None
    if not isinstance(rows, list):
        return None
    return next(
        (row for row in rows if isinstance(row, dict) and row.get("id") == project_id),
        None,
    )
