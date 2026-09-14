"""Persistent reputation registry with audited hysteretic state transitions."""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

from atomic_file import write_text as atomic_write_text

REGISTRY_VERSION=5
MAX_AUDIT_EVENTS=500
RECOVERY_CONFIRMATIONS_REQUIRED=2
RECOVERY_MIN_DWELL_SECONDS=7*24*60*60
RECOVERY_MIN_NEW_EFFECTIVE_SAMPLES=2.0
TRANSITION_POLICY_VERSION=2
TRANSITION_POLICY={
    "UNOBSERVED":{
        "EXPERIMENTAL":{"allowed":True,"severity":"info","required_gates":[]},
        "TRUSTED":{"allowed":True,"severity":"info","required_gates":[]},
        "DEGRADED":{"allowed":True,"severity":"warning","required_gates":["degraded_replacement_revalidated"]},
        "QUARANTINED":{"allowed":True,"severity":"critical","required_gates":["quarantined_replacement_revalidated"]},
    },
    "EXPERIMENTAL":{
        "TRUSTED":{"allowed":True,"severity":"info","required_gates":[]},
        "DEGRADED":{"allowed":True,"severity":"warning","required_gates":["degraded_replacement_revalidated"]},
        "QUARANTINED":{"allowed":True,"severity":"critical","required_gates":["quarantined_replacement_revalidated"]},
    },
    "TRUSTED":{
        "DEGRADED":{"allowed":True,"severity":"warning","required_gates":["degraded_replacement_revalidated"]},
        "QUARANTINED":{"allowed":True,"severity":"critical","required_gates":["quarantined_replacement_revalidated"]},
    },
    "DEGRADED":{
        "QUARANTINED":{"allowed":True,"severity":"critical","required_gates":["quarantined_replacement_revalidated"]},
        "RECOVERING":{
            "allowed":True,"severity":"warning",
            "minimum_dwell_seconds":RECOVERY_MIN_DWELL_SECONDS,
            "minimum_new_effective_samples":RECOVERY_MIN_NEW_EFFECTIVE_SAMPLES,
            "minimum_confirmations":RECOVERY_CONFIRMATIONS_REQUIRED,
            "required_gates":["recovering_replacement_revalidated","replacement_reputation_transition_completed"],
        },
    },
    "QUARANTINED":{
        "RECOVERING":{
            "allowed":True,"severity":"critical",
            "minimum_dwell_seconds":RECOVERY_MIN_DWELL_SECONDS,
            "minimum_new_effective_samples":RECOVERY_MIN_NEW_EFFECTIVE_SAMPLES,
            "minimum_confirmations":RECOVERY_CONFIRMATIONS_REQUIRED,
            "required_gates":["recovering_replacement_revalidated","replacement_reputation_transition_completed"],
        },
    },
    "RECOVERING":{
        "TRUSTED":{
            "allowed":True,"severity":"warning",
            "minimum_dwell_seconds":RECOVERY_MIN_DWELL_SECONDS,
            "minimum_new_effective_samples":RECOVERY_MIN_NEW_EFFECTIVE_SAMPLES,
            "minimum_confirmations":RECOVERY_CONFIRMATIONS_REQUIRED,
            "required_gates":["replacement_reputation_transition_completed"],
        },
        "DEGRADED":{"allowed":True,"severity":"warning","required_gates":["degraded_replacement_revalidated"]},
        "QUARANTINED":{"allowed":True,"severity":"critical","required_gates":["quarantined_replacement_revalidated"]},
    },
}

REPUTATION_STATES={"UNOBSERVED","EXPERIMENTAL","TRUSTED","DEGRADED","QUARANTINED","RECOVERING"}
DANGEROUS_STATES={"DEGRADED","QUARANTINED","RECOVERING"}
DANGEROUS_STATE_GATES={
    "DEGRADED":"degraded_replacement_revalidated",
    "QUARANTINED":"quarantined_replacement_revalidated",
    "RECOVERING":"recovering_replacement_revalidated",
}

def transition_policy_digest(policy: dict | None=None) -> str:
    policy=TRANSITION_POLICY if policy is None else policy
    payload={
        "version":TRANSITION_POLICY_VERSION,
        "policy":policy,
    }
    return hashlib.sha256(
        json.dumps(payload,sort_keys=True,separators=(",",":")).encode("utf-8")
    ).hexdigest()

def validate_transition_policy(policy: dict | None=None) -> dict:
    policy=TRANSITION_POLICY if policy is None else policy
    errors=[]
    warnings=[]
    if not isinstance(policy,dict):
        return {"valid":False,"errors":["policy_not_mapping"],"warnings":[]}

    unknown_sources=sorted(set(policy)-REPUTATION_STATES)
    if unknown_sources:
        errors.append("unknown_source_states:"+",".join(unknown_sources))

    adjacency={state:set() for state in REPUTATION_STATES}
    for source,row in policy.items():
        if source not in REPUTATION_STATES or not isinstance(row,dict):
            if source in REPUTATION_STATES and not isinstance(row,dict):
                errors.append(f"transition_row_not_mapping:{source}")
            continue
        for target,rule in row.items():
            if target not in REPUTATION_STATES:
                errors.append(f"unknown_target_state:{source}->{target}")
                continue
            if not isinstance(rule,dict):
                errors.append(f"transition_rule_not_mapping:{source}->{target}")
                continue
            if rule.get("allowed") is not True:
                continue
            adjacency[source].add(target)
            gates=rule.get("required_gates",[])
            if not isinstance(gates,list) or any(not isinstance(g,str) or not g for g in gates):
                errors.append(f"invalid_required_gates:{source}->{target}")
                gates=[]
            required=DANGEROUS_STATE_GATES.get(target)
            if required and required not in gates:
                errors.append(f"dangerous_state_missing_gate:{source}->{target}:{required}")
            if source in {"DEGRADED","QUARANTINED"} and target=="TRUSTED":
                errors.append(f"unsafe_direct_promotion:{source}->TRUSTED")
            if source=="RECOVERING" and target=="TRUSTED":
                if int(rule.get("minimum_dwell_seconds",0) or 0)<=0:
                    errors.append("recovering_trusted_missing_dwell")
                if float(rule.get("minimum_new_effective_samples",0.0) or 0.0)<=0:
                    errors.append("recovering_trusted_missing_new_evidence")
                if int(rule.get("minimum_confirmations",0) or 0)<2:
                    errors.append("recovering_trusted_missing_confirmations")

    # Reachability catches dead states and accidental policy partitions.
    reachable={"UNOBSERVED"}
    frontier=["UNOBSERVED"]
    while frontier:
        source=frontier.pop()
        for target in adjacency.get(source,set()):
            if target not in reachable:
                reachable.add(target)
                frontier.append(target)
    unreachable=sorted(REPUTATION_STATES-reachable)
    if unreachable:
        errors.append("unreachable_states:"+",".join(unreachable))

    # Every dangerous state must have a defined escape/recovery route.
    for state in DANGEROUS_STATES:
        if not adjacency.get(state):
            errors.append(f"dead_end_dangerous_state:{state}")

    # There must be no path from a degraded/quarantined state to TRUSTED
    # that bypasses RECOVERING.
    for origin in ("DEGRADED","QUARANTINED"):
        frontier=[(origin,frozenset({origin}))]
        while frontier:
            source,seen=frontier.pop()
            for target in adjacency.get(source,set()):
                if target=="TRUSTED":
                    errors.append(f"promotion_path_bypasses_recovering:{origin}")
                    frontier=[]
                    break
                if target=="RECOVERING" or target in seen:
                    continue
                frontier.append((target,seen|{target}))

    return {
        "valid":not errors,
        "errors":sorted(set(errors)),
        "warnings":sorted(set(warnings)),
        "states":sorted(REPUTATION_STATES),
        "reachable_states":sorted(reachable),
        "policy_version":TRANSITION_POLICY_VERSION,
        "policy_digest":transition_policy_digest(policy),
    }

def assert_transition_policy_valid(policy: dict | None=None) -> None:
    validation=validate_transition_policy(policy)
    if not validation["valid"]:
        raise ValueError("invalid replacement reputation transition policy: "+"; ".join(validation["errors"]))

def transition_policy(previous: str | None, target: str) -> dict:
    previous=previous if isinstance(previous,str) else "UNOBSERVED"
    if previous==target:
        return {
            "allowed":True,
            "severity":"info",
            "minimum_dwell_seconds":0,
            "minimum_new_effective_samples":0.0,
            "minimum_confirmations":0,
            "required_gates":[],
        }
    row=TRANSITION_POLICY.get(previous,{})
    rule=row.get(target) if isinstance(row,dict) else None
    if not isinstance(rule,dict):
        return {
            "allowed":False,
            "severity":"critical",
            "minimum_dwell_seconds":0,
            "minimum_new_effective_samples":0.0,
            "minimum_confirmations":0,
            "required_gates":["replacement_reputation_transition_reviewed"],
        }
    return {
        "allowed":rule.get("allowed") is True,
        "severity":rule.get("severity","warning"),
        "minimum_dwell_seconds":int(rule.get("minimum_dwell_seconds",0) or 0),
        "minimum_new_effective_samples":float(rule.get("minimum_new_effective_samples",0.0) or 0.0),
        "minimum_confirmations":int(rule.get("minimum_confirmations",0) or 0),
        "required_gates":list(rule.get("required_gates",[])),
    }

def _identity(context: dict) -> str:
    payload={
        "current_repo":context.get("current_repo"),
        "replacement_repo":context.get("replacement_repo"),
        "framework":context.get("framework"),
        "project_type":context.get("project_type"),
        "primary_domain":context.get("primary_domain"),
        "platform":context.get("platform"),
        "current_major_version":context.get("current_major_version"),
        "replacement_major_version":context.get("replacement_major_version"),
    }
    return hashlib.sha256(
        json.dumps(payload,sort_keys=True,separators=(",",":")).encode("utf-8")
    ).hexdigest()

def desired_state(evidence: dict | None) -> dict:
    if not isinstance(evidence,dict):
        return {"state":"UNOBSERVED","reason":"no_historical_evidence"}

    samples=max(0,int(evidence.get("effective_samples",evidence.get("samples",0)) or 0))
    confidence=float(evidence.get("evidence_confidence",0.0) or 0.0)
    wilson=float(evidence.get("wilson_lower_95",0.0) or 0.0)
    regression=float(evidence.get("regression_rate",0.0) or 0.0)

    sequential=evidence.get("sequential_drift")
    sequential_detected=(
        sequential is True
        or (isinstance(sequential,dict) and sequential.get("drift_detected") is True)
    )
    recovery_detected=(
        evidence.get("recovery_candidate") is True
        or (isinstance(sequential,dict) and sequential.get("recovery_detected") is True)
    )
    if sequential_detected or evidence.get("regime_shift") is True:
        return {"state":"QUARANTINED","reason":"active_performance_deterioration"}
    if evidence.get("evidence_conflict") is True:
        return {"state":"DEGRADED","reason":"conflicting_historical_evidence"}
    if recovery_detected:
        return {"state":"RECOVERING","reason":"sustained_recent_recovery"}
    if evidence.get("stale_evidence") is True:
        return {"state":"DEGRADED","reason":"stale_historical_evidence"}
    if samples<5 or confidence<0.25:
        return {"state":"EXPERIMENTAL","reason":"insufficient_effective_evidence"}
    if wilson>=0.70 and regression<=0.10 and confidence>=0.50:
        return {"state":"TRUSTED","reason":"strong_consistent_historical_evidence"}
    if wilson<0.50 or regression>=0.25:
        return {"state":"DEGRADED","reason":"weak_or_regressive_historical_evidence"}
    return {"state":"EXPERIMENTAL","reason":"mixed_or_maturing_evidence"}

def _effective_samples(evidence: dict | None) -> float:
    if not isinstance(evidence,dict):
        return 0.0
    value=evidence.get("effective_samples",evidence.get("samples",0))
    try:
        return max(0.0,float(value or 0.0))
    except (TypeError,ValueError):
        return 0.0

def _transition(
    previous_entry: dict,
    desired: str,
    evidence: dict | None,
    now: float,
) -> tuple[str,int,str,dict]:
    previous=previous_entry.get("state") if isinstance(previous_entry.get("state"),str) else "UNOBSERVED"
    confirmations=int(previous_entry.get("recovery_confirmations",0) or 0)
    current_samples=_effective_samples(evidence)
    state_since=float(previous_entry.get("state_since",previous_entry.get("updated_at",now)) or now)
    recovery_started_at=previous_entry.get("recovery_started_at")
    recovery_start_samples=previous_entry.get("recovery_start_effective_samples")

    meta={
        "transition_pending":False,
        "state_since":state_since if previous!="UNOBSERVED" else now,
        "recovery_started_at":recovery_started_at,
        "recovery_start_effective_samples":recovery_start_samples,
        "new_effective_samples_since_recovery":0.0,
        "eligible_at":None,
    }

    # Downward safety transitions are intentionally fast.
    if desired=="QUARANTINED":
        meta["state_since"]=now if previous!="QUARANTINED" else state_since
        meta["recovery_started_at"]=None
        meta["recovery_start_effective_samples"]=None
        return "QUARANTINED",0,"immediate_safety_quarantine",meta
    if previous=="TRUSTED" and desired in {"DEGRADED","EXPERIMENTAL"}:
        meta["state_since"]=now
        meta["recovery_started_at"]=None
        meta["recovery_start_effective_samples"]=None
        reason="trusted_degraded" if desired=="DEGRADED" else "trusted_evidence_weakened"
        return "DEGRADED",0,reason,meta

    # A degraded or quarantined replacement can only climb through RECOVERING.
    if previous in {"QUARANTINED","DEGRADED"} and desired in {"TRUSTED","RECOVERING"}:
        started=now
        meta.update({
            "state_since":now,
            "recovery_started_at":started,
            "recovery_start_effective_samples":current_samples,
            "new_effective_samples_since_recovery":0.0,
            "eligible_at":started+RECOVERY_MIN_DWELL_SECONDS,
            "transition_pending":True,
        })
        return "RECOVERING",1,"recovery_started",meta

    if previous=="RECOVERING":
        started=float(recovery_started_at) if isinstance(recovery_started_at,(int,float)) else state_since
        start_samples=float(recovery_start_samples) if isinstance(recovery_start_samples,(int,float)) else current_samples
        new_samples=max(0.0,current_samples-start_samples)
        meta.update({
            "state_since":state_since,
            "recovery_started_at":started,
            "recovery_start_effective_samples":start_samples,
            "new_effective_samples_since_recovery":round(new_samples,3),
            "eligible_at":started+RECOVERY_MIN_DWELL_SECONDS,
        })

        if desired=="QUARANTINED":
            meta["state_since"]=now
            meta["recovery_started_at"]=None
            meta["recovery_start_effective_samples"]=None
            return "QUARANTINED",0,"recovery_failed_quarantine",meta
        if desired=="DEGRADED":
            meta["state_since"]=now
            meta["recovery_started_at"]=None
            meta["recovery_start_effective_samples"]=None
            return "DEGRADED",0,"recovery_failed",meta
        if desired in {"TRUSTED","RECOVERING"}:
            confirmations+=1
            dwell_ok=(now-started)>=RECOVERY_MIN_DWELL_SECONDS
            samples_ok=new_samples>=RECOVERY_MIN_NEW_EFFECTIVE_SAMPLES
            confirmations_ok=confirmations>=RECOVERY_CONFIRMATIONS_REQUIRED
            if desired=="TRUSTED" and dwell_ok and samples_ok and confirmations_ok:
                meta.update({
                    "state_since":now,
                    "transition_pending":False,
                    "recovery_started_at":None,
                    "recovery_start_effective_samples":None,
                    "eligible_at":None,
                })
                return "TRUSTED",0,"recovery_confirmed",meta
            meta["transition_pending"]=True
            if not dwell_ok:
                reason="recovery_minimum_dwell_pending"
            elif not samples_ok:
                reason="recovery_new_evidence_pending"
            elif not confirmations_ok:
                reason="recovery_confirmation_pending"
            else:
                reason="recovery_ongoing"
            return "RECOVERING",confirmations,reason,meta

    # Bootstrap and non-recovery transitions use the current evidence directly.
    meta["state_since"]=now if previous!=desired else state_since
    meta["transition_pending"]=False
    return desired,0,"desired_state_applied",meta

def apply(registry: dict | None, context: dict, evidence: dict | None, *, now: float | None=None) -> tuple[dict,dict]:
    assert_transition_policy_valid()
    now=float(now) if isinstance(now,(int,float)) else time.time()
    registry=registry if isinstance(registry,dict) else {}
    entries=registry.get("entries") if isinstance(registry.get("entries"),dict) else {}
    audit=registry.get("audit") if isinstance(registry.get("audit"),list) else []
    key=_identity(context)
    previous_entry=entries.get(key) if isinstance(entries.get(key),dict) else {}
    previous_state=previous_entry.get("state") if isinstance(previous_entry.get("state"),str) else "UNOBSERVED"
    desired=desired_state(evidence)
    requested_rule=transition_policy(previous_state,desired["state"])
    new_state,new_confirmations,transition_reason,transition_meta=_transition(
        previous_entry,desired["state"],evidence,now
    )
    applied_rule=transition_policy(previous_state,new_state)
    if not applied_rule["allowed"]:
        new_state=previous_state
        new_confirmations=int(previous_entry.get("recovery_confirmations",0) or 0)
        transition_reason="transition_blocked_by_policy"
        transition_meta["transition_pending"]=True
        transition_meta["state_since"]=previous_entry.get("state_since",previous_entry.get("updated_at",now))
        applied_rule=transition_policy(previous_state,new_state)

    entry={
        "identity":key,
        **{field:context.get(field) for field in (
            "current_repo","replacement_repo","framework","project_type","primary_domain",
            "platform","current_major_version","replacement_major_version"
        )},
        "state":new_state,
        "desired_state":desired["state"],
        "reason":desired["reason"],
        "transition_reason":transition_reason,
        "transition_policy_version":TRANSITION_POLICY_VERSION,
        "transition_policy_digest":transition_policy_digest(),
        "transition_rule":applied_rule,
        "requested_transition_rule":requested_rule,
        "required_transition_gates":applied_rule.get("required_gates",[]),
        "recovery_confirmations":new_confirmations,
        "state_since":transition_meta.get("state_since",now),
        "recovery_started_at":transition_meta.get("recovery_started_at"),
        "recovery_start_effective_samples":transition_meta.get("recovery_start_effective_samples"),
        "new_effective_samples_since_recovery":transition_meta.get("new_effective_samples_since_recovery",0.0),
        "transition_pending":transition_meta.get("transition_pending") is True,
        "eligible_at":transition_meta.get("eligible_at"),
        "updated_at":now,
        "promotion_eligible":new_state=="TRUSTED" and transition_meta.get("transition_pending") is not True,
        "requires_revalidation":new_state in {"DEGRADED","QUARANTINED","RECOVERING"},
    }
    if evidence:
        entry["metrics"]={
            "effective_samples":evidence.get("effective_samples",evidence.get("samples")),
            "evidence_confidence":evidence.get("evidence_confidence"),
            "wilson_lower_95":evidence.get("wilson_lower_95"),
            "regression_rate":evidence.get("regression_rate"),
            "sequential_drift":evidence.get("sequential_drift"),
            "regime_shift":evidence.get("regime_shift"),
            "recovery_candidate":evidence.get("recovery_candidate"),
            "stale_evidence":evidence.get("stale_evidence"),
        }

    event={
        "identity":key,
        "observed_at":now,
        "previous_state":previous_state,
        "desired_state":desired["state"],
        "new_state":new_state,
        "transition_reason":transition_reason,
        "reason":desired["reason"],
        "transition_policy_version":TRANSITION_POLICY_VERSION,
        "transition_policy_digest":transition_policy_digest(),
        "transition_rule":applied_rule,
        "transition_pending":transition_meta.get("transition_pending") is True,
        "eligible_at":transition_meta.get("eligible_at"),
        "effective_samples":_effective_samples(evidence),
    }
    entries=dict(entries)
    entries[key]=entry
    audit=(audit+[event])[-MAX_AUDIT_EVENTS:]
    updated={
        "version":REGISTRY_VERSION,
        "updated_at":now,
        "entries":entries,
        "audit":audit,
        "policy":{
            "version":TRANSITION_POLICY_VERSION,
            "digest":transition_policy_digest(),
            "transition_matrix":TRANSITION_POLICY,
            "recovery_confirmations_required":RECOVERY_CONFIRMATIONS_REQUIRED,
            "recovery_min_dwell_seconds":RECOVERY_MIN_DWELL_SECONDS,
            "recovery_min_new_effective_samples":RECOVERY_MIN_NEW_EFFECTIVE_SAMPLES,
            "fast_downward_transitions":True,
            "slow_upward_recovery":True,
            "upward_transition_requires_time_and_new_evidence":True,
            "validation":validate_transition_policy(),
        },
    }
    return updated,entry

def load(path: Path) -> dict:
    if not path.is_file():
        return {"version":REGISTRY_VERSION,"entries":{},"audit":[]}
    try:
        value=json.loads(path.read_text(encoding="utf-8"))
    except (OSError,UnicodeError,json.JSONDecodeError):
        return {"version":REGISTRY_VERSION,"entries":{},"audit":[]}
    return value if isinstance(value,dict) else {"version":REGISTRY_VERSION,"entries":{},"audit":[]}

def update(path: Path, context: dict, evidence: dict | None, *, now: float | None=None) -> dict:
    registry,entry=apply(load(path),context,evidence,now=now)
    atomic_write_text(
        path,
        json.dumps(registry,ensure_ascii=False,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    return entry

def lookup(registry: dict | None, context: dict) -> dict | None:
    if not isinstance(registry,dict):
        return None
    entries=registry.get("entries")
    if not isinstance(entries,dict):
        return None
    value=entries.get(_identity(context))
    return value if isinstance(value,dict) else None
