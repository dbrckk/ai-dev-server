"""Create a bounded migration plan from evidence-backed architecture deprecation candidates."""
from __future__ import annotations

import json
from pathlib import Path

from atomic_file import write_text as atomic_write_text

MAX_PLANS = 8
LOW_RISK_DELTA = 15.0
MEDIUM_RISK_DELTA = 8.0

def _index(recommendations: dict) -> dict[str, dict]:
    rows = recommendations.get("matches", []) if isinstance(recommendations, dict) else []
    return {
        row["repo"]: row
        for row in rows
        if isinstance(row, dict) and isinstance(row.get("repo"), str)
    }

def _risk(current: dict, replacement: dict, benchmark_delta: float | None) -> str:
    current_caps = set(current.get("capabilities", []) if isinstance(current.get("capabilities"), list) else [])
    replacement_caps = set(replacement.get("capabilities", []) if isinstance(replacement.get("capabilities"), list) else [])
    missing = current_caps - replacement_caps
    delta = float(benchmark_delta) if isinstance(benchmark_delta, (int, float)) else 0.0
    if missing or delta < MEDIUM_RISK_DELTA:
        return "high"
    if delta < LOW_RISK_DELTA:
        return "medium"
    return "low"

def _replacement_history(learning: dict | None, current_repo: str, replacement_repo: str, context: dict | None = None) -> dict | None:
    if not isinstance(learning, dict):
        return None
    rows=learning.get("rankings")
    if not isinstance(rows,list):
        return None
    context=context if isinstance(context,dict) else {}
    fields=("framework","project_type","primary_domain","platform","current_major_version","replacement_major_version")
    candidates=[]
    for row in rows:
        if not isinstance(row,dict):
            continue
        if row.get("current_repo")!=current_repo or row.get("replacement_repo")!=replacement_repo:
            continue
        mismatch=False
        specificity=0
        for field in fields:
            expected=context.get(field)
            observed=row.get(field)
            if isinstance(observed,str) and observed:
                if isinstance(expected,str) and expected:
                    if observed!=expected:
                        mismatch=True
                        break
                    specificity+=1
            elif isinstance(observed,(int,float)) and observed is not None:
                if isinstance(expected,(int,float)) and expected is not None:
                    if observed!=expected:
                        mismatch=True
                        break
                    specificity+=1
        if not mismatch:
            candidates.append((specificity,row))
    if not candidates:
        return None
    candidates.sort(key=lambda item:(
        item[0],
        bool(item[1].get("eligible_for_bias")),
        float(item[1].get("evidence_confidence",0.0) or 0.0),
        int(item[1].get("samples",0) or 0),
    ),reverse=True)
    return candidates[0][1]

def _impact(current: dict, replacement: dict) -> dict:
    current_caps = set(current.get("capabilities", []) if isinstance(current.get("capabilities"), list) else [])
    replacement_caps = set(replacement.get("capabilities", []) if isinstance(replacement.get("capabilities"), list) else [])
    current_lang = set(current.get("languages", []) if isinstance(current.get("languages"), list) else [])
    replacement_lang = set(replacement.get("languages", []) if isinstance(replacement.get("languages"), list) else [])
    current_platform = set(current.get("platforms", []) if isinstance(current.get("platforms"), list) else [])
    replacement_platform = set(replacement.get("platforms", []) if isinstance(replacement.get("platforms"), list) else [])

    return {
        "capabilities_preserved": sorted(current_caps & replacement_caps),
        "capabilities_missing": sorted(current_caps - replacement_caps),
        "capabilities_added": sorted(replacement_caps - current_caps),
        "language_overlap": sorted(current_lang & replacement_lang),
        "platform_overlap": sorted(current_platform & replacement_platform),
        "runtime_change": current.get("runtime") != replacement.get("runtime"),
        "integration_complexity_change": {
            "from": current.get("integrationComplexity"),
            "to": replacement.get("integrationComplexity"),
        },
        "resource_level_change": {
            "from": current.get("resourceLevel"),
            "to": replacement.get("resourceLevel"),
        },
    }

def plan(obsolescence: dict, recommendations: dict, learning: dict | None = None) -> dict:
    recs = _index(recommendations)
    rows = obsolescence.get("deprecation_candidates", []) if isinstance(obsolescence, dict) else []
    plans = []

    for row in rows[:MAX_PLANS]:
        if not isinstance(row, dict):
            continue
        current_repo = row.get("repo")
        replacement_repo = row.get("replacement_candidate")
        if not isinstance(current_repo, str) or not isinstance(replacement_repo, str):
            continue

        current = recs.get(current_repo, {})
        replacement = recs.get(replacement_repo, {})
        impact = _impact(current, replacement)
        risk = _risk(current, replacement, row.get("benchmark_delta"))
        context={
            "framework":row.get("framework"),
            "project_type":row.get("project_type"),
            "primary_domain":row.get("primary_domain"),
            "platform":row.get("platform"),
            "current_major_version":row.get("current_major_version"),
            "replacement_major_version":row.get("replacement_major_version"),
        }
        history = _replacement_history(learning,current_repo,replacement_repo,context=context)
        empirical_status="unobserved"
        empirical_priority_adjustment=0.0
        if isinstance(history,dict) and history.get("eligible_for_bias") is True:
            regression=float(history.get("regression_rate",0.0) or 0.0)
            wilson=float(history.get("wilson_lower_95",0.0) or 0.0)
            confidence=float(history.get("evidence_confidence",0.0) or 0.0)
            empirical_priority_adjustment=max(-10.0,min(5.0,(wilson-0.5)*10.0-regression*10.0))*confidence
            if regression>=0.25 or wilson<0.5:
                risk="high"
                empirical_status="historically_risky"
            elif wilson>=0.70 and regression<=0.10:
                empirical_status="historically_supported"
            else:
                empirical_status="mixed_history"

        gates = [
            "replacement_metadata_available",
            "capability_parity_reviewed",
            "dependency_policy_approved",
            "isolated_migration_branch_created",
            "existing_tests_pass_before_migration",
            "migration_tests_added",
            "existing_tests_pass_after_migration",
            "release_build_non_regressing",
            "rollback_path_verified",
        ]
        if impact["capabilities_missing"]:
            gates.insert(1, "missing_capabilities_resolved")
        if empirical_status=="historically_risky":
            gates.insert(0,"historical_replacement_risk_reviewed")
        if row.get("maintenance_evidence_available") is not True:
            gates.insert(0, "maintenance_evidence_completed")

        plans.append({
            "current_repo": current_repo,
            "replacement_repo": replacement_repo,
            "status": "replacement_plan_ready",
            "risk": risk,
            "benchmark_delta": row.get("benchmark_delta"),
            "drift_score": row.get("drift_score"),
            "maintenance_signal": row.get("maintenance_signal"),
            "framework": context.get("framework"),
            "project_type": context.get("project_type"),
            "primary_domain": context.get("primary_domain"),
            "platform": context.get("platform"),
            "current_major_version": context.get("current_major_version"),
            "replacement_major_version": context.get("replacement_major_version"),
            "historical_replacement_evidence": history,
            "empirical_status": empirical_status,
            "empirical_priority_adjustment": round(empirical_priority_adjustment,3),
            "priority_score": round(float(row.get("benchmark_delta",0.0) or 0.0)+empirical_priority_adjustment,3),
            "impact": impact,
            "estimated_change_scope": (
                "broad" if risk == "high" else "moderate" if risk == "medium" else "narrow"
            ),
            "migration_steps": [
                "inventory current dependency/API usage in the target project",
                "map each used capability to the replacement",
                "create an isolated migration branch or worktree",
                "add compatibility tests before modifying dependencies",
                "apply the smallest dependency/API changes required",
                "run unit, integration, visual and release regression gates",
                "compare before/after evidence and benchmark results",
                "promote only if all gates pass; otherwise rollback",
            ],
            "required_gates": gates,
            "go_no_go": "NO_GO_PENDING_ISOLATED_BENCHMARK",
        })

    plans.sort(key=lambda row:(
        float(row.get("priority_score",0.0) or 0.0),
        row.get("risk")=="low",
        row.get("empirical_status")=="historically_supported",
    ),reverse=True)

    return {
        "version": 3,
        "status": "planned",
        "advisory_only": True,
        "replacement_plans": plans,
        "policy": {
            "auto_modify_dependencies": False,
            "auto_apply_migration": False,
            "require_isolated_execution": True,
            "require_before_after_benchmark": True,
            "require_rollback": True,
            "require_dependency_policy_approval": True,
        },
    }

def write(obsolescence: dict, recommendations: dict, out: Path, learning: dict | None = None) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    result = plan(obsolescence, recommendations, learning=learning)
    atomic_write_text(
        out / "architecture-replacement-plan.json",
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return result
