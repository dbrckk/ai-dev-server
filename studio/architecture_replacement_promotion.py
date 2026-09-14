"""Trusted review controller for isolated architecture replacement evidence.

This controller never modifies the repository, never pushes, and never merges.
It deterministically re-checks the replacement evidence and emits a promotion-review
package only when every required identity and safety condition still holds.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

from core import canonical

class ReplacementPromotionError(RuntimeError):
    pass

def _sha(value, label):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{40}", value):
        raise ReplacementPromotionError(label+" SHA invalid")
    return value

def _candidate_digest(candidate: dict) -> str:
    files=candidate.get("files")
    if not isinstance(files,list) or not files:
        raise ReplacementPromotionError("candidate files missing")
    payload={
        "work_order_id":candidate.get("work_order_id"),
        "current_repo":candidate.get("current_repo"),
        "replacement_repo":candidate.get("replacement_repo"),
        "baseline_sha":candidate.get("baseline_sha"),
        "files":[
            {
                "path":item.get("path"),
                "sha256":hashlib.sha256(item.get("content","").encode("utf-8")).hexdigest(),
            }
            for item in sorted(files,key=lambda x:x.get("path",""))
            if isinstance(item,dict) and isinstance(item.get("path"),str) and isinstance(item.get("content"),str)
        ],
    }
    if len(payload["files"])!=len(files):
        raise ReplacementPromotionError("candidate file set malformed")
    return hashlib.sha256(
        json.dumps(payload,sort_keys=True,separators=(",",":")).encode("utf-8")
    ).hexdigest()

def review(work_order: dict, candidate: dict, execution: dict) -> dict:
    if not isinstance(work_order,dict) or not isinstance(candidate,dict) or not isinstance(execution,dict):
        raise ReplacementPromotionError("promotion inputs malformed")
    if candidate.get("status")!="replacement_candidate_validated":
        raise ReplacementPromotionError("candidate is not validated")
    if execution.get("status")!="replacement_isolated_benchmark_complete":
        raise ReplacementPromotionError("isolated execution evidence missing")

    order_id=work_order.get("id")
    if not isinstance(order_id,str) or not order_id:
        raise ReplacementPromotionError("work order id missing")
    if candidate.get("work_order_id")!=order_id or execution.get("work_order_id")!=order_id:
        raise ReplacementPromotionError("work order identity mismatch")

    current=work_order.get("current_repo")
    replacement=work_order.get("replacement_repo")
    if candidate.get("current_repo")!=current or execution.get("current_repo")!=current:
        raise ReplacementPromotionError("current repository mismatch")
    if candidate.get("replacement_repo")!=replacement or execution.get("replacement_repo")!=replacement:
        raise ReplacementPromotionError("replacement repository mismatch")

    baseline=_sha(candidate.get("baseline_sha"),"Baseline")
    if execution.get("baseline_sha")!=baseline:
        raise ReplacementPromotionError("baseline evidence mismatch")
    candidate_sha=_sha(execution.get("candidate_sha"),"Candidate")

    if execution.get("go_no_go")!="GO_FOR_MANUAL_PROMOTION_REVIEW":
        raise ReplacementPromotionError("candidate did not pass isolated promotion gate")
    if execution.get("network")!="disabled":
        raise ReplacementPromotionError("candidate network isolation not proven")
    if execution.get("credentials_exposed_to_candidate") is not False:
        raise ReplacementPromotionError("credential isolation not proven")
    if execution.get("default_branch_modified") is not False:
        raise ReplacementPromotionError("default branch immutability not proven")
    if execution.get("reversible") is not True:
        raise ReplacementPromotionError("rollback reversibility not proven")

    baseline_validation=execution.get("baseline_validation")
    candidate_validation=execution.get("candidate_validation")
    if not isinstance(baseline_validation,dict) or baseline_validation.get("passed") is not True:
        raise ReplacementPromotionError("baseline validation not clean")
    if not isinstance(candidate_validation,dict) or candidate_validation.get("passed") is not True:
        raise ReplacementPromotionError("candidate validation not clean")

    required=work_order.get("required_gates")
    required=[x for x in required if isinstance(x,str)] if isinstance(required,list) else []

    return {
        "version":1,
        "status":"promotion_review_ready",
        "work_order_id":order_id,
        "current_repo":current,
        "replacement_repo":replacement,
        "baseline_sha":baseline,
        "candidate_sha":candidate_sha,
        "candidate_digest":_candidate_digest(candidate),
        "changed_files":[
            x for x in execution.get("changed_files",[]) if isinstance(x,str)
        ][:128],
        "required_gates":required[:16],
        "evidence":{
            "baseline_validation_passed":True,
            "candidate_validation_passed":True,
            "reversible":True,
            "network_disabled":True,
            "credentials_exposed":False,
            "default_branch_modified":False,
        },
        "decision":"READY_FOR_EXPLICIT_PROMOTION_ACTION",
        "policy":{
            "auto_push":False,
            "auto_open_pull_request":False,
            "auto_merge":False,
            "require_explicit_promotion_action":True,
            "require_content_bound_pr":True,
            "require_rollback_record":True,
        },
    }

def write(work_order: dict, candidate: dict, execution: dict, out: Path) -> dict:
    out.mkdir(parents=True,exist_ok=True)
    result=review(work_order,candidate,execution)
    (out/"architecture-replacement-promotion-review.json").write_text(
        canonical(result)+"\n",encoding="utf-8"
    )
    return result
