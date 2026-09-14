"""Validate persisted replacement pull requests against immutable local approval evidence.

Read-only GitHub validator: verifies PR identity, exact file scope/content hashes, trusted
GitHub Actions checks, branch/head binding, and clean merge state. It never writes or merges.
"""
from __future__ import annotations

import base64
import hashlib
from pathlib import Path
from urllib.parse import quote, urlparse

from architecture_replacement_persist import _request, ReplacementPersistenceError
from replacement_ci_policy import REQUIRED_GITHUB_CHECKS as REQUIRED_CHECKS, TRUSTED_CHECK_APP

class ReplacementPRValidationError(RuntimeError):
    pass

def _trusted_check(run: dict, repository: str) -> bool:
    if not isinstance(run,dict):
        return False
    app=run.get("app")
    if not isinstance(app,dict) or app.get("slug")!=TRUSTED_CHECK_APP:
        return False
    details=run.get("details_url")
    if not isinstance(details,str):
        return False
    parsed=urlparse(details)
    prefix="/"+repository+"/actions/runs/"
    return (
        parsed.scheme=="https"
        and parsed.netloc=="github.com"
        and parsed.path.startswith(prefix)
    )

def _expected_files(package: dict) -> dict[str,str]:
    rows=package.get("files") if isinstance(package,dict) else None
    if not isinstance(rows,list) or not rows:
        raise ReplacementPRValidationError("PR package file evidence missing")
    out={}
    for row in rows:
        if not isinstance(row,dict):
            raise ReplacementPRValidationError("PR package file evidence malformed")
        path=row.get("path")
        digest=row.get("sha256")
        if not isinstance(path,str) or not path or not isinstance(digest,str) or len(digest)!=64:
            raise ReplacementPRValidationError("PR package file evidence malformed")
        if path in out:
            raise ReplacementPRValidationError("duplicate approved PR path")
        out[path]=digest
    return out

def _decode_content(value: dict) -> bytes:
    if not isinstance(value,dict) or value.get("encoding")!="base64":
        raise ReplacementPRValidationError("GitHub content evidence malformed")
    content=value.get("content")
    if not isinstance(content,str):
        raise ReplacementPRValidationError("GitHub content evidence missing")
    try:
        return base64.b64decode(content,validate=False)
    except (ValueError,TypeError):
        raise ReplacementPRValidationError("GitHub content evidence invalid") from None

def validate(review: dict, package: dict, persisted: dict, token: str, repository: str, requester=_request) -> dict:
    if not token:
        raise ReplacementPRValidationError("GitHub token missing")
    if not isinstance(repository,str) or repository.count("/")!=1:
        raise ReplacementPRValidationError("GitHub repository invalid")
    if review.get("status")!="promotion_review_ready":
        raise ReplacementPRValidationError("promotion review not ready")
    if package.get("status")!="pr_package_ready":
        raise ReplacementPRValidationError("PR package not ready")
    if persisted.get("status") not in {"replacement_pr_created","replacement_pr_already_exists"}:
        raise ReplacementPRValidationError("persisted replacement PR evidence invalid")

    for key in ("work_order_id","branch"):
        if package.get(key)!=persisted.get(key):
            raise ReplacementPRValidationError("persisted PR identity mismatch: "+key)
    number=persisted.get("pull_request")
    head_sha=persisted.get("commit_sha")
    branch=persisted.get("branch")
    if not isinstance(number,int) or not isinstance(head_sha,str) or len(head_sha)!=40:
        raise ReplacementPRValidationError("persisted PR proof incomplete")

    api="https://api.github.com/repos/"+repository
    pr=requester(api+"/pulls/"+str(number),token)
    if not isinstance(pr,dict) or pr.get("state")!="open":
        raise ReplacementPRValidationError("replacement PR is not open")
    if pr.get("base",{}).get("ref")!="main":
        raise ReplacementPRValidationError("replacement PR base changed")
    if pr.get("head",{}).get("ref")!=branch or pr.get("head",{}).get("sha")!=head_sha:
        raise ReplacementPRValidationError("replacement PR head changed")

    expected=_expected_files(package)
    files=requester(api+"/pulls/"+str(number)+"/files?per_page=100",token)
    if not isinstance(files,list) or len(files)!=len(expected):
        raise ReplacementPRValidationError("replacement PR file scope changed")
    names={row.get("filename") for row in files if isinstance(row,dict)}
    if names!=set(expected):
        raise ReplacementPRValidationError("replacement PR contains unapproved paths")
    if any(row.get("status") not in {"added","modified"} for row in files if isinstance(row,dict)):
        raise ReplacementPRValidationError("replacement PR contains destructive file changes")

    verified=[]
    for path,digest in sorted(expected.items()):
        content=requester(
            api+"/contents/"+quote(path,safe="/")+"?ref="+head_sha,
            token,
        )
        actual=hashlib.sha256(_decode_content(content)).hexdigest()
        if actual!=digest:
            raise ReplacementPRValidationError("replacement PR content digest mismatch: "+path)
        verified.append(path)

    checks=requester(api+"/commits/"+head_sha+"/check-runs?per_page=100",token)
    runs=checks.get("check_runs") if isinstance(checks,dict) else None
    if not isinstance(runs,list):
        raise ReplacementPRValidationError("GitHub check-run evidence malformed")
    trusted=[run for run in runs if _trusted_check(run,repository)]
    by_name={run.get("name"):run for run in trusted if isinstance(run.get("name"),str)}
    missing=sorted(REQUIRED_CHECKS-set(by_name))
    if missing:
        return {
            "version":1,
            "status":"awaiting_required_checks",
            "pull_request":number,
            "branch":branch,
            "head_sha":head_sha,
            "missing_checks":missing,
            "draft":pr.get("draft") is True,
            "ready_to_merge":False,
        }
    incomplete=[name for name in sorted(REQUIRED_CHECKS) if by_name[name].get("status")!="completed"]
    if incomplete:
        return {
            "version":1,
            "status":"awaiting_required_checks",
            "pull_request":number,
            "branch":branch,
            "head_sha":head_sha,
            "missing_checks":[],
            "incomplete_checks":incomplete,
            "draft":pr.get("draft") is True,
            "ready_to_merge":False,
        }
    failed=[name for name in sorted(REQUIRED_CHECKS) if by_name[name].get("conclusion")!="success"]
    if failed:
        raise ReplacementPRValidationError("required replacement PR check failed: "+",".join(failed))

    # Re-fetch immediately before readiness decision to bind the final state.
    final_pr=requester(api+"/pulls/"+str(number),token)
    if final_pr.get("head",{}).get("sha")!=head_sha or final_pr.get("head",{}).get("ref")!=branch:
        raise ReplacementPRValidationError("replacement PR changed during validation")

    draft=final_pr.get("draft") is True
    clean=final_pr.get("mergeable") is True and final_pr.get("mergeable_state")=="clean"
    if draft:
        status="validated_draft"
        ready=False
    elif not clean:
        status="awaiting_clean_merge_state"
        ready=False
    else:
        status="ready_to_merge"
        ready=True

    return {
        "version":1,
        "status":status,
        "pull_request":number,
        "branch":branch,
        "head_sha":head_sha,
        "verified_files":verified,
        "required_checks":sorted(REQUIRED_CHECKS),
        "draft":draft,
        "mergeable_clean":clean,
        "ready_to_merge":ready,
        "policy":{
            "read_only_validation":True,
            "auto_merge":False,
            "require_explicit_merge_action":True,
        },
    }
