"""Prepare a content-bound rollback gate for a regressed architecture replacement.

No network writes. The gate binds a future explicit rollback authorization to the exact
merge commit, original replacement head, PR, work order, and approved pre-replacement base.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from core import canonical

class ReplacementRollbackGateError(RuntimeError):
    pass

def _sha(value,label):
    if not isinstance(value,str) or not re.fullmatch(r"[0-9a-f]{40}",value):
        raise ReplacementRollbackGateError(label+" SHA invalid")
    return value

def build(postmerge,merged,package):
    if not all(isinstance(x,dict) for x in (postmerge,merged,package)):
        raise ReplacementRollbackGateError("rollback gate inputs malformed")
    if postmerge.get("status")!="post_merge_regression" or postmerge.get("rollback_required") is not True:
        raise ReplacementRollbackGateError("rollback is not required by post-merge evidence")
    if merged.get("status")!="replacement_merged":
        raise ReplacementRollbackGateError("merge evidence invalid")
    if package.get("status")!="pr_package_ready":
        raise ReplacementRollbackGateError("replacement package invalid")
    if postmerge.get("work_order_id")!=merged.get("work_order_id") or merged.get("work_order_id")!=package.get("work_order_id"):
        raise ReplacementRollbackGateError("rollback work order identity mismatch")

    merge_sha=_sha(merged.get("merge_sha"),"Merge")
    head_sha=_sha(merged.get("head_sha"),"Replacement head")
    baseline_sha=_sha(package.get("baseline_sha"),"Baseline")
    payload={
        "work_order_id":merged.get("work_order_id"),
        "pull_request":merged.get("pull_request"),
        "merge_sha":merge_sha,
        "replacement_head_sha":head_sha,
        "baseline_sha":baseline_sha,
    }
    authorization_id=hashlib.sha256(
        json.dumps(payload,sort_keys=True,separators=(",",":")).encode("utf-8")
    ).hexdigest()
    return {
        "version":1,
        "status":"rollback_authorization_required",
        **payload,
        "authorization_id":authorization_id,
        "reason":{
            "failed_checks":postmerge.get("failed_checks",[]),
            "content_mismatches":postmerge.get("content_mismatches",[]),
        },
        "authorization_template":{
            "version":1,
            "status":"explicit_rollback_authorization",
            "authorization_id":authorization_id,
            "work_order_id":merged.get("work_order_id"),
            "merge_sha":merge_sha,
            "authorized":False,
        },
        "policy":{
            "automatic_rollback":False,
            "network_write":False,
            "require_explicit_authorization":True,
            "require_main_sha_revalidation":True,
        },
    }

def write(postmerge,merged,package,out:Path):
    out.mkdir(parents=True,exist_ok=True)
    result=build(postmerge,merged,package)
    (out/"architecture-replacement-rollback-gate.json").write_text(
        canonical(result)+"\n",encoding="utf-8"
    )
    return result
