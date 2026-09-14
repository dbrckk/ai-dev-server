"""Collect GitHub evidence and build a migration approval attestation.

This module performs read-only GitHub API calls. It never approves, merges, or mutates a PR.
"""
from __future__ import annotations

import re
import urllib.parse

from architecture_replacement_persist import _request, ReplacementPersistenceError
from architecture_reputation_policy_approval import ApprovalProvenanceError
from architecture_reputation_policy_github_attestation import build, latest_approvals

class GitHubAttestationCollectionError(RuntimeError):
    pass

def _valid_repository(value: str) -> bool:
    return isinstance(value,str) and re.fullmatch(r"[^/]+/[^/]+",value) is not None

def collect_review_target(*, token: str, repository: str, pull_request: int) -> dict:
    if not token:
        raise GitHubAttestationCollectionError("GitHub token missing")
    if not _valid_repository(repository):
        raise GitHubAttestationCollectionError("GitHub repository invalid")
    if not isinstance(pull_request,int) or pull_request<1:
        raise GitHubAttestationCollectionError("pull request invalid")
    api="https://api.github.com/repos/"+repository
    try:
        pr=_request(api+f"/pulls/{pull_request}",token)
    except ReplacementPersistenceError as exc:
        raise GitHubAttestationCollectionError("GitHub PR target collection failed") from exc
    if not isinstance(pr,dict):
        raise GitHubAttestationCollectionError("pull request response malformed")
    head=pr.get("head") if isinstance(pr.get("head"),dict) else {}
    base=pr.get("base") if isinstance(pr.get("base"),dict) else {}
    user=pr.get("user") if isinstance(pr.get("user"),dict) else {}
    target={
        "repository":repository,
        "pull_request":pull_request,
        "commit_sha":head.get("sha"),
        "head_ref":head.get("ref"),
        "base_ref":base.get("ref"),
        "author":user.get("login"),
    }
    if any(not target.get(key) for key in target):
        raise GitHubAttestationCollectionError("GitHub PR review target incomplete")
    if pr.get("state")!="open" or pr.get("draft") is True:
        raise GitHubAttestationCollectionError("GitHub PR review target is not review-ready")
    if target["base_ref"]!="main":
        raise GitHubAttestationCollectionError("GitHub PR review target base is not main")
    return target

def collect(plan: dict, *, token: str, repository: str, pull_request: int) -> dict:
    if not token:
        raise GitHubAttestationCollectionError("GitHub token missing")
    if not _valid_repository(repository):
        raise GitHubAttestationCollectionError("GitHub repository invalid")
    if not isinstance(pull_request,int) or pull_request<1:
        raise GitHubAttestationCollectionError("pull request invalid")

    api="https://api.github.com/repos/"+repository
    try:
        pr=_request(api+f"/pulls/{pull_request}",token)
        if not isinstance(pr,dict):
            raise GitHubAttestationCollectionError("pull request response malformed")
        commit_sha=pr.get("head",{}).get("sha") if isinstance(pr.get("head"),dict) else None
        if not isinstance(commit_sha,str) or not commit_sha:
            raise GitHubAttestationCollectionError("pull request head SHA missing")

        commit=_request(api+f"/commits/{commit_sha}",token)
        commit_data=commit.get("commit") if isinstance(commit,dict) and isinstance(commit.get("commit"),dict) else {}
        committer=commit_data.get("committer") if isinstance(commit_data.get("committer"),dict) else {}
        author_commit=commit_data.get("author") if isinstance(commit_data.get("author"),dict) else {}
        head_commit_time_raw=committer.get("date") or author_commit.get("date")
        if not isinstance(head_commit_time_raw,str) or not head_commit_time_raw:
            raise GitHubAttestationCollectionError("head commit timestamp missing")

        from architecture_reputation_policy_github_attestation import _timestamp
        head_commit_timestamp=_timestamp(head_commit_time_raw)
        if head_commit_timestamp is None:
            raise GitHubAttestationCollectionError("head commit timestamp invalid")

        reviews=_request(api+f"/pulls/{pull_request}/reviews?per_page=100",token)
        if not isinstance(reviews,list):
            raise GitHubAttestationCollectionError("pull request reviews malformed")

        approvals=latest_approvals(reviews,commit_sha,head_commit_timestamp=head_commit_timestamp)
        permissions={}
        for row in approvals:
            login=row.get("login")
            if not isinstance(login,str) or not login:
                continue
            value=_request(api+f"/collaborators/{urllib.parse.quote(login,safe='')}/permission",token)
            permission=value.get("permission") if isinstance(value,dict) else None
            if isinstance(permission,str):
                permissions[login]=permission

        checks_response=_request(api+f"/commits/{commit_sha}/check-runs?per_page=100",token)
        check_runs=(
            checks_response.get("check_runs")
            if isinstance(checks_response,dict) and isinstance(checks_response.get("check_runs"),list)
            else None
        )
        if check_runs is None:
            raise GitHubAttestationCollectionError("check runs malformed")

        query=urllib.parse.urlencode({
            "head_sha":commit_sha,
            "event":"pull_request",
            "per_page":100,
        })
        runs_response=_request(api+"/actions/runs?"+query,token)
        workflow_runs=(
            runs_response.get("workflow_runs")
            if isinstance(runs_response,dict) and isinstance(runs_response.get("workflow_runs"),list)
            else None
        )
        if workflow_runs is None:
            raise GitHubAttestationCollectionError("workflow runs malformed")

        risk=plan.get("risk") if isinstance(plan,dict) and isinstance(plan.get("risk"),dict) else {}
        reinforced=risk.get("reinforced_review_required") is True
        head=pr.get("head") if isinstance(pr.get("head"),dict) else {}
        base=pr.get("base") if isinstance(pr.get("base"),dict) else {}
        user=pr.get("user") if isinstance(pr.get("user"),dict) else {}
        pr_identity={
            "number":pull_request,
            "state":pr.get("state"),
            "draft":pr.get("draft") is True,
            "head_ref":head.get("ref"),
            "head_sha":head.get("sha"),
            "base_ref":base.get("ref"),
            "author":user.get("login"),
        }
        return build(
            plan,
            repository=repository,
            pull_request=pull_request,
            commit_sha=commit_sha,
            reviews=reviews,
            permissions=permissions,
            workflow_runs=workflow_runs,
            check_runs=check_runs,
            pr_identity=pr_identity,
            head_commit_timestamp=head_commit_timestamp,
            reinforced=reinforced,
        )
    except ReplacementPersistenceError as exc:
        raise GitHubAttestationCollectionError("GitHub evidence collection failed") from exc
    except ApprovalProvenanceError as exc:
        raise GitHubAttestationCollectionError(str(exc)) from None
