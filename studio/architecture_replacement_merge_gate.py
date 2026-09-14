"""Create a content-bound merge authorization template after PR validation.

This module is read-only. It does not call GitHub and does not merge. Its output can only
be consumed by the explicit merge executor after a separate authorization record is supplied.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

from core import canonical

class ReplacementMergeGateError(RuntimeError):
    pass

def _sha(value,label):
    if not isinstance(value,str) or not re.fullmatch(r"[0-9a-f]{40}",value):
        raise ReplacementMergeGateError(label+" SHA invalid")
    return value

def build(validation: dict, review: dict, package: dict, persisted: dict) -> dict:
    if not all(isinstance(x,dict) for x in (validation,review,package,persisted)):
        raise ReplacementMergeGateError("merge gate inputs malformed")
    if validation.get("status")!="ready_to_merge" or validation.get("ready_to_merge") is not True:
        raise ReplacementMergeGateError("replacement PR is not merge-ready")
    if validation.get("draft") is True or validation.get("mergeable_clean") is not True:
        raise ReplacementMergeGateError("replacement PR state is not clean")
    if review.get("status")!="promotion_review_ready":
        raise ReplacementMergeGateError("promotion review not ready")
    if package.get("status")!="pr_package_ready":
        raise ReplacementMergeGateError("PR package not ready")
    if persisted.get("status") not in {"replacement_pr_created","replacement_pr_already_exists"}:
        raise ReplacementMergeGateError("persistence evidence invalid")

    number=validation.get("pull_request")
    branch=validation.get("branch")
    head_sha=_sha(validation.get("head_sha"),"Head")
    if not isinstance(number,int) or not isinstance(branch,str):
        raise ReplacementMergeGateError("merge identity incomplete")
    if persisted.get("pull_request")!=number or persisted.get("branch")!=branch or persisted.get("commit_sha")!=head_sha:
        raise ReplacementMergeGateError("persisted PR proof changed")
    if package.get("branch")!=branch:
        raise ReplacementMergeGateError("package branch mismatch")

    work_order_id=review.get("work_order_id")
    if package.get("work_order_id")!=work_order_id or persisted.get("work_order_id")!=work_order_id:
        raise ReplacementMergeGateError("work order identity mismatch")

    payload={
        "work_order_id":work_order_id,
        "pull_request":number,
        "branch":branch,
        "head_sha":head_sha,
        "candidate_digest":review.get("candidate_digest"),
    }
    authorization_id=hashlib.sha256(
        json.dumps(payload,sort_keys=True,separators=(",",":")).encode("utf-8")
    ).hexdigest()

    return {
        "version":1,
        "status":"merge_authorization_required",
        **payload,
        "authorization_id":authorization_id,
        "merge_method":"merge",
        "authorization_template":{
            "version":1,
            "status":"explicit_merge_authorization",
            "authorization_id":authorization_id,
            "work_order_id":work_order_id,
            "pull_request":number,
            "branch":branch,
            "head_sha":head_sha,
            "authorized":False,
        },
        "policy":{
            "auto_merge":False,
            "network_write":False,
            "require_explicit_authorization":True,
            "require_head_sha_revalidation":True,
            "require_clean_merge_state_revalidation":True,
        },
    }

def write(validation: dict, review: dict, package: dict, persisted: dict, out: Path) -> dict:
    out.mkdir(parents=True,exist_ok=True)
    result=build(validation,review,package,persisted)
    (out/"architecture-replacement-merge-gate.json").write_text(
        canonical(result)+"\n",encoding="utf-8"
    )
    return result
