"""Explicit GitHub rollback executor for a regressed architecture replacement.

Creates a revert commit and a draft rollback PR. It never force-pushes main and never merges
the rollback automatically.
"""
from __future__ import annotations
import json
import os
import re
from pathlib import Path
from architecture_replacement_persist import _request
from core import canonical

class ReplacementRollbackError(RuntimeError):
    pass

def _verify(gate,authorization):
    if not isinstance(gate,dict) or gate.get("status")!="rollback_authorization_required":
        raise ReplacementRollbackError("rollback gate invalid")
    if not isinstance(authorization,dict) or authorization.get("status")!="explicit_rollback_authorization" or authorization.get("authorized") is not True:
        raise ReplacementRollbackError("explicit rollback authorization absent")
    for key in ("authorization_id","work_order_id","merge_sha"):
        if authorization.get(key)!=gate.get(key):
            raise ReplacementRollbackError("rollback authorization identity mismatch: "+key)

def execute(gate,authorization,token,repository,requester=_request):
    if not token:
        raise ReplacementRollbackError("GitHub token missing")
    if not isinstance(repository,str) or repository.count("/")!=1:
        raise ReplacementRollbackError("GitHub repository invalid")
    _verify(gate,authorization)
    merge_sha=gate.get("merge_sha")
    if not isinstance(merge_sha,str) or not re.fullmatch(r"[0-9a-f]{40}",merge_sha):
        raise ReplacementRollbackError("merge SHA invalid")
    api="https://api.github.com/repos/"+repository

    branch=requester(api+"/branches/main",token)
    main_sha=branch.get("commit",{}).get("sha") if isinstance(branch,dict) else None
    if main_sha!=merge_sha:
        raise ReplacementRollbackError("main advanced after replacement merge; automatic revert preparation blocked")

    merge_commit=requester(api+"/git/commits/"+merge_sha,token)
    parents=merge_commit.get("parents") if isinstance(merge_commit,dict) else None
    parent_shas=[x.get("sha") for x in parents] if isinstance(parents,list) else []
    baseline=gate.get("baseline_sha")
    if not isinstance(baseline,str) or baseline not in parent_shas:
        raise ReplacementRollbackError("approved baseline is not a merge parent")

    baseline_commit=requester(api+"/git/commits/"+baseline,token)
    baseline_tree=baseline_commit.get("tree",{}).get("sha") if isinstance(baseline_commit,dict) else None
    if not isinstance(baseline_tree,str):
        raise ReplacementRollbackError("baseline tree unavailable")

    revert=requester(api+"/git/commits",token,"POST",{
        "message":"Revert regressed architecture replacement "+str(gate.get("work_order_id")),
        "tree":baseline_tree,
        "parents":[merge_sha],
    })
    revert_sha=revert.get("sha") if isinstance(revert,dict) else None
    if not isinstance(revert_sha,str) or not re.fullmatch(r"[0-9a-f]{40}",revert_sha):
        raise ReplacementRollbackError("rollback commit creation failed")

    branch_name="architecture/rollback-"+gate["authorization_id"][:16]+"-"+revert_sha
    requester(api+"/git/refs",token,"POST",{"ref":"refs/heads/"+branch_name,"sha":revert_sha})
    pr=requester(api+"/pulls",token,"POST",{
        "title":"Rollback architecture replacement "+str(gate.get("work_order_id")),
        "head":branch_name,
        "base":"main",
        "draft":True,
        "body":canonical({
            "reason":gate.get("reason"),
            "reverted_merge_sha":merge_sha,
            "restored_baseline_sha":baseline,
            "authorization_id":gate.get("authorization_id"),
            "policy":"Explicitly authorized rollback preparation; draft PR only, no automatic merge.",
        }),
    })
    number=pr.get("number") if isinstance(pr,dict) else None
    if not isinstance(number,int):
        raise ReplacementRollbackError("rollback PR creation failed")
    return {
        "version":1,
        "status":"replacement_rollback_pr_created",
        "work_order_id":gate.get("work_order_id"),
        "rollback_branch":branch_name,
        "rollback_commit_sha":revert_sha,
        "pull_request":number,
        "draft":True,
        "merged":False,
        "restores_baseline_sha":baseline,
    }

def main(argv=None):
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("gate"); parser.add_argument("authorization")
    parser.add_argument("--out",default="studio-output")
    args=parser.parse_args(argv); out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
    try:
        gate=json.loads(Path(args.gate).read_text(encoding="utf-8"))
        authorization=json.loads(Path(args.authorization).read_text(encoding="utf-8"))
        result=execute(gate,authorization,os.environ.get("STUDIO_GITHUB_TOKEN",""),os.environ.get("GITHUB_REPOSITORY",""))
        (out/"architecture-replacement-rollback.json").write_text(canonical(result)+"\n",encoding="utf-8")
        print(canonical(result)); return 0
    except (OSError,ValueError,json.JSONDecodeError,ReplacementRollbackError):
        (out/"architecture-replacement-rollback-error.json").write_text(canonical({"status":"replacement_rollback_blocked"})+"\n",encoding="utf-8")
        return 1

if __name__=="__main__":
    raise SystemExit(main())
