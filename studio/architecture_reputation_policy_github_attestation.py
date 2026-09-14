"""Build deterministic GitHub evidence for reputation-policy migration approval.

This module is intentionally connector-agnostic: callers fetch PR/review/permission/workflow
objects from GitHub, then this pure builder normalizes and binds them to the migration plan.
"""
from __future__ import annotations
import hashlib
import json
from datetime import datetime,timezone
from architecture_reputation_policy_approval import ApprovalProvenanceError, validate_github_attestation
from replacement_ci_policy import validate_check_runs

def _canonical(v):
    return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False)

def _login(review):
    if not isinstance(review,dict):
        return None
    for key in ("author","user"):
        value=review.get(key)
        if isinstance(value,dict):
            login=value.get("login") or value.get("name")
            if login:
                return login
    return review.get("login")

def _state(review):
    value=review.get("state") if isinstance(review,dict) else None
    return str(value or "").upper()

def _commit(review):
    if not isinstance(review,dict): return None
    return review.get("commit_sha") or review.get("commitId") or review.get("commit_id") or review.get("commit_oid")

def _timestamp(value) -> float | None:
    if isinstance(value,(int,float)):
        return float(value)
    if not isinstance(value,str) or not value:
        return None
    try:
        text=value[:-1]+"+00:00" if value.endswith("Z") else value
        dt=datetime.fromisoformat(text)
        if dt.tzinfo is None:
            dt=dt.replace(tzinfo=timezone.utc)
        return dt.timestamp()
    except ValueError:
        return None

def _submitted_at(review):
    if not isinstance(review,dict):
        return None
    return (
        review.get("submitted_at")
        or review.get("submittedAt")
        or review.get("created_at")
        or review.get("createdAt")
    )

def _review_order_key(review) -> tuple[float,int]:
    ts=_timestamp(_submitted_at(review))
    review_id=review.get("id") if isinstance(review,dict) else None
    try:
        rid=int(review_id or 0)
    except (TypeError,ValueError):
        rid=0
    return (ts if ts is not None else float("-inf"),rid)

def latest_approvals(reviews: list[dict], commit_sha: str, *, head_commit_timestamp: float | None=None) -> list[dict]:
    latest={}
    for review in reviews if isinstance(reviews,list) else []:
        login=_login(review)
        if not login:
            continue
        current=latest.get(login)
        if current is None or _review_order_key(review)>=_review_order_key(current):
            latest[login]=review
    rows=[]
    for login,review in sorted(latest.items()):
        if _state(review)!="APPROVED": continue
        review_commit=_commit(review)
        if review_commit and review_commit!=commit_sha: continue
        submitted_raw=_submitted_at(review)
        submitted_ts=_timestamp(submitted_raw)
        if head_commit_timestamp is not None:
            if submitted_ts is None or submitted_ts<head_commit_timestamp:
                continue
        rows.append({
            "login":login,
            "review_state":"APPROVED",
            "reviewed_commit_sha":review_commit or commit_sha,
            "submitted_at":submitted_raw,
            "submitted_at_epoch":submitted_ts,
        })
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
          check_runs: list[dict], pr_identity: dict, head_commit_timestamp: float, reinforced: bool) -> dict:
    if not isinstance(head_commit_timestamp,(int,float)):
        raise ApprovalProvenanceError("head commit timestamp missing")
    approvals=latest_approvals(reviews,commit_sha,head_commit_timestamp=float(head_commit_timestamp))
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
    checks=validate_check_runs(check_runs,repository)
    if checks.get("valid") is not True:
        raise ApprovalProvenanceError("required GitHub checks are not all successful")
    attestation={
        "repository":repository,
        "commit_sha":commit_sha,
        "reviewed_commit_sha":commit_sha,
        "pull_request":pull_request,
        "workflow_run_id":workflow["id"],
        "migration_id":plan.get("migration_id"),
        "review_digest":plan.get("review_digest"),
        "reviewer":first,
        "head_commit_timestamp":float(head_commit_timestamp),
        "pr_identity":pr_identity,
        "required_checks":checks,
        "workflow":{"head_sha":workflow["head_sha"],"conclusion":workflow["conclusion"],"name":workflow["name"]},
    }
    if second is not None: attestation["second_reviewer"]=second
    attestation["attestation_digest"]=hashlib.sha256(_canonical(attestation).encode()).hexdigest()
    validate_github_attestation(attestation,plan,reinforced=reinforced)
    return attestation
