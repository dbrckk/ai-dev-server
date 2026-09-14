"""Finalize post-merge replacement evidence and update empirical replacement learning.

Read-only with respect to GitHub. It verifies the exact merge, records a durable outcome,
updates the bounded historical learning file, and emits a rollback gate when regression
evidence requires one.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

from architecture_learning import root_for_output
from architecture_replacement_postmerge import verify as verify_postmerge, ReplacementPostMergeError
from architecture_replacement_outcome import write as write_replacement_outcome
from architecture_replacement_learning import summarize as summarize_replacement_learning
from architecture_replacement_rollback_gate import write as write_rollback_gate, ReplacementRollbackGateError
from core import canonical

def _load(path: Path, label: str) -> dict:
    try:
        value=json.loads(path.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError):
        raise ValueError(label+" unreadable") from None
    if not isinstance(value,dict):
        raise ValueError(label+" malformed")
    return value

def run(work_order_path: Path, merged_path: Path, package_path: Path, out: Path, token: str, repository: str) -> dict:
    work_order=_load(work_order_path,"work order")
    merged=_load(merged_path,"merged evidence")
    package=_load(package_path,"PR package")

    postmerge=verify_postmerge(merged,package,token,repository)
    out.mkdir(parents=True,exist_ok=True)
    (out/"architecture-replacement-postmerge.json").write_text(
        canonical(postmerge)+"\n",encoding="utf-8"
    )

    rollback_gate=None
    if postmerge.get("rollback_required") is True:
        rollback_gate=write_rollback_gate(postmerge,merged,package,out)

    terminal=postmerge.get("status") in {"post_merge_healthy","post_merge_regression"}
    outcome=None
    if terminal:
        outcome=write_replacement_outcome(work_order,merged,postmerge,out)
    learning=summarize_replacement_learning(root_for_output(out))
    (root_for_output(out)/"architecture-replacement-learning.json").write_text(
        json.dumps(learning,ensure_ascii=False,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )

    return {
        "version":1,
        "status":"replacement_postmerge_pipeline_complete",
        "postmerge_status":postmerge.get("status"),
        "replacement_outcome":outcome.get("successful") if isinstance(outcome,dict) else None,
        "replacement_learning_samples":next((
            row.get("samples")
            for row in learning.get("rankings",[])
            if row.get("current_repo")==work_order.get("current_repo")
            and row.get("replacement_repo")==work_order.get("replacement_repo")
        ),0),
        "rollback_gate_status":rollback_gate.get("status") if isinstance(rollback_gate,dict) else "not_required",
    }

def main(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument("work_order")
    parser.add_argument("merged")
    parser.add_argument("package")
    parser.add_argument("--out",default="studio-output")
    args=parser.parse_args(argv)
    out=Path(args.out)
    try:
        result=run(
            Path(args.work_order),
            Path(args.merged),
            Path(args.package),
            out,
            os.environ.get("STUDIO_GITHUB_TOKEN",""),
            os.environ.get("GITHUB_REPOSITORY",""),
        )
        (out/"architecture-replacement-postmerge-pipeline.json").write_text(
            canonical(result)+"\n",encoding="utf-8"
        )
        print(canonical(result))
        return 0 if result["postmerge_status"] in {"post_merge_healthy","awaiting_post_merge_checks","awaiting_main_head"} else 1
    except (OSError,ValueError,json.JSONDecodeError,ReplacementPostMergeError,ReplacementRollbackGateError):
        out.mkdir(parents=True,exist_ok=True)
        (out/"architecture-replacement-postmerge-pipeline-error.json").write_text(
            canonical({"status":"replacement_postmerge_pipeline_blocked"})+"\n",
            encoding="utf-8",
        )
        return 1

if __name__=="__main__":
    sys.exit(main())
