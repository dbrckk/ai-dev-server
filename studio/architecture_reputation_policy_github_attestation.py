"""Build deterministic GitHub evidence for reputation-policy migration approval.

This module is intentionally connector-agnostic: callers fetch PR/review/permission/workflow
objects from GitHub, then this pure builder normalizes and binds them to the migration plan.
"""
from __future__ import annotations
import hashlib
import json
from architecture_reputation_policy_approval import ApprovalProvenanceError, validate_github_attestation

def _canonical(v):
    return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False)

def _login(review):
    author=review.get("author") if isinstance(review,dict) else None
    if isinstance(author,dict):
        return author.get("login") or author.get("name")
    return review.get("login") if isinstance(review,dict) else None

def _state(review):
    value=review.get("state") if isinstance(review,dict) else None
    return str(value or "").upper()

def _commit(review):
    if not isinstance(review,dict): return None
    return review.get("commit_sha") or review.get("commitId") or review.get("commit_id")

def latest_approvals(reviews: list[dict], commit_sha: str) -> list[dict]:
    latest={}
    for review in reviews if isinstance(reviews,list) else []:
        login=_login(review)
        if not login: continue
        latest[login]=review
    rows=[]
    for login,review in sorted(latest.items()):
        if _state(review)!="APPROVED": continue
        review_commit=_commit(review)
        if review_commit and review_commit!=commit_sha: continue
        rows.append({"login":login,"review_state":"APPROVED","reviewed_commit_sha":review_commit or commit_sha})
    return rows

def successful_workflow(runs: list[dict], commit_sha: str) -> dict:
    candidates=[]
    for run in runs if isinstance(runs,list) else []:
        head=run.get("head_sha")
        conclusion=str(run.get("conclusion") or "").lower()
        if head==commit_sha and conclusion=="success":
            candidates.append(run)
    if not candidates:
        raise ApprovalProvenanceError("no successful workflow for reviewed commit")
    run=sorted(candidates,key=lambda x:int(x.get("id") or 0),reverse=True)[0]
    return {"id":run.get("id"),"head_sha":commit_sha,"conclusion":"success","name":run.get("name")}

def build(plan: dict, *, repository: str, pull_request: int, commit_sha: str,
          reviews: list[dict], permissions: dict[str,str], workflow_runs: list[dict],
          reinforced: bool) -> dict:
    approvals=latest_approvals(reviews,commit_sha)
    eligible=[a for a in approvals if permissions.get(a["login"]) in {"admin","maintain","write"}]
    if not eligible:
        raise ApprovalProvenanceError("no eligible GitHub approver")
    first=eligible[0]
    first["permission"]=permissions[first["login"]]
    second=None
    if reinforced:
        if len(eligible)<2:
            raise ApprovalProvenanceError("reinforced GitHub approval requires two eligible approvers")
        second=eligible[1]
        second["permission"]=permissions[second["login"]]
    workflow=successful_workflow(workflow_runs,commit_sha)
    attestation={
        "repository":repository,
        "commit_sha":commit_sha,
        "reviewed_commit_sha":commit_sha,
        "pull_request":pull_request,
        "workflow_run_id":workflow["id"],
        "migration_id":plan.get("migration_id"),
        "review_digest":plan.get("review_digest"),
        "reviewer":first,
        "workflow":{"head_sha":workflow["head_sha"],"conclusion":workflow["conclusion"],"name":workflow["name"]},
    }
    if second is not None: attestation["second_reviewer"]=second
    attestation["attestation_digest"]=hashlib.sha256(_canonical(attestation).encode()).hexdigest()
    validate_github_attestation(attestation,plan,reinforced=reinforced)
    return attestation
