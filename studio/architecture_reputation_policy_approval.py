"""Approval provenance and append-only anti-replay ledger for reputation policy migrations."""
from __future__ import annotations
import hashlib
import json

LEDGER_VERSION=1
GENESIS_HASH="0"*64
ROLE_REVIEWER="reviewer"
ROLE_RISK_OWNER="risk_owner"

class ApprovalProvenanceError(RuntimeError):
    pass

def _canonical(v):
    return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False)

def approval_digest(approval: dict) -> str:
    payload={k:v for k,v in approval.items() if k!="approval_digest"}
    return hashlib.sha256(_canonical(payload).encode()).hexdigest()

def validate_approval(approval: dict, plan: dict, *, reinforced: bool) -> dict:
    if not isinstance(approval,dict):
        raise ApprovalProvenanceError("approval provenance missing")
    reviewer=approval.get("reviewer")
    if not isinstance(reviewer,dict) or not isinstance(reviewer.get("id"),str) or not reviewer["id"].strip():
        raise ApprovalProvenanceError("reviewer identity missing")
    roles=reviewer.get("roles")
    if not isinstance(roles,list) or ROLE_REVIEWER not in roles:
        raise ApprovalProvenanceError("reviewer role missing")
    if approval.get("migration_id")!=plan.get("migration_id") or approval.get("review_digest")!=plan.get("review_digest"):
        raise ApprovalProvenanceError("approval provenance binding mismatch")
    second=approval.get("second_reviewer")
    if reinforced:
        if not isinstance(second,dict) or not isinstance(second.get("id"),str) or not second["id"].strip():
            raise ApprovalProvenanceError("second reviewer identity missing")
        if second["id"]==reviewer["id"]:
            raise ApprovalProvenanceError("reinforced review requires separation of duties")
        second_roles=second.get("roles")
        if not isinstance(second_roles,list) or ROLE_RISK_OWNER not in second_roles:
            raise ApprovalProvenanceError("risk owner role missing")
    expected=approval_digest(approval)
    if approval.get("approval_digest")!=expected:
        raise ApprovalProvenanceError("approval provenance digest mismatch")
    return {"reviewer_id":reviewer["id"],"second_reviewer_id":second.get("id") if isinstance(second,dict) else None,"approval_digest":expected}

def new_ledger() -> dict:
    return {"version":LEDGER_VERSION,"head":GENESIS_HASH,"events":[]}

def consume(ledger: dict | None, *, migration_id: str, review_digest: str, approval_digest_value: str, applied_at: float) -> dict:
    ledger=dict(ledger) if isinstance(ledger,dict) else new_ledger()
    events=list(ledger.get("events",[])) if isinstance(ledger.get("events"),list) else []
    if any(isinstance(e,dict) and (e.get("migration_id")==migration_id or e.get("approval_digest")==approval_digest_value) for e in events):
        raise ApprovalProvenanceError("migration authorization replay detected")
    previous=ledger.get("head") if isinstance(ledger.get("head"),str) else GENESIS_HASH
    body={"sequence":len(events)+1,"previous_hash":previous,"migration_id":migration_id,"review_digest":review_digest,"approval_digest":approval_digest_value,"applied_at":applied_at}
    event_hash=hashlib.sha256(_canonical(body).encode()).hexdigest()
    event={**body,"event_hash":event_hash}
    return {"version":LEDGER_VERSION,"head":event_hash,"events":events+[event]}

def validate_ledger(ledger: dict | None) -> dict:
    if not isinstance(ledger,dict):
        return {"valid":False,"reason":"ledger_missing"}
    previous=GENESIS_HASH
    events=ledger.get("events")
    if not isinstance(events,list):
        return {"valid":False,"reason":"events_malformed"}
    seen=set()
    for index,event in enumerate(events,1):
        if not isinstance(event,dict) or event.get("sequence")!=index or event.get("previous_hash")!=previous:
            return {"valid":False,"reason":"chain_broken"}
        body={k:v for k,v in event.items() if k!="event_hash"}
        digest=hashlib.sha256(_canonical(body).encode()).hexdigest()
        if event.get("event_hash")!=digest:
            return {"valid":False,"reason":"event_digest_mismatch"}
        if event.get("migration_id") in seen:
            return {"valid":False,"reason":"migration_replay"}
        seen.add(event.get("migration_id"))
        previous=digest
    return {"valid":ledger.get("head")==previous,"events":len(events),"head":previous}

def validate_github_attestation(attestation: dict, plan: dict, *, reinforced: bool) -> dict:
    """Validate already-fetched GitHub evidence. Network/API retrieval stays outside this pure validator."""
    if not isinstance(attestation,dict):
        raise ApprovalProvenanceError("github attestation missing")
    required=("repository","commit_sha","pull_request","workflow_run_id")
    if any(not attestation.get(k) for k in required):
        raise ApprovalProvenanceError("github attestation incomplete")
    if attestation.get("migration_id")!=plan.get("migration_id") or attestation.get("review_digest")!=plan.get("review_digest"):
        raise ApprovalProvenanceError("github attestation binding mismatch")
    if attestation.get("commit_sha")!=attestation.get("reviewed_commit_sha"):
        raise ApprovalProvenanceError("review does not bind current commit")
    reviewer=attestation.get("reviewer")
    if not isinstance(reviewer,dict) or reviewer.get("review_state")!="APPROVED":
        raise ApprovalProvenanceError("github approving review missing")
    if reviewer.get("permission") not in {"admin","maintain","write"}:
        raise ApprovalProvenanceError("github reviewer lacks write-level permission")
    second=attestation.get("second_reviewer")
    if reinforced:
        if not isinstance(second,dict) or second.get("review_state")!="APPROVED":
            raise ApprovalProvenanceError("second github approving review missing")
        if second.get("login")==reviewer.get("login"):
            raise ApprovalProvenanceError("github reinforced review requires separation of duties")
        if second.get("permission") not in {"admin","maintain","write"}:
            raise ApprovalProvenanceError("second github reviewer lacks write-level permission")
    workflow=attestation.get("workflow")
    if not isinstance(workflow,dict) or workflow.get("conclusion")!="success":
        raise ApprovalProvenanceError("github workflow is not successful")
    if workflow.get("head_sha")!=attestation.get("commit_sha"):
        raise ApprovalProvenanceError("github workflow does not bind reviewed commit")
    payload={k:v for k,v in attestation.items() if k!="attestation_digest"}
    digest=hashlib.sha256(_canonical(payload).encode()).hexdigest()
    if attestation.get("attestation_digest")!=digest:
        raise ApprovalProvenanceError("github attestation digest mismatch")
    return {
        "repository":attestation["repository"],
        "commit_sha":attestation["commit_sha"],
        "pull_request":attestation["pull_request"],
        "workflow_run_id":attestation["workflow_run_id"],
        "github_reviewer":reviewer.get("login"),
        "github_second_reviewer":second.get("login") if isinstance(second,dict) else None,
        "attestation_digest":digest,
    }

def approval_from_github_attestation(attestation: dict, plan: dict, *, reinforced: bool) -> dict:
    github=validate_github_attestation(attestation,plan,reinforced=reinforced)
    approval={
        "migration_id":plan.get("migration_id"),
        "review_digest":plan.get("review_digest"),
        "reviewer":{
            "id":github["github_reviewer"],
            "roles":[ROLE_REVIEWER],
            "source":"github_verified",
        },
        "github_attestation_digest":github["attestation_digest"],
    }
    if reinforced:
        approval["second_reviewer"]={
            "id":github["github_second_reviewer"],
            "roles":[ROLE_RISK_OWNER],
            "source":"github_verified",
        }
    approval["approval_digest"]=approval_digest(approval)
    return approval
