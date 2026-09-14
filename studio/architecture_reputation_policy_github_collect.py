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

        reviews=_request(api+f"/pulls/{pull_request}/reviews?per_page=100",token)
        if not isinstance(reviews,list):
            raise GitHubAttestationCollectionError("pull request reviews malformed")

        approvals=latest_approvals(reviews,commit_sha)
        permissions={}
        for row in approvals:
            login=row.get("login")
            if not isinstance(login,str) or not login:
                continue
            value=_request(api+f"/collaborators/{urllib.parse.quote(login,safe='')}/permission",token)
            permission=value.get("permission") if isinstance(value,dict) else None
            if isinstance(permission,str):
                permissions[login]=permission

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
        return build(
            plan,
            repository=repository,
            pull_request=pull_request,
            commit_sha=commit_sha,
            reviews=reviews,
            permissions=permissions,
            workflow_runs=workflow_runs,
            reinforced=reinforced,
        )
    except ReplacementPersistenceError as exc:
        raise GitHubAttestationCollectionError("GitHub evidence collection failed") from exc
    except ApprovalProvenanceError as exc:
        raise GitHubAttestationCollectionError(str(exc)) from None
