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
from architecture_reputation_policy_approval import ApprovalProvenanceError, approval_from_github_attestation, consume as consume_approval, validate_approval, validate_github_attestation, validate_ledger
from architecture_replacement_reputation import (
    DANGEROUS_STATE_GATES,
    MAX_AUDIT_EVENTS,
    RECOVERY_CONFIRMATIONS_REQUIRED,
    RECOVERY_MIN_DWELL_SECONDS,
    RECOVERY_MIN_NEW_EFFECTIVE_SAMPLES,
    REGISTRY_VERSION,
    TRANSITION_POLICY,
    TRANSITION_POLICY_VERSION,
    desired_state,
    transition_policy,
    transition_policy_digest,
    validate_transition_policy,
)

MIGRATION_VERSION=3
AUTHORIZATION_VERSION=2
AUTHORIZATION_TTL_SECONDS=24*60*60
RISK_LEVELS=("NO_IMPACT","SAFE_STRICTER","BEHAVIOR_CHANGE","TRUST_DOWNGRADE","PROMOTION_PATH_CHANGE","CRITICAL")
_REINFORCED_RISKS={"PROMOTION_PATH_CHANGE","CRITICAL"}

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

def _rule_snapshot(rule: dict | None) -> dict:
    if not isinstance(rule,dict):
        return {
            "allowed":False,
            "severity":"critical",
            "minimum_dwell_seconds":0,
            "minimum_new_effective_samples":0.0,
            "minimum_confirmations":0,
            "required_gates":[],
        }
    return {
        "allowed":rule.get("allowed") is True,
        "severity":str(rule.get("severity","warning")),
        "minimum_dwell_seconds":int(rule.get("minimum_dwell_seconds",0) or 0),
        "minimum_new_effective_samples":float(rule.get("minimum_new_effective_samples",0.0) or 0.0),
        "minimum_confirmations":int(rule.get("minimum_confirmations",0) or 0),
        "required_gates":sorted(set(
            gate for gate in rule.get("required_gates",[])
            if isinstance(gate,str) and gate
        )),
    }

def _policy_edges(policy: dict | None) -> dict[tuple[str,str],dict]:
    if not isinstance(policy,dict):
        return {}
    out={}
    for source,row in policy.items():
        if not isinstance(source,str) or not isinstance(row,dict):
            continue
        for target,rule in row.items():
            if isinstance(target,str) and isinstance(rule,dict):
                out[(source,target)]=_rule_snapshot(rule)
    return out

def _is_stricter_or_equal(old: dict, new: dict) -> bool:
    if old["allowed"] is False and new["allowed"] is True:
        return False
    if old["allowed"] is True and new["allowed"] is False:
        return True
    if not old["allowed"] and not new["allowed"]:
        return True
    severity_rank={"info":0,"warning":1,"critical":2}
    if severity_rank.get(new["severity"],1)<severity_rank.get(old["severity"],1):
        return False
    if new["minimum_dwell_seconds"]<old["minimum_dwell_seconds"]:
        return False
    if new["minimum_new_effective_samples"]<old["minimum_new_effective_samples"]:
        return False
    if new["minimum_confirmations"]<old["minimum_confirmations"]:
        return False
    if not set(old["required_gates"]).issubset(set(new["required_gates"])):
        return False
    return True

def classify_migration_risk(registry: dict, changes: list[dict]) -> dict:
    if not isinstance(registry,dict) or not isinstance(changes,list):
        raise ReputationPolicyMigrationError("risk classifier inputs malformed")

    source_policy=registry.get("policy") if isinstance(registry.get("policy"),dict) else {}
    source_matrix=source_policy.get("transition_matrix") if isinstance(source_policy.get("transition_matrix"),dict) else {}
    old_edges=_policy_edges(source_matrix)
    new_edges=_policy_edges(TRANSITION_POLICY)
    all_edges=sorted(set(old_edges)|set(new_edges))

    changed_edges=[]
    promotion_path_changes=[]
    only_stricter=True
    for edge in all_edges:
        old=old_edges.get(edge,_rule_snapshot(None))
        new=new_edges.get(edge,_rule_snapshot(None))
        if old==new:
            continue
        source,target=edge
        stricter=_is_stricter_or_equal(old,new)
        only_stricter=only_stricter and stricter
        row={
            "source":source,
            "target":target,
            "old":old,
            "new":new,
            "stricter_or_equal":stricter,
        }
        changed_edges.append(row)
        if target=="TRUSTED" or source in {"DEGRADED","QUARANTINED","RECOVERING"}:
            promotion_path_changes.append(row)

    changed_rows=[row for row in changes if isinstance(row,dict) and row.get("changed") is True]
    trusted_downgrades=[
        row for row in changed_rows
        if row.get("previous_state")=="TRUSTED"
        and row.get("target_state") in {"DEGRADED","QUARANTINED","RECOVERING","EXPERIMENTAL","UNOBSERVED"}
    ]

    source_validation=source_policy.get("validation") if isinstance(source_policy.get("validation"),dict) else None
    source_known_invalid=isinstance(source_validation,dict) and source_validation.get("valid") is False

    if source_known_invalid:
        level="CRITICAL"
        reason="source_policy_was_invalid"
    elif promotion_path_changes:
        level="PROMOTION_PATH_CHANGE"
        reason="transition_path_to_or_from_recovery_changed"
    elif trusted_downgrades:
        level="TRUST_DOWNGRADE"
        reason="one_or_more_trusted_entries_downgrade"
    elif changed_edges and only_stricter and not changed_rows:
        level="SAFE_STRICTER"
        reason="policy_only_became_stricter_without_state_changes"
    elif changed_edges or changed_rows:
        level="BEHAVIOR_CHANGE"
        reason="policy_or_reputation_behavior_changes"
    else:
        level="NO_IMPACT"
        reason="no_effective_policy_or_state_change"

    return {
        "level":level,
        "reason":reason,
        "reinforced_review_required":level in _REINFORCED_RISKS,
        "changed_transition_edges":changed_edges,
        "promotion_path_changes":promotion_path_changes,
        "trusted_downgrades":len(trusted_downgrades),
        "changed_entries":len(changed_rows),
        "policy_only_stricter":bool(changed_edges) and only_stricter,
    }

def _format_seconds(value: int | float) -> str:
    seconds=max(0,int(value or 0))
    if seconds and seconds%86400==0:
        return f"{seconds//86400}d"
    if seconds and seconds%3600==0:
        return f"{seconds//3600}h"
    return f"{seconds}s"

def explain_migration(risk: dict, changes: list[dict]) -> dict:
    if not isinstance(risk,dict) or not isinstance(changes,list):
        raise ReputationPolicyMigrationError("migration explainer inputs malformed")
    edge_explanations=[]
    for row in risk.get("changed_transition_edges",[]):
        if not isinstance(row,dict):
            continue
        old=row.get("old") if isinstance(row.get("old"),dict) else {}
        new=row.get("new") if isinstance(row.get("new"),dict) else {}
        diffs=[]
        for field in ("allowed","severity","minimum_dwell_seconds","minimum_new_effective_samples","minimum_confirmations"):
            if old.get(field)==new.get(field):
                continue
            before=old.get(field); after=new.get(field)
            if field=="minimum_dwell_seconds":
                before=_format_seconds(before); after=_format_seconds(after)
            diffs.append({"field":field,"before":before,"after":after})
        old_gates=set(old.get("required_gates",[])); new_gates=set(new.get("required_gates",[]))
        for gate in sorted(new_gates-old_gates):
            diffs.append({"field":"required_gate","change":"added","value":gate})
        for gate in sorted(old_gates-new_gates):
            diffs.append({"field":"required_gate","change":"removed","value":gate})
        edge_explanations.append({
            "transition":f"{row.get('source')} -> {row.get('target')}",
            "stricter_or_equal":row.get("stricter_or_equal") is True,
            "changes":diffs,
        })

    state_counts={}
    affected=[]
    for row in changes:
        if not isinstance(row,dict) or row.get("changed") is not True:
            continue
        key=f"{row.get('previous_state')} -> {row.get('target_state')}"
        state_counts[key]=state_counts.get(key,0)+1
        affected.append({
            "identity":row.get("identity"),
            "transition":key,
            "reason":row.get("reason"),
            "evidence_source":row.get("evidence_source"),
        })

    review_action=(
        "reinforced_review_required"
        if risk.get("reinforced_review_required") is True
        else "explicit_authorization_required"
    )
    return {
        "risk_level":risk.get("level"),
        "risk_reason":risk.get("reason"),
        "review_action":review_action,
        "policy_changes":edge_explanations,
        "state_impact":{
            "changed_entries":len(affected),
            "transitions":[{"transition":key,"count":state_counts[key]} for key in sorted(state_counts)],
            "affected_entries":affected,
        },
        "summary":(
            f"{risk.get('level')}: {len(edge_explanations)} policy edge(s) changed; "
            f"{len(affected)} persisted reputation entr{'y' if len(affected)==1 else 'ies'} affected."
        ),
    }

def review_digest(plan: dict) -> str:
    if not isinstance(plan,dict):
        raise ReputationPolicyMigrationError("migration plan malformed")
    payload={
        "migration_id":plan.get("migration_id"),
        "risk":plan.get("risk"),
        "explanation":plan.get("explanation"),
        "summary":plan.get("summary"),
        "changes":plan.get("changes"),
    }
    return hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()

def authorization_template(plan: dict, *, now: float | None=None) -> dict:
    now=float(now) if isinstance(now,(int,float)) else time.time()
    risk=plan.get("risk") if isinstance(plan.get("risk"),dict) else {}
    return {
        "version":AUTHORIZATION_VERSION,
        "status":"explicit_reputation_policy_migration_authorization",
        "migration_id":plan.get("migration_id"),
        "source_registry_digest":plan.get("source_registry_digest"),
        "target_policy_digest":plan.get("target_policy_digest"),
        "review_digest":review_digest(plan),
        "risk_level":risk.get("level"),
        "reinforced_review_required":risk.get("reinforced_review_required") is True,
        "reinforced_reviewed":False,
        "issued_at":now,
        "expires_at":now+AUTHORIZATION_TTL_SECONDS,
        "authorized":False,
    }

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

    risk=classify_migration_risk(registry,changes)
    explanation=explain_migration(risk,changes)
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
        "risk":risk,
        "explanation":explanation,
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
            "reinforced_review_required":risk.get("reinforced_review_required") is True,
        },
    }
    migration_id=hashlib.sha256(_canonical(core).encode("utf-8")).hexdigest()
    result={**core,"migration_id":migration_id}
    result["review_digest"]=review_digest(result)
    result["authorization_template"]=authorization_template(result,now=now)
    return result

def bind_github_review_target(plan: dict, target: dict, *, now: float | None=None) -> dict:
    if not isinstance(plan,dict) or plan.get("status")!="reputation_policy_migration_review_ready":
        raise ReputationPolicyMigrationError("migration plan invalid")
    required=("repository","pull_request","commit_sha","head_ref","base_ref","author")
    if not isinstance(target,dict) or any(not target.get(key) for key in required):
        raise ReputationPolicyMigrationError("GitHub review target incomplete")
    if target.get("base_ref")!="main":
        raise ReputationPolicyMigrationError("GitHub review target base must be main")
    bound={
        **plan,
        "github_review_target":{key:target.get(key) for key in required},
    }
    bound.pop("authorization_template",None)
    bound.pop("review_digest",None)
    bound.pop("migration_id",None)
    # Re-bind the plan identity to the exact GitHub review target.
    migration_id=hashlib.sha256(_canonical(bound).encode("utf-8")).hexdigest()
    bound["migration_id"]=migration_id
    bound["review_digest"]=review_digest(bound)
    bound["authorization_template"]=authorization_template(
        bound,
        now=float(now) if isinstance(now,(int,float)) else time.time(),
    )
    return bound

def apply_migration(registry: dict, plan: dict, authorization: dict, *, approval: dict | None=None, github_attestation: dict | None=None, approval_ledger: dict | None=None, now: float | None=None) -> dict:
    if not isinstance(plan,dict) or plan.get("status")!="reputation_policy_migration_review_ready":
        raise ReputationPolicyMigrationError("migration plan invalid")
    if not isinstance(plan.get("github_review_target"),dict):
        raise ReputationPolicyMigrationError("migration plan is not bound to a GitHub review target")
    if not isinstance(authorization,dict):
        raise ReputationPolicyMigrationError("migration authorization missing")
    if authorization.get("version")!=AUTHORIZATION_VERSION:
        raise ReputationPolicyMigrationError("migration authorization version unsupported")
    if authorization.get("status")!="explicit_reputation_policy_migration_authorization" or authorization.get("authorized") is not True:
        raise ReputationPolicyMigrationError("explicit migration authorization absent")
    for key in ("migration_id","source_registry_digest","target_policy_digest"):
        if authorization.get(key)!=plan.get(key):
            raise ReputationPolicyMigrationError("migration authorization identity mismatch: "+key)
    expected_review_digest=review_digest(plan)
    if plan.get("review_digest")!=expected_review_digest or authorization.get("review_digest")!=expected_review_digest:
        raise ReputationPolicyMigrationError("migration review digest mismatch")
    risk=plan.get("risk") if isinstance(plan.get("risk"),dict) else {}
    if authorization.get("risk_level")!=risk.get("level"):
        raise ReputationPolicyMigrationError("migration authorization risk mismatch")
    if risk.get("reinforced_review_required") is True:
        if authorization.get("reinforced_reviewed") is not True:
            raise ReputationPolicyMigrationError("reinforced migration review absent")
    try:
        reinforced=risk.get("reinforced_review_required") is True
        github_provenance=validate_github_attestation(
            github_attestation,
            plan,
            reinforced=reinforced,
        )
        if approval is None:
            approval=approval_from_github_attestation(
                github_attestation,
                plan,
                reinforced=reinforced,
            )
        provenance=validate_approval(
            approval,
            plan,
            reinforced=reinforced,
        )
        if provenance["reviewer_id"]!=github_provenance["github_reviewer"]:
            raise ApprovalProvenanceError("approval reviewer does not match GitHub reviewer")
        if reinforced and provenance["second_reviewer_id"]!=github_provenance["github_second_reviewer"]:
            raise ApprovalProvenanceError("approval second reviewer does not match GitHub reviewer")
        if approval_ledger is not None and validate_ledger(approval_ledger).get("valid") is not True:
            raise ApprovalProvenanceError("approval ledger invalid")
    except ApprovalProvenanceError as exc:
        raise ReputationPolicyMigrationError(str(exc)) from None

    now=float(now) if isinstance(now,(int,float)) else time.time()
    issued_at=authorization.get("issued_at")
    expires_at=authorization.get("expires_at")
    if not isinstance(issued_at,(int,float)) or not isinstance(expires_at,(int,float)):
        raise ReputationPolicyMigrationError("migration authorization lifetime missing")
    if expires_at<=issued_at or expires_at-issued_at>AUTHORIZATION_TTL_SECONDS:
        raise ReputationPolicyMigrationError("migration authorization lifetime invalid")
    if now<issued_at or now>=expires_at:
        raise ReputationPolicyMigrationError("migration authorization expired or not yet valid")

    try:
        next_approval_ledger=consume_approval(
            approval_ledger,
            migration_id=str(plan.get("migration_id")),
            review_digest=expected_review_digest,
            approval_digest_value=provenance["approval_digest"],
            applied_at=now,
        )
    except ApprovalProvenanceError as exc:
        raise ReputationPolicyMigrationError(str(exc)) from None

    current_digest=registry_digest(registry)
    if current_digest!=plan.get("source_registry_digest"):
        raise ReputationPolicyMigrationError("registry changed after migration review")
    if plan.get("target_policy_version")!=TRANSITION_POLICY_VERSION or plan.get("target_policy_digest")!=transition_policy_digest():
        raise ReputationPolicyMigrationError("target transition policy changed after review")

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
        required_gates=list(rule.get("required_gates",[]))
        target_gate=DANGEROUS_STATE_GATES.get(target)
        if target_gate and target_gate not in required_gates:
            required_gates.insert(0,target_gate)
        if target=="RECOVERING" and "replacement_reputation_transition_completed" not in required_gates:
            required_gates.append("replacement_reputation_transition_completed")
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
            "required_transition_gates":required_gates,
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
            "recovery_confirmations_required":RECOVERY_CONFIRMATIONS_REQUIRED,
            "recovery_min_dwell_seconds":RECOVERY_MIN_DWELL_SECONDS,
            "recovery_min_new_effective_samples":RECOVERY_MIN_NEW_EFFECTIVE_SAMPLES,
            "fast_downward_transitions":True,
            "slow_upward_recovery":True,
            "upward_transition_requires_time_and_new_evidence":True,
            "validation":validate_transition_policy(),
        },
        "policy_migration_approval_ledger":next_approval_ledger,
        "last_policy_migration":{
            "migration_id":plan.get("migration_id"),
            "risk_level":risk.get("level"),
            "reinforced_review_required":risk.get("reinforced_review_required") is True,
            "reinforced_reviewed":authorization.get("reinforced_reviewed") is True,
            "review_digest":expected_review_digest,
            "authorization_issued_at":issued_at,
            "authorization_expires_at":expires_at,
            "approval_digest":provenance["approval_digest"],
            "github_attestation_digest":github_provenance["attestation_digest"],
            "github_repository":github_provenance["repository"],
            "github_commit_sha":github_provenance["commit_sha"],
            "github_pull_request":github_provenance["pull_request"],
            "github_workflow_run_id":github_provenance["workflow_run_id"],
            "github_reviewer":github_provenance["github_reviewer"],
            "github_second_reviewer":github_provenance["github_second_reviewer"],
            "github_head_ref":github_provenance["github_head_ref"],
            "github_base_ref":github_provenance["github_base_ref"],
            "github_pr_author":github_provenance["github_pr_author"],
            "github_head_commit_timestamp":github_provenance["github_head_commit_timestamp"],
            "github_reviewer_submitted_at":github_provenance["github_reviewer_submitted_at"],
            "github_second_reviewer_submitted_at":github_provenance["github_second_reviewer_submitted_at"],
            "github_required_checks":github_provenance["required_checks"],
            "github_passed_checks":github_provenance["passed_checks"],
            "reviewer_id":provenance["reviewer_id"],
            "second_reviewer_id":provenance["second_reviewer_id"],
            "approval_ledger_head":next_approval_ledger["head"],
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
    from architecture_reputation_policy_migration_review import render
    atomic_write_text(
        out/"architecture-reputation-policy-migration-review.md",
        render(result),
        encoding="utf-8",
    )
    return result

def write_applied(registry: dict, plan: dict, authorization: dict, path: Path, *, approval: dict | None=None, github_attestation: dict | None=None, approval_ledger: dict | None=None, now: float | None=None) -> dict:
    migrated=apply_migration(registry,plan,authorization,approval=approval,github_attestation=github_attestation,approval_ledger=approval_ledger,now=now)
    atomic_write_text(
        path,
        json.dumps(migrated,ensure_ascii=False,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    return migrated
