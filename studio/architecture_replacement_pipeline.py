"""Manual/explicit replacement pipeline: synthesize candidate, then benchmark it in isolation.

This module never promotes or merges. It is intentionally not called automatically by
orchestrator.py. It can be invoked only with an explicit work-order path.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from architecture_replacement_synthesis import consume as synthesize_candidate
from architecture_replacement_executor import execute as execute_candidate, ReplacementExecutionError
from architecture_replacement_candidate import ReplacementCandidateRejected
from core import StudioError, canonical

def run(work_order_path: Path, repo_root: Path, out: Path) -> dict:
    order=json.loads(work_order_path.read_text(encoding="utf-8"))
    candidate=synthesize_candidate(work_order_path,repo_root,out)
    execution=execute_candidate(repo_root,order,candidate,out)
    result={
        "version":1,
        "status":"replacement_pipeline_complete",
        "work_order_id":order.get("id"),
        "candidate_status":candidate.get("status"),
        "execution_status":execution.get("status"),
        "go_no_go":execution.get("go_no_go"),
        "auto_promoted":False,
        "default_branch_modified":False,
    }
    (out/"architecture-replacement-pipeline.json").write_text(
        canonical(result)+"\n",encoding="utf-8"
    )
    return result

def main(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument("work_order")
    parser.add_argument("--repo-root",default=".")
    parser.add_argument("--out",default="studio-output")
    args=parser.parse_args(argv)
    out=Path(args.out)
    try:
        result=run(Path(args.work_order),Path(args.repo_root),out)
    except (OSError,ValueError,json.JSONDecodeError,ReplacementExecutionError,ReplacementCandidateRejected,StudioError):
        out.mkdir(parents=True,exist_ok=True)
        (out/"architecture-replacement-pipeline-error.json").write_text(
            canonical({"status":"replacement_pipeline_blocked"})+"\n",encoding="utf-8"
        )
        return 1
    print(canonical(result))
    return 0 if result.get("go_no_go")=="GO_FOR_MANUAL_PROMOTION_REVIEW" else 1

if __name__=="__main__":
    sys.exit(main())
