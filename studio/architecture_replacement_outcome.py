"""Record post-merge replacement outcomes for empirical replacement learning."""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

from atomic_file import write_text as atomic_write_text

def _identity(work_order: dict, merged: dict) -> str:
    payload={
        "work_order_id":work_order.get("id"),
        "current_repo":work_order.get("current_repo"),
        "replacement_repo":work_order.get("replacement_repo"),
        "merge_sha":merged.get("merge_sha"),
    }
    return hashlib.sha256(
        json.dumps(payload,sort_keys=True,separators=(",",":")).encode("utf-8")
    ).hexdigest()

def build(work_order: dict, merged: dict, postmerge: dict, rollback: dict | None = None) -> dict:
    if not all(isinstance(x,dict) for x in (work_order,merged,postmerge)):
        raise ValueError("replacement outcome inputs malformed")
    if merged.get("status")!="replacement_merged":
        raise ValueError("replacement merge evidence invalid")
    if merged.get("work_order_id")!=work_order.get("id") or postmerge.get("work_order_id")!=work_order.get("id"):
        raise ValueError("replacement outcome identity mismatch")

    healthy=postmerge.get("status")=="post_merge_healthy" and postmerge.get("post_merge_healthy") is True
    regressed=postmerge.get("status")=="post_merge_regression" or postmerge.get("rollback_required") is True
    rollback_prepared=isinstance(rollback,dict) and rollback.get("status")=="replacement_rollback_pr_created"
    rolled_back=isinstance(rollback,dict) and rollback.get("status")=="replacement_rollback_merged"

    if healthy:
        quality=100.0
    elif regressed:
        failed=len(postmerge.get("failed_checks",[])) if isinstance(postmerge.get("failed_checks"),list) else 0
        mismatches=len(postmerge.get("content_mismatches",[])) if isinstance(postmerge.get("content_mismatches"),list) else 0
        quality=max(0.0,30.0-10.0*failed-15.0*mismatches)
    else:
        quality=50.0

    return {
        "version":2,
        "status":"replacement_outcome_recorded",
        "replacement_id":_identity(work_order,merged),
        "observed_at":time.time(),
        "work_order_id":work_order.get("id"),
        "current_repo":work_order.get("current_repo"),
        "replacement_repo":work_order.get("replacement_repo"),
        "risk":work_order.get("risk"),
        "scope":work_order.get("scope"),
        "framework":work_order.get("framework"),
        "project_type":work_order.get("project_type"),
        "primary_domain":work_order.get("primary_domain"),
        "platform":work_order.get("platform"),
        "current_major_version":work_order.get("current_major_version"),
        "replacement_major_version":work_order.get("replacement_major_version"),
        "merge_sha":merged.get("merge_sha"),
        "successful":healthy,
        "regressed":regressed,
        "rollback_prepared":rollback_prepared,
        "rolled_back":rolled_back,
        "quality_score":round(quality,3),
        "postmerge_status":postmerge.get("status"),
        "failed_checks":postmerge.get("failed_checks",[])[:16] if isinstance(postmerge.get("failed_checks"),list) else [],
        "content_mismatches":postmerge.get("content_mismatches",[])[:32] if isinstance(postmerge.get("content_mismatches"),list) else [],
    }

def write(work_order: dict, merged: dict, postmerge: dict, out: Path, rollback: dict | None = None) -> dict:
    out.mkdir(parents=True,exist_ok=True)
    result=build(work_order,merged,postmerge,rollback=rollback)
    atomic_write_text(
        out/"architecture-replacement-outcome.json",
        json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    return result
