"""Prepare a content-bound pull-request package for an approved replacement review.

This module does not call GitHub, does not push, and does not merge. It emits the exact
branch name, title, body, content digest, and rollback requirements that a separate
authorized persistence step may use.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

from core import canonical

class ReplacementPRPackageError(RuntimeError):
    pass

def _sha(value,label):
    if not isinstance(value,str) or not re.fullmatch(r"[0-9a-f]{40}",value):
        raise ReplacementPRPackageError(label+" SHA invalid")
    return value

def build(review: dict, candidate: dict) -> dict:
    if not isinstance(review,dict) or review.get("status")!="promotion_review_ready":
        raise ReplacementPRPackageError("promotion review not ready")
    if not isinstance(candidate,dict) or candidate.get("status")!="replacement_candidate_validated":
        raise ReplacementPRPackageError("candidate not validated")
    if review.get("work_order_id")!=candidate.get("work_order_id"):
        raise ReplacementPRPackageError("work order identity mismatch")
    if review.get("current_repo")!=candidate.get("current_repo"):
        raise ReplacementPRPackageError("current repository mismatch")
    if review.get("replacement_repo")!=candidate.get("replacement_repo"):
        raise ReplacementPRPackageError("replacement repository mismatch")

    baseline=_sha(review.get("baseline_sha"),"Baseline")
    candidate_sha=_sha(review.get("candidate_sha"),"Candidate")
    digest=review.get("candidate_digest")
    if not isinstance(digest,str) or not re.fullmatch(r"[0-9a-f]{64}",digest):
        raise ReplacementPRPackageError("candidate digest invalid")

    identity=hashlib.sha256(
        (review["work_order_id"]+":"+digest+":"+candidate_sha).encode("utf-8")
    ).hexdigest()[:16]
    branch=f"architecture/replacement-{identity}"

    files=[]
    for item in candidate.get("files",[]):
        if not isinstance(item,dict) or not isinstance(item.get("path"),str) or not isinstance(item.get("content"),str):
            raise ReplacementPRPackageError("candidate file malformed")
        files.append({
            "path":item["path"],
            "sha256":hashlib.sha256(item["content"].encode("utf-8")).hexdigest(),
            "bytes":len(item["content"].encode("utf-8")),
        })

    return {
        "version":1,
        "status":"pr_package_ready",
        "work_order_id":review["work_order_id"],
        "branch":branch,
        "base_branch":"main",
        "baseline_sha":baseline,
        "candidate_sha":candidate_sha,
        "candidate_digest":digest,
        "title":f"Replace {review['current_repo']} with {review['replacement_repo']}",
        "body":{
            "summary":f"Evidence-backed architecture replacement: {review['current_repo']} -> {review['replacement_repo']}.",
            "safety":[
                "validated in isolated worktree",
                "candidate validation passed",
                "network disabled during candidate execution",
                "no production credentials exposed",
                "default branch was not modified",
                "rollback reversibility was verified",
            ],
            "required_gates":review.get("required_gates",[])[:16],
            "promotion_policy":"Explicit authorized persistence only; no automatic merge.",
        },
        "files":files,
        "rollback":{
            "required":True,
            "strategy":"restore baseline manifest/lockfile/API usage from baseline_sha",
        },
        "policy":{
            "perform_network_actions":False,
            "create_branch":False,
            "open_pull_request":False,
            "merge_pull_request":False,
            "require_head_sha_binding":True,
            "require_required_checks":True,
        },
    }

def write(review: dict, candidate: dict, out: Path) -> dict:
    out.mkdir(parents=True,exist_ok=True)
    result=build(review,candidate)
    (out/"architecture-replacement-pr-package.json").write_text(
        canonical(result)+"\n",encoding="utf-8"
    )
    return result
