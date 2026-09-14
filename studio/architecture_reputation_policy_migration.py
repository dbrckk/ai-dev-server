"""Dry-run and explicitly authorized migration of persisted replacement reputation policy.

Policy migrations never silently promote a replacement. A dry-run computes the exact
registry diff under the current canonical reputation engine/policy. Applying the migration
requires an authorization record bound to the source-registry digest and migration plan.
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

from atomic_file import write_text as atomic_write_text
from architecture_replacement_reputation import (
    MAX_AUDIT_EVENTS,
    REGISTRY_VERSION,
    TRANSITION_POLICY,
    TRANSITION_POLICY_VERSION,
    desired_state,
    transition_policy,
    transition_policy_digest,
    validate_transition_policy,
)

MIGRATION_VERSION=1

class ReputationPolicyMigrationError(RuntimeError):
    pass

_CONTEXT_FIELDS=(
    "current_repo","replacement_repo","framework","project_type","primary_domain",
    "platform","current_major_version","replacement_major_version",
)

def _canonical(value) -> str:
    return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False)

def registry_digest(registry: dict) -> str:
    if not isinstance(registry,dict):
        raise ReputationPolicyMigrationError("registry malformed")
    return hashlib.sha256(_canonical(registry).encode("utf-8")).hexdigest()

def _entry_context(entry: dict) -> dict:
    return {field:entry.get(field) for field in _CONTEXT_FIELDS}

def _learning_index(learning: dict | None) -> dict[tuple,dict]:
    rows=learning.get("rankings") if isinstance(learning,dict) else None
    out={}
    if not isinstance(rows,list):
        return out
    for row in rows:
        if not isinstance(row,dict):
            continue
        key=tuple(row.get(field) for field in _CONTEXT_FIELDS)
        current=out.get(key)
        if current is None or float(row.get("evidence_confidence",0.0) or 0.0)>float(current.get("evidence_confidence",0.0) or 0.0):
            out[key]=row
    return out

def _evidence_for(entry: dict, learning_index: dict[tuple,dict]) -> dict | None:
    key=tuple(entry.get(field) for field in _CONTEXT_FIELDS)
    row=learning_index.get(key)
    if isinstance(row,dict):
        return row
    metrics=entry.get("metrics")
    if isinstance(metrics,dict) and metrics:
        return dict(metrics)
    return None

def _migrated_state(previous: str, desired: str) -> tuple[str,str,bool]:
    # Policy migration itself is never a source of upward trust.
    if desired=="QUARANTINED":
        return "QUARANTINED","policy_migration_quarantine",False
    if desired=="DEGRADED":
        if previous=="QUARANTINED":
            return "QUARANTINED","policy_migration_preserve_stricter_state",False
        return "DEGRADED","policy_migration_degraded",False
    if desired in {"UNOBSERVED","EXPERIMENTAL"}:
        if previous=="TRUSTED":
            return "DEGRADED","policy_migration_evidence_weakened",False
        if previous in {"QUARANTINED","DEGRADED","RECOVERING"}:
            return previous,"policy_migration_preserve_nontrusted_state",False
        return desired,"policy_migration_nontrusted",False
    if desired=="RECOVERING":
        if previous=="QUARANTINED":
            return "QUARANTINED","policy_migration_preserve_quarantine",False
        return "RECOVERING","policy_migration_recovery_required",False
    if desired=="TRUSTED":
        if previous=="TRUSTED":
            return "TRUSTED","policy_migration_trust_revalidated",True
        # Any non-trusted state must re-enter normal recovery flow later.
        return previous,"policy_migration_no_upward_promotion",False
    raise ReputationPolicyMigrationError("unknown desired reputation state")

def dry_run(registry: dict, learning: dict | None=None, *, now: float | None=None) -> dict:
    validation=validate_transition_policy()
    if validation.get("valid") is not True:
        raise ReputationPolicyMigrationError("current transition policy invalid")
    if not isinstance(registry,dict):
        raise ReputationPolicyMigrationError("registry malformed")
    entries=registry.get("entries")
    if not isinstance(entries,dict):
        raise ReputationPolicyMigrationError("registry entries malformed")

    now=float(now) if isinstance(now,(int,float)) else time.time()
    source_digest=registry_digest(registry)
    target_policy_digest=transition_policy_digest()
    index=_learning_index(learning)

    changes=[]
    unchanged=0
    downgrades=0
    preserved_nontrusted=0
    trusted_revalidated=0
    for identity,entry in sorted(entries.items()):
        if not isinstance(entry,dict):
            raise ReputationPolicyMigrationError("registry entry malformed")
        previous=entry.get("state") if isinstance(entry.get("state"),str) else "UNOBSERVED"
        evidence=_evidence_for(entry,index)
        desired=desired_state(evidence)
        target_state,reason,promotion_eligible=_migrated_state(previous,desired["state"])
        changed=(
            target_state!=previous
            or entry.get("transition_policy_version")!=TRANSITION_POLICY_VERSION
            or entry.get("transition_policy_digest")!=target_policy_digest
        )
        if not changed:
            unchanged+=1
        if target_state in {"DEGRADED","QUARANTINED"} and previous=="TRUSTED":
            downgrades+=1
        if previous in {"DEGRADED","QUARANTINED","RECOVERING"} and target_state==previous:
            preserved_nontrusted+=1
        if previous=="TRUSTED" and target_state=="TRUSTED":
            trusted_revalidated+=1

        changes.append({
            "identity":identity,
            "context":_entry_context(entry),
            "previous_state":previous,
            "desired_state":desired["state"],
            "target_state":target_state,
            "reason":reason,
            "desired_reason":desired.get("reason"),
            "changed":changed,
            "promotion_eligible_after_migration":promotion_eligible,
            "requires_revalidation_after_migration":target_state in {"DEGRADED","QUARANTINED","RECOVERING"},
            "evidence_source":"learning" if tuple(entry.get(field) for field in _CONTEXT_FIELDS) in index else "entry_metrics",
        })

    core={
        "version":MIGRATION_VERSION,
        "status":"reputation_policy_migration_review_ready",
        "generated_at":now,
        "source_registry_version":registry.get("version"),
        "source_registry_digest":source_digest,
        "source_policy_version":registry.get("policy",{}).get("version") if isinstance(registry.get("policy"),dict) else None,
        "source_policy_digest":registry.get("policy",{}).get("digest") if isinstance(registry.get("policy"),dict) else None,
        "target_registry_version":REGISTRY_VERSION,
        "target_policy_version":TRANSITION_POLICY_VERSION,
        "target_policy_digest":target_policy_digest,
        "summary":{
            "entries":len(changes),
            "changed":sum(1 for row in changes if row["changed"]),
            "unchanged":unchanged,
            "trusted_downgrades":downgrades,
            "preserved_nontrusted":preserved_nontrusted,
            "trusted_revalidated":trusted_revalidated,
        },
        "changes":changes,
        "policy":{
            "dry_run_only":True,
            "automatic_apply":False,
            "never_promote_during_policy_migration":True,
            "explicit_authorization_required":True,
        },
    }
    migration_id=hashlib.sha256(_canonical(core).encode("utf-8")).hexdigest()
    return {
        **core,
        "migration_id":migration_id,
        "authorization_template":{
            "version":1,
            "status":"explicit_reputation_policy_migration_authorization",
            "migration_id":migration_id,
            "source_registry_digest":source_digest,
            "target_policy_digest":target_policy_digest,
            "authorized":False,
        },
    }

def apply_migration(registry: dict, plan: dict, authorization: dict, *, now: float | None=None) -> dict:
    if not isinstance(plan,dict) or plan.get("status")!="reputation_policy_migration_review_ready":
        raise ReputationPolicyMigrationError("migration plan invalid")
    if not isinstance(authorization,dict):
        raise ReputationPolicyMigrationError("migration authorization missing")
    if authorization.get("status")!="explicit_reputation_policy_migration_authorization" or authorization.get("authorized") is not True:
        raise ReputationPolicyMigrationError("explicit migration authorization absent")
    for key in ("migration_id","source_registry_digest","target_policy_digest"):
        if authorization.get(key)!=plan.get(key):
            raise ReputationPolicyMigrationError("migration authorization identity mismatch: "+key)

    current_digest=registry_digest(registry)
    if current_digest!=plan.get("source_registry_digest"):
        raise ReputationPolicyMigrationError("registry changed after migration review")
    if plan.get("target_policy_version")!=TRANSITION_POLICY_VERSION or plan.get("target_policy_digest")!=transition_policy_digest():
        raise ReputationPolicyMigrationError("target transition policy changed after review")

    now=float(now) if isinstance(now,(int,float)) else time.time()
    entries=registry.get("entries")
    audit=registry.get("audit") if isinstance(registry.get("audit"),list) else []
    if not isinstance(entries,dict):
        raise ReputationPolicyMigrationError("registry entries malformed")

    change_index={row.get("identity"):row for row in plan.get("changes",[]) if isinstance(row,dict)}
    migrated_entries={}
    migration_events=[]
    for identity,entry in entries.items():
        if not isinstance(entry,dict):
            raise ReputationPolicyMigrationError("registry entry malformed")
        row=change_index.get(identity)
        if not isinstance(row,dict):
            raise ReputationPolicyMigrationError("migration plan missing registry identity")
        target=row.get("target_state")
        if not isinstance(target,str):
            raise ReputationPolicyMigrationError("migration target state malformed")
        previous=entry.get("state") if isinstance(entry.get("state"),str) else "UNOBSERVED"
        rule=transition_policy(previous,target)
        updated=dict(entry)
        updated.update({
            "state":target,
            "desired_state":row.get("desired_state"),
            "reason":row.get("desired_reason"),
            "transition_reason":row.get("reason"),
            "transition_policy_version":TRANSITION_POLICY_VERSION,
            "transition_policy_digest":transition_policy_digest(),
            "transition_rule":rule,
            "requested_transition_rule":rule,
            "required_transition_gates":rule.get("required_gates",[]),
            "transition_pending":target in {"DEGRADED","QUARANTINED","RECOVERING"},
            "promotion_eligible":row.get("promotion_eligible_after_migration") is True,
            "requires_revalidation":row.get("requires_revalidation_after_migration") is True,
            "updated_at":now,
            "policy_migration_id":plan.get("migration_id"),
        })
        if target!="RECOVERING":
            updated["recovery_confirmations"]=0
            updated["recovery_started_at"]=None
            updated["recovery_start_effective_samples"]=None
            updated["new_effective_samples_since_recovery"]=0.0
            updated["eligible_at"]=None
        migrated_entries[identity]=updated
        migration_events.append({
            "identity":identity,
            "observed_at":now,
            "previous_state":previous,
            "desired_state":row.get("desired_state"),
            "new_state":target,
            "transition_reason":"policy_migration:"+str(row.get("reason")),
            "reason":row.get("desired_reason"),
            "transition_policy_version":TRANSITION_POLICY_VERSION,
            "transition_policy_digest":transition_policy_digest(),
            "policy_migration_id":plan.get("migration_id"),
            "migration_authorized":True,
        })

    migrated={
        **registry,
        "version":REGISTRY_VERSION,
        "updated_at":now,
        "entries":migrated_entries,
        "audit":(audit+migration_events)[-MAX_AUDIT_EVENTS:],
        "policy":{
            "version":TRANSITION_POLICY_VERSION,
            "digest":transition_policy_digest(),
            "transition_matrix":TRANSITION_POLICY,
            "validation":validate_transition_policy(),
        },
        "last_policy_migration":{
            "migration_id":plan.get("migration_id"),
            "applied_at":now,
            "source_registry_digest":plan.get("source_registry_digest"),
            "target_policy_digest":plan.get("target_policy_digest"),
            "entries":len(migrated_entries),
        },
    }
    return migrated

def write_dry_run(registry: dict, learning: dict | None, out: Path, *, now: float | None=None) -> dict:
    out.mkdir(parents=True,exist_ok=True)
    result=dry_run(registry,learning,now=now)
    atomic_write_text(
        out/"architecture-reputation-policy-migration-review.json",
        json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    return result

def write_applied(registry: dict, plan: dict, authorization: dict, path: Path, *, now: float | None=None) -> dict:
    migrated=apply_migration(registry,plan,authorization,now=now)
    atomic_write_text(
        path,
        json.dumps(migrated,ensure_ascii=False,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    return migrated
