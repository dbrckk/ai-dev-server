"""Post-merge assurance for architecture replacements.

Read-only verifier for the exact merge commit. It checks that main contains the merge,
that trusted GitHub Actions checks on that exact merge SHA succeeded, and that approved
replacement file content survived the merge unchanged. It emits rollback-required evidence
on any regression but performs no rollback or GitHub write.
"""
from __future__ import annotations

import base64
import hashlib
import re
from urllib.parse import quote

from architecture_replacement_persist import _request
from replacement_ci_policy import REQUIRED_GITHUB_CHECKS as REQUIRED_CHECKS, validate_check_runs

class ReplacementPostMergeError(RuntimeError):
    pass

def _sha(value,label):
    if not isinstance(value,str) or not re.fullmatch(r"[0-9a-f]{40}",value):
        raise ReplacementPostMergeError(label+" SHA invalid")
    return value

def _expected_files(package):
    rows=package.get("files") if isinstance(package,dict) else None
    if not isinstance(rows,list) or not rows:
        raise ReplacementPostMergeError("replacement package file evidence missing")
    out={}
    for row in rows:
        if not isinstance(row,dict):
            raise ReplacementPostMergeError("replacement package file evidence malformed")
        path=row.get("path")
        digest=row.get("sha256")
        if not isinstance(path,str) or not path or not isinstance(digest,str) or not re.fullmatch(r"[0-9a-f]{64}",digest):
            raise ReplacementPostMergeError("replacement package file evidence malformed")
        if path in out:
            raise ReplacementPostMergeError("duplicate replacement package path")
        out[path]=digest
    return out

def _content_bytes(value):
    if not isinstance(value,dict) or value.get("encoding")!="base64" or not isinstance(value.get("content"),str):
        raise ReplacementPostMergeError("merge content evidence malformed")
    try:
        return base64.b64decode(value["content"],validate=False)
    except (ValueError,TypeError):
        raise ReplacementPostMergeError("merge content evidence invalid") from None

def verify(merged,package,token,repository,requester=_request):
    if not token:
        raise ReplacementPostMergeError("GitHub token missing")
    if not isinstance(repository,str) or repository.count("/")!=1:
        raise ReplacementPostMergeError("GitHub repository invalid")
    if not isinstance(merged,dict) or merged.get("status")!="replacement_merged":
        raise ReplacementPostMergeError("replacement merge evidence invalid")
    if not isinstance(package,dict) or package.get("status")!="pr_package_ready":
        raise ReplacementPostMergeError("replacement PR package invalid")
    if merged.get("work_order_id")!=package.get("work_order_id"):
        raise ReplacementPostMergeError("post-merge work order mismatch")

    merge_sha=_sha(merged.get("merge_sha"),"Merge")
    api="https://api.github.com/repos/"+repository

    branch=requester(api+"/branches/main",token)
    main_sha=branch.get("commit",{}).get("sha") if isinstance(branch,dict) else None
    if main_sha!=merge_sha:
        return {
            "version":1,
            "status":"awaiting_main_head",
            "work_order_id":merged.get("work_order_id"),
            "merge_sha":merge_sha,
            "observed_main_sha":main_sha,
            "rollback_required":False,
            "post_merge_healthy":False,
        }

    expected=_expected_files(package)
    verified=[]
    mismatches=[]
    for path,digest in sorted(expected.items()):
        value=requester(api+"/contents/"+quote(path,safe="/")+"?ref="+merge_sha,token)
        actual=hashlib.sha256(_content_bytes(value)).hexdigest()
        if actual!=digest:
            mismatches.append(path)
        else:
            verified.append(path)

    checks=requester(api+"/commits/"+merge_sha+"/check-runs?per_page=100",token)
    runs=checks.get("check_runs") if isinstance(checks,dict) else None
    if not isinstance(runs,list):
        raise ReplacementPostMergeError("post-merge check evidence malformed")
    check_result=validate_check_runs(runs,repository)
    missing=check_result["missing_checks"]
    incomplete=check_result["incomplete_checks"]
    failed=check_result["failed_checks"]

    if mismatches or failed:
        status="post_merge_regression"
        rollback=True
        healthy=False
    elif missing or incomplete:
        status="awaiting_post_merge_checks"
        rollback=False
        healthy=False
    else:
        status="post_merge_healthy"
        rollback=False
        healthy=True

    return {
        "version":1,
        "status":status,
        "work_order_id":merged.get("work_order_id"),
        "pull_request":merged.get("pull_request"),
        "merge_sha":merge_sha,
        "verified_files":verified,
        "content_mismatches":mismatches,
        "required_checks":sorted(REQUIRED_CHECKS),
        "missing_checks":missing,
        "incomplete_checks":incomplete,
        "failed_checks":failed,
        "post_merge_healthy":healthy,
        "rollback_required":rollback,
        "policy":{
            "read_only":True,
            "automatic_rollback":False,
            "require_explicit_rollback_authorization":True,
        },
    }
