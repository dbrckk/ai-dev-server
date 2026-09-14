"""Create a bounded migration plan from evidence-backed architecture deprecation candidates."""
from __future__ import annotations

import json
import math
import time
from pathlib import Path

from atomic_file import write_text as atomic_write_text
from architecture_replacement_reputation import lookup as lookup_reputation

MAX_PLANS = 8
LOW_RISK_DELTA = 15.0
MEDIUM_RISK_DELTA = 8.0

CONTEXT_WEIGHTS = {
    "framework": 0.25,
    "project_type": 0.15,
    "primary_domain": 0.10,
    "platform": 0.10,
    "current_major_version": 0.15,
    "replacement_major_version": 0.15,
    "version_jump": 0.10,
}
MIN_TRANSFERABILITY_FOR_RISK = 0.72
MIN_TRANSFERABILITY_FOR_POSITIVE_BIAS = 0.55
MAX_FUSED_HISTORIES = 8
MIN_FUSION_TRANSFERABILITY = 0.20
RECENCY_HALF_LIFE_DAYS = 180.0
RECENCY_FLOOR = 0.20

def _major(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if value >= 0 else None
    if isinstance(value, float) and value.is_integer() and value >= 0:
        return int(value)
    return None

def _version_similarity(expected, observed) -> float:
    expected=_major(expected)
    observed=_major(observed)
    if expected is None or observed is None:
        return 0.5
    gap=abs(expected-observed)
    if gap==0:
        return 1.0
    if gap==1:
        return 0.65
    if gap==2:
        return 0.35
    return 0.0

def _numeric_similarity(expected, observed) -> float:
    if not isinstance(expected,(int,float)) or isinstance(expected,bool):
        return 0.5
    if not isinstance(observed,(int,float)) or isinstance(observed,bool):
        return 0.5
    gap=abs(float(expected)-float(observed))
    if gap==0:
        return 1.0
    if gap<=1:
        return 0.65
    if gap<=2:
        return 0.35
    return 0.0

def _categorical_similarity(expected, observed) -> float:
    if expected is None or observed is None:
        return 0.5
    return 1.0 if expected==observed else 0.0

def _compatibility_distance(history: dict | None, context: dict) -> dict:
    if not isinstance(history,dict):
        return {
            "transferability": 0.0,
            "distance": 1.0,
            "components": {},
            "exact_context_match": False,
        }

    components={}
    components["framework"]=_categorical_similarity(context.get("framework"),history.get("framework"))
    components["project_type"]=_categorical_similarity(context.get("project_type"),history.get("project_type"))
    components["primary_domain"]=_categorical_similarity(context.get("primary_domain"),history.get("primary_domain"))
    components["platform"]=_categorical_similarity(context.get("platform"),history.get("platform"))
    components["current_major_version"]=_version_similarity(context.get("current_major_version"),history.get("current_major_version"))
    components["replacement_major_version"]=_version_similarity(context.get("replacement_major_version"),history.get("replacement_major_version"))

    expected_current=_major(context.get("current_major_version"))
    expected_replacement=_major(context.get("replacement_major_version"))
    observed_current=_major(history.get("current_major_version"))
    observed_replacement=_major(history.get("replacement_major_version"))
    expected_jump=(expected_replacement-expected_current) if expected_current is not None and expected_replacement is not None else None
    observed_jump=(observed_replacement-observed_current) if observed_current is not None and observed_replacement is not None else None
    components["version_jump"]=_numeric_similarity(expected_jump,observed_jump)

    transferability=sum(CONTEXT_WEIGHTS[key]*components[key] for key in CONTEXT_WEIGHTS)

    # Explicit categorical incompatibilities are stronger evidence than a merely
    # nearby version number, so they cap cross-context transfer.
    if context.get("framework") is not None and history.get("framework") is not None and context.get("framework")!=history.get("framework"):
        transferability=min(transferability,0.35)
    if context.get("project_type") is not None and history.get("project_type") is not None and context.get("project_type")!=history.get("project_type"):
        transferability=min(transferability,0.60)
    if context.get("platform") is not None and history.get("platform") is not None and context.get("platform")!=history.get("platform"):
        transferability=min(transferability,0.65)

    transferability=max(0.0,min(1.0,transferability))
    return {
        "transferability": round(transferability,4),
        "distance": round(1.0-transferability,4),
        "components": {key:round(value,4) for key,value in components.items()},
        "exact_context_match": all(value==1.0 for value in components.values()),
    }

def _reputation_state(evidence: dict | None) -> dict:
    if not isinstance(evidence,dict):
        return {
            "state":"UNOBSERVED",
            "reason":"no_historical_evidence",
            "promotion_eligible":False,
            "requires_revalidation":False,
        }

    samples=max(0,int(evidence.get("effective_samples",evidence.get("samples",0)) or 0))
    confidence=float(evidence.get("evidence_confidence",0.0) or 0.0)
    wilson=float(evidence.get("wilson_lower_95",0.0) or 0.0)
    regression=float(evidence.get("regression_rate",0.0) or 0.0)

    if evidence.get("sequential_drift") is True or evidence.get("regime_shift") is True:
        return {
            "state":"QUARANTINED",
            "reason":"active_performance_deterioration",
            "promotion_eligible":False,
            "requires_revalidation":True,
        }
    if evidence.get("evidence_conflict") is True:
        return {
            "state":"DEGRADED",
            "reason":"conflicting_historical_evidence",
            "promotion_eligible":False,
            "requires_revalidation":True,
        }
    if evidence.get("recovery_candidate") is True:
        return {
            "state":"RECOVERING",
            "reason":"sustained_recent_recovery",
            "promotion_eligible":False,
            "requires_revalidation":True,
        }
    if evidence.get("stale_evidence") is True:
        return {
            "state":"DEGRADED",
            "reason":"stale_historical_evidence",
            "promotion_eligible":False,
            "requires_revalidation":True,
        }
    if samples<5 or confidence<0.25:
        return {
            "state":"EXPERIMENTAL",
            "reason":"insufficient_effective_evidence",
            "promotion_eligible":False,
            "requires_revalidation":False,
        }
    if wilson>=0.70 and regression<=0.10 and confidence>=0.50:
        return {
            "state":"TRUSTED",
            "reason":"strong_consistent_historical_evidence",
            "promotion_eligible":True,
            "requires_revalidation":False,
        }
    if wilson<0.50 or regression>=0.25:
        return {
            "state":"DEGRADED",
            "reason":"weak_or_regressive_historical_evidence",
            "promotion_eligible":False,
            "requires_revalidation":True,
        }
    return {
        "state":"EXPERIMENTAL",
        "reason":"mixed_or_maturing_evidence",
        "promotion_eligible":False,
        "requires_revalidation":False,
    }

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

def _replacement_histories(learning: dict | None, current_repo: str, replacement_repo: str, context: dict | None = None) -> list[dict]:
    if not isinstance(learning, dict):
        return []
    rows=learning.get("rankings")
    if not isinstance(rows,list):
        return []
    context=context if isinstance(context,dict) else {}
    candidates=[]
    for row in rows:
        if not isinstance(row,dict):
            continue
        if row.get("current_repo")!=current_repo or row.get("replacement_repo")!=replacement_repo:
            continue
        compatibility=_compatibility_distance(row,context)
        transferability=float(compatibility.get("transferability",0.0) or 0.0)
        if transferability<MIN_FUSION_TRANSFERABILITY:
            continue
        item=dict(row)
        item["compatibility"]=compatibility
        candidates.append(item)
    candidates.sort(key=lambda item:(
        float(item.get("compatibility",{}).get("transferability",0.0) or 0.0),
        bool(item.get("eligible_for_bias")),
        float(item.get("evidence_confidence",0.0) or 0.0),
        int(item.get("samples",0) or 0),
    ),reverse=True)
    return candidates[:MAX_FUSED_HISTORIES]

def _replacement_history(learning: dict | None, current_repo: str, replacement_repo: str, context: dict | None = None) -> dict | None:
    histories=_replacement_histories(learning,current_repo,replacement_repo,context=context)
    return histories[0] if histories else None

def _recency_factor(history: dict, now: float | None = None) -> float:
    latest=history.get("latest_observed_at")
    if not isinstance(latest,(int,float)):
        return 0.5
    now=float(now) if isinstance(now,(int,float)) else time.time()
    age_seconds=max(0.0,now-float(latest))
    age_days=age_seconds/86400.0
    decay=math.pow(0.5,age_days/RECENCY_HALF_LIFE_DAYS)
    return round(max(RECENCY_FLOOR,min(1.0,decay)),4)

def _fusion_weight(history: dict, now: float | None = None) -> float:
    compatibility=history.get("compatibility") if isinstance(history.get("compatibility"),dict) else {}
    transferability=float(compatibility.get("transferability",0.0) or 0.0)
    confidence=float(history.get("evidence_confidence",0.0) or 0.0)
    samples=max(0,int(history.get("samples",0) or 0))
    sample_factor=min(1.0,samples/20.0)
    eligible_factor=1.0 if history.get("eligible_for_bias") is True else 0.35
    recency=_recency_factor(history,now=now)
    return max(0.0,transferability*confidence*sample_factor*eligible_factor*recency)

def _fuse_histories(histories: list[dict], now: float | None = None) -> dict | None:
    weighted=[]
    for history in histories:
        if not isinstance(history,dict):
            continue
        weight=_fusion_weight(history,now=now)
        if weight>0.0:
            weighted.append((weight,history))
    if not weighted:
        return None
    total=sum(weight for weight,_ in weighted)
    if total<=0:
        return None

    def avg(field,default=0.0):
        return sum(
            weight*float(history.get(field,default) or default)
            for weight,history in weighted
        )/total

    effective_samples=sum(
        float(history.get("samples",0) or 0)
        * float(history.get("compatibility",{}).get("transferability",0.0) or 0.0)
        * (1.0 if history.get("eligible_for_bias") is True else 0.35)
        * _recency_factor(history,now=now)
        for _,history in weighted
    )
    max_transfer=max(
        float(history.get("compatibility",{}).get("transferability",0.0) or 0.0)
        for _,history in weighted
    )
    fused_transfer=sum(
        weight*float(history.get("compatibility",{}).get("transferability",0.0) or 0.0)
        for weight,history in weighted
    )/total
    positive_weight=sum(
        weight for weight,history in weighted
        if float(history.get("wilson_lower_95",0.0) or 0.0)>=0.70
        and float(history.get("regression_rate",0.0) or 0.0)<=0.10
    )
    negative_weight=sum(
        weight for weight,history in weighted
        if float(history.get("wilson_lower_95",0.0) or 0.0)<0.50
        or float(history.get("regression_rate",0.0) or 0.0)>=0.25
    )
    conflict_ratio=min(positive_weight,negative_weight)/total if total>0 else 0.0
    evidence_conflict=positive_weight/total>=0.20 and negative_weight/total>=0.20
    contributors=[]
    for weight,history in weighted:
        compatibility=history.get("compatibility",{})
        contributors.append({
            "framework":history.get("framework"),
            "project_type":history.get("project_type"),
            "primary_domain":history.get("primary_domain"),
            "platform":history.get("platform"),
            "current_major_version":history.get("current_major_version"),
            "replacement_major_version":history.get("replacement_major_version"),
            "samples":history.get("samples"),
            "transferability":compatibility.get("transferability"),
            "evidence_confidence":history.get("evidence_confidence"),
            "latest_observed_at":history.get("latest_observed_at"),
            "recency_factor":_recency_factor(history,now=now),
            "regime_shift":history.get("regime_shift") is True,
            "regime_drop":history.get("regime_drop"),
            "regime_window_days":history.get("regime_window_days"),
            "regime_recent_success_rate":history.get("regime_recent_success_rate"),
            "sequential_drift":history.get("sequential_drift") if isinstance(history.get("sequential_drift"),dict) else {},
            "recovery_detected":(
                isinstance(history.get("sequential_drift"),dict)
                and history["sequential_drift"].get("recovery_detected") is True
            ),
            "normalized_weight":round(weight/total,4),
        })
    recency_weighted=sum(
        weight*_recency_factor(history,now=now)
        for weight,history in weighted
    )/total
    regime_shift_weight=sum(
        weight for weight,history in weighted
        if history.get("regime_shift") is True
    )/total
    regime_shift=regime_shift_weight>=0.35
    sequential_drift_weight=sum(
        weight for weight,history in weighted
        if isinstance(history.get("sequential_drift"),dict)
        and history["sequential_drift"].get("drift_detected") is True
    )/total
    sequential_drift=sequential_drift_weight>=0.35
    recovery_weight=sum(
        weight for weight,history in weighted
        if isinstance(history.get("sequential_drift"),dict)
        and history["sequential_drift"].get("recovery_detected") is True
    )/total
    recovery_candidate=(
        recovery_weight>=0.35
        and not sequential_drift
        and not regime_shift
    )
    return {
        "contributors":contributors,
        "contributor_count":len(contributors),
        "effective_samples":round(effective_samples,3),
        "transferability":round(fused_transfer,4),
        "max_transferability":round(max_transfer,4),
        "success_rate":round(avg("success_rate"),4),
        "posterior_success_rate":round(avg("posterior_success_rate",0.5),4),
        "wilson_lower_95":round(avg("wilson_lower_95"),4),
        "regression_rate":round(avg("regression_rate"),4),
        "rollback_rate":round(avg("rollback_rate"),4),
        "mean_quality_score":round(avg("mean_quality_score"),3),
        "evidence_confidence":round(min(1.0,effective_samples/20.0),4),
        "recency_half_life_days":RECENCY_HALF_LIFE_DAYS,
        "recency_floor":RECENCY_FLOOR,
        "temporal_confidence":round(recency_weighted,4),
        "stale_evidence":recency_weighted<0.40,
        "regime_shift":regime_shift,
        "regime_shift_weight":round(regime_shift_weight,4),
        "sequential_drift":sequential_drift,
        "sequential_drift_weight":round(sequential_drift_weight,4),
        "recovery_candidate":recovery_candidate,
        "recovery_weight":round(recovery_weight,4),
        "eligible_for_bias":effective_samples>=5.0,
        "evidence_conflict":evidence_conflict,
        "conflict_ratio":round(conflict_ratio,4),
        "positive_weight_share":round(positive_weight/total,4),
        "negative_weight_share":round(negative_weight/total,4),
    }

def _history_context_weight(history: dict | None, context: dict) -> float:
    if not isinstance(history,dict):
        return 0.0
    compatibility=history.get("compatibility")
    if isinstance(compatibility,dict) and isinstance(compatibility.get("transferability"),(int,float)):
        return round(max(0.0,min(1.0,float(compatibility["transferability"]))),4)
    return _compatibility_distance(history,context)["transferability"]

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

def plan(obsolescence: dict, recommendations: dict, learning: dict | None = None, reputation_registry: dict | None = None) -> dict:
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
        histories = _replacement_histories(learning,current_repo,replacement_repo,context=context)
        history = histories[0] if histories else None
        fused_history = _fuse_histories(histories)
        empirical_status="unobserved"
        empirical_priority_adjustment=0.0
        history_context_weight=(
            float(fused_history.get("transferability",0.0) or 0.0)
            if isinstance(fused_history,dict)
            else _history_context_weight(history,context)
        )
        evidence=fused_history if isinstance(fused_history,dict) else history
        reputation=_reputation_state(evidence)
        persisted_reputation=lookup_reputation(reputation_registry,context)
        if isinstance(persisted_reputation,dict):
            reputation={
                "state":persisted_reputation.get("state"),
                "reason":persisted_reputation.get("reason"),
                "promotion_eligible":persisted_reputation.get("promotion_eligible") is True,
                "requires_revalidation":persisted_reputation.get("requires_revalidation") is True,
                "transition_reason":persisted_reputation.get("transition_reason"),
                "updated_at":persisted_reputation.get("updated_at"),
                "source":"persistent_registry",
            }
        else:
            reputation["source"]="derived_current_evidence"
        if isinstance(evidence,dict) and evidence.get("eligible_for_bias") is True:
            regression=float(evidence.get("regression_rate",0.0) or 0.0)
            wilson=float(evidence.get("wilson_lower_95",0.0) or 0.0)
            confidence=float(evidence.get("evidence_confidence",0.0) or 0.0)
            empirical_priority_adjustment=max(-10.0,min(5.0,(wilson-0.5)*10.0-regression*10.0))*confidence*history_context_weight
            if isinstance(fused_history,dict) and fused_history.get("sequential_drift") is True:
                empirical_priority_adjustment=min(0.0,empirical_priority_adjustment)
                risk="high"
                empirical_status="sequential_drift_detected"
            elif isinstance(fused_history,dict) and fused_history.get("regime_shift") is True:
                empirical_priority_adjustment=min(0.0,empirical_priority_adjustment)
                risk="high"
                empirical_status="regime_shift_detected"
            elif isinstance(fused_history,dict) and fused_history.get("evidence_conflict") is True:
                empirical_priority_adjustment=min(0.0,empirical_priority_adjustment)
                empirical_status="conflicting_history"
            elif isinstance(fused_history,dict) and fused_history.get("recovery_candidate") is True:
                empirical_priority_adjustment=min(0.0,empirical_priority_adjustment)*0.25
                empirical_status="recovery_candidate"
            elif history_context_weight>=MIN_TRANSFERABILITY_FOR_RISK and (regression>=0.25 or wilson<0.5):
                risk="high"
                empirical_status="historically_risky"
            elif history_context_weight>=MIN_TRANSFERABILITY_FOR_POSITIVE_BIAS and wilson>=0.70 and regression<=0.10:
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
        if empirical_status=="regime_shift_detected":
            gates.insert(0,"replacement_regime_shift_revalidated")
        if empirical_status=="sequential_drift_detected":
            gates.insert(0,"replacement_sequential_drift_revalidated")
        if empirical_status=="recovery_candidate":
            gates.insert(0,"replacement_recovery_revalidated")
        if empirical_status=="conflicting_history":
            gates.insert(0,"conflicting_replacement_evidence_reviewed")
        if isinstance(fused_history,dict) and fused_history.get("stale_evidence") is True:
            gates.insert(0,"stale_replacement_evidence_revalidated")
        if reputation.get("state")=="QUARANTINED":
            gates.insert(0,"quarantined_replacement_revalidated")
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
            "fused_historical_evidence": fused_history,
            "replacement_reputation": reputation,
            "history_context_weight": history_context_weight,
            "compatibility_distance": (
                history.get("compatibility")
                if isinstance(history,dict) and isinstance(history.get("compatibility"),dict)
                else {"transferability":0.0,"distance":1.0,"components":{},"exact_context_match":False}
            ),
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
        "version": 14,
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

def write(obsolescence: dict, recommendations: dict, out: Path, learning: dict | None = None, reputation_registry: dict | None = None) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    result = plan(obsolescence, recommendations, learning=learning, reputation_registry=reputation_registry)
    atomic_write_text(
        out / "architecture-replacement-plan.json",
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return result
