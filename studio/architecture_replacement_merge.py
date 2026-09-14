"""Explicit architecture replacement merge executor.

This is the only replacement component allowed to call GitHub's merge endpoint. It requires
an explicit authorization record bound to the exact PR head SHA and revalidates the PR,
trusted checks, file scope/content, and clean merge state immediately before merging.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from architecture_replacement_persist import _request
from architecture_replacement_pr_validator import validate as validate_pr, ReplacementPRValidationError
from architecture_replacement_merge_gate import ReplacementMergeGateError
from core import canonical

class ReplacementMergeError(RuntimeError):
    pass

def _verify_authorization(gate: dict, authorization: dict) -> None:
    if not isinstance(gate,dict) or gate.get("status")!="merge_authorization_required":
        raise ReplacementMergeError("merge gate invalid")
    if not isinstance(authorization,dict):
        raise ReplacementMergeError("merge authorization missing")
    if authorization.get("status")!="explicit_merge_authorization" or authorization.get("authorized") is not True:
        raise ReplacementMergeError("explicit merge authorization absent")
    for key in ("authorization_id","work_order_id","pull_request","branch","head_sha"):
        if authorization.get(key)!=gate.get(key):
            raise ReplacementMergeError("merge authorization identity mismatch: "+key)

def merge(
    review: dict,
    package: dict,
    persisted: dict,
    gate: dict,
    authorization: dict,
    token: str,
    repository: str,
    requester=_request,
) -> dict:
    if not token:
        raise ReplacementMergeError("GitHub token missing")
    _verify_authorization(gate,authorization)

    try:
        validation=validate_pr(review,package,persisted,token,repository,requester=requester)
    except ReplacementPRValidationError as exc:
        raise ReplacementMergeError("replacement PR revalidation failed") from exc
    if validation.get("status")!="ready_to_merge" or validation.get("ready_to_merge") is not True:
        raise ReplacementMergeError("replacement PR is no longer merge-ready")
    for key in ("pull_request","branch","head_sha"):
        if validation.get(key)!=gate.get(key):
            raise ReplacementMergeError("replacement PR proof changed before merge: "+key)

    api="https://api.github.com/repos/"+repository
    number=gate["pull_request"]
    head_sha=gate["head_sha"]

    # Final TOCTOU re-read immediately before the write.
    pr=requester(api+"/pulls/"+str(number),token)
    if not isinstance(pr,dict) or pr.get("state")!="open" or pr.get("draft") is True:
        raise ReplacementMergeError("replacement PR is no longer open and ready")
    if pr.get("head",{}).get("sha")!=head_sha or pr.get("head",{}).get("ref")!=gate.get("branch"):
        raise ReplacementMergeError("replacement PR head changed before merge")
    if pr.get("base",{}).get("ref")!="main":
        raise ReplacementMergeError("replacement PR base changed before merge")
    if pr.get("mergeable") is not True or pr.get("mergeable_state")!="clean":
        raise ReplacementMergeError("replacement PR is no longer cleanly mergeable")

    result=requester(
        api+"/pulls/"+str(number)+"/merge",
        token,
        "PUT",
        {
            "sha":head_sha,
            "merge_method":"merge",
            "commit_title":package.get("title","Architecture replacement"),
        },
    )
    if not isinstance(result,dict) or result.get("merged") is not True:
        raise ReplacementMergeError("GitHub refused replacement merge")

    return {
        "version":1,
        "status":"replacement_merged",
        "work_order_id":gate.get("work_order_id"),
        "pull_request":number,
        "branch":gate.get("branch"),
        "head_sha":head_sha,
        "merge_sha":result.get("sha"),
        "authorization_id":gate.get("authorization_id"),
        "explicit_authorization_verified":True,
    }

def main(argv=None):
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("review")
    parser.add_argument("package")
    parser.add_argument("persisted")
    parser.add_argument("gate")
    parser.add_argument("authorization")
    parser.add_argument("--out",default="studio-output")
    args=parser.parse_args(argv)
    out=Path(args.out)
    out.mkdir(parents=True,exist_ok=True)
    try:
        review=json.loads(Path(args.review).read_text(encoding="utf-8"))
        package=json.loads(Path(args.package).read_text(encoding="utf-8"))
        persisted=json.loads(Path(args.persisted).read_text(encoding="utf-8"))
        gate=json.loads(Path(args.gate).read_text(encoding="utf-8"))
        authorization=json.loads(Path(args.authorization).read_text(encoding="utf-8"))
        result=merge(
            review,package,persisted,gate,authorization,
            os.environ.get("STUDIO_GITHUB_TOKEN",""),
            os.environ.get("GITHUB_REPOSITORY",""),
        )
        (out/"architecture-replacement-merged.json").write_text(
            canonical(result)+"\n",encoding="utf-8"
        )
        print(canonical(result))
        return 0
    except (OSError,ValueError,json.JSONDecodeError,ReplacementMergeError):
        (out/"architecture-replacement-merge-error.json").write_text(
            canonical({"status":"replacement_merge_blocked"})+"\n",encoding="utf-8"
        )
        return 1

if __name__=="__main__":
    raise SystemExit(main())
