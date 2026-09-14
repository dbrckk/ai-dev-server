"""Persistent reputation registry with audited hysteretic state transitions."""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

from atomic_file import write_text as atomic_write_text

REGISTRY_VERSION=1
MAX_AUDIT_EVENTS=500
RECOVERY_CONFIRMATIONS_REQUIRED=2

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

    if evidence.get("sequential_drift") is True or evidence.get("regime_shift") is True:
        return {"state":"QUARANTINED","reason":"active_performance_deterioration"}
    if evidence.get("evidence_conflict") is True:
        return {"state":"DEGRADED","reason":"conflicting_historical_evidence"}
    if evidence.get("recovery_candidate") is True:
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

def _transition(previous: str | None, desired: str, confirmations: int) -> tuple[str,int,str]:
    previous=previous or "UNOBSERVED"

    # Downward safety transitions happen immediately.
    if desired=="QUARANTINED":
        return "QUARANTINED",0,"immediate_safety_quarantine"
    if previous=="TRUSTED" and desired=="DEGRADED":
        return "DEGRADED",0,"trusted_degraded"
    if previous=="TRUSTED" and desired=="EXPERIMENTAL":
        return "DEGRADED",0,"trusted_evidence_weakened"

    # Recovery is deliberately slower than degradation.
    if previous in {"QUARANTINED","DEGRADED"} and desired=="TRUSTED":
        return "RECOVERING",1,"trusted_candidate_requires_recovery_confirmation"
    if previous in {"QUARANTINED","DEGRADED"} and desired=="RECOVERING":
        return "RECOVERING",max(1,confirmations),"recovery_started"
    if previous=="RECOVERING":
        if desired=="QUARANTINED":
            return "QUARANTINED",0,"recovery_failed_quarantine"
        if desired=="DEGRADED":
            return "DEGRADED",0,"recovery_failed"
        if desired=="TRUSTED":
            confirmations+=1
            if confirmations>=RECOVERY_CONFIRMATIONS_REQUIRED:
                return "TRUSTED",0,"recovery_confirmed"
            return "RECOVERING",confirmations,"recovery_confirmation_pending"
        if desired=="RECOVERING":
            return "RECOVERING",max(1,confirmations),"recovery_ongoing"

    return desired,0,"desired_state_applied"

def apply(registry: dict | None, context: dict, evidence: dict | None, *, now: float | None=None) -> tuple[dict,dict]:
    now=float(now) if isinstance(now,(int,float)) else time.time()
    registry=registry if isinstance(registry,dict) else {}
    entries=registry.get("entries") if isinstance(registry.get("entries"),dict) else {}
    audit=registry.get("audit") if isinstance(registry.get("audit"),list) else []
    key=_identity(context)
    previous_entry=entries.get(key) if isinstance(entries.get(key),dict) else {}
    previous_state=previous_entry.get("state") if isinstance(previous_entry.get("state"),str) else "UNOBSERVED"
    confirmations=int(previous_entry.get("recovery_confirmations",0) or 0)

    desired=desired_state(evidence)
    new_state,new_confirmations,transition_reason=_transition(
        previous_state,desired["state"],confirmations
    )

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
        "recovery_confirmations":new_confirmations,
        "updated_at":now,
        "promotion_eligible":new_state=="TRUSTED",
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
            "recovery_confirmations_required":RECOVERY_CONFIRMATIONS_REQUIRED,
            "fast_downward_transitions":True,
            "slow_upward_recovery":True,
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
