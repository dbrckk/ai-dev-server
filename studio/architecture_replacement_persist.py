"""Persist an explicitly approved architecture replacement as a content-bound branch and PR.

This module performs GitHub writes only when invoked directly with an approved promotion
review + PR package. It never merges the pull request.
"""
from __future__ import annotations

import base64
import json
import os
from pathlib import Path
import re
import urllib.error
import urllib.parse
import urllib.request

from core import canonical

class ReplacementPersistenceError(RuntimeError):
    pass

def _request(url, token, method="GET", payload=None, allow_404=False):
    data=None if payload is None else canonical(payload).encode("utf-8")
    req=urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Accept":"application/vnd.github+json",
            "Authorization":"Bearer "+token,
            "X-GitHub-Api-Version":"2022-11-28",
            "User-Agent":"ai-dev-server-replacement",
            "Content-Type":"application/json",
        },
    )
    try:
        with urllib.request.urlopen(req,timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if allow_404 and exc.code==404:
            return None
        raise ReplacementPersistenceError("GitHub replacement persistence request failed") from exc
    except (urllib.error.URLError,json.JSONDecodeError) as exc:
        raise ReplacementPersistenceError("GitHub replacement persistence request failed") from exc

def _valid_repository(value):
    return isinstance(value,str) and re.fullmatch(r"[^/]+/[^/]+",value) is not None

def _sha(value,label):
    if not isinstance(value,str) or not re.fullmatch(r"[0-9a-f]{40}",value):
        raise ReplacementPersistenceError(label+" SHA invalid")
    return value

def _load_candidate(path: Path):
    try:
        value=json.loads(path.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError):
        raise ReplacementPersistenceError("replacement candidate unreadable") from None
    if not isinstance(value,dict) or value.get("status")!="replacement_candidate_validated":
        raise ReplacementPersistenceError("replacement candidate invalid")
    return value

def _existing_pr(api, token, owner, branch, head_sha):
    query=urllib.parse.urlencode({
        "state":"all",
        "head":owner+":"+branch,
        "base":"main",
        "per_page":20,
    })
    pulls=_request(api+"/pulls?"+query,token)
    if not isinstance(pulls,list):
        raise ReplacementPersistenceError("replacement PR lookup malformed")
    matches=[
        pr for pr in pulls
        if isinstance(pr,dict)
        and pr.get("head",{}).get("sha")==head_sha
        and pr.get("head",{}).get("ref")==branch
        and isinstance(pr.get("number"),int)
    ]
    if len(matches)>1:
        raise ReplacementPersistenceError("multiple matching replacement PRs")
    return matches[0]["number"] if matches else None

def persist(repo_root: Path, review: dict, package: dict, candidate_path: Path, token: str, repository: str):
    if not token:
        raise ReplacementPersistenceError("GitHub token missing")
    if not _valid_repository(repository):
        raise ReplacementPersistenceError("GitHub repository invalid")
    if review.get("status")!="promotion_review_ready":
        raise ReplacementPersistenceError("promotion review not ready")
    if package.get("status")!="pr_package_ready":
        raise ReplacementPersistenceError("PR package not ready")
    if package.get("work_order_id")!=review.get("work_order_id"):
        raise ReplacementPersistenceError("replacement package identity mismatch")
    if package.get("candidate_digest")!=review.get("candidate_digest"):
        raise ReplacementPersistenceError("replacement candidate digest mismatch")
    if package.get("policy",{}).get("perform_network_actions") is not False:
        raise ReplacementPersistenceError("PR package policy malformed")
    if package.get("policy",{}).get("merge_pull_request") is not False:
        raise ReplacementPersistenceError("replacement PR package cannot permit merge")

    baseline_sha=_sha(package.get("baseline_sha"),"Baseline")
    candidate_sha=_sha(package.get("candidate_sha"),"Candidate")
    branch=package.get("branch")
    if not isinstance(branch,str) or not branch.startswith("architecture/replacement-"):
        raise ReplacementPersistenceError("replacement branch invalid")

    root=repo_root.resolve()
    candidate=_load_candidate(candidate_path)
    if candidate.get("work_order_id")!=review.get("work_order_id"):
        raise ReplacementPersistenceError("replacement candidate identity mismatch")

    api="https://api.github.com/repos/"+repository
    owner=repository.split("/",1)[0]
    base_commit=_request(api+"/git/commits/"+baseline_sha,token)
    base_tree=base_commit.get("tree",{}).get("sha") if isinstance(base_commit,dict) else None
    if not isinstance(base_tree,str):
        raise ReplacementPersistenceError("baseline tree missing")

    tree_entries=[]
    for item in candidate.get("files",[]):
        if not isinstance(item,dict) or not isinstance(item.get("path"),str) or not isinstance(item.get("content"),str):
            raise ReplacementPersistenceError("replacement candidate file malformed")
        blob=_request(api+"/git/blobs",token,"POST",{
            "content":base64.b64encode(item["content"].encode("utf-8")).decode("ascii"),
            "encoding":"base64",
        })
        blob_sha=blob.get("sha") if isinstance(blob,dict) else None
        if not isinstance(blob_sha,str):
            raise ReplacementPersistenceError("replacement blob creation failed")
        tree_entries.append({
            "path":item["path"],
            "mode":"100644",
            "type":"blob",
            "sha":blob_sha,
        })

    tree=_request(api+"/git/trees",token,"POST",{"base_tree":base_tree,"tree":tree_entries})
    tree_sha=tree.get("sha") if isinstance(tree,dict) else None
    if not isinstance(tree_sha,str):
        raise ReplacementPersistenceError("replacement tree creation failed")

    commit=_request(api+"/git/commits",token,"POST",{
        "message":package.get("title","Architecture replacement"),
        "tree":tree_sha,
        "parents":[baseline_sha],
    })
    commit_sha=commit.get("sha") if isinstance(commit,dict) else None
    if not isinstance(commit_sha,str) or not re.fullmatch(r"[0-9a-f]{40}",commit_sha):
        raise ReplacementPersistenceError("replacement commit creation failed")

    # The isolated executor candidate SHA is local-only. The GitHub commit is content-bound
    # by the candidate digest + branch identity, not required to equal the local commit SHA.
    _request(api+"/git/refs",token,"POST",{"ref":"refs/heads/"+branch,"sha":commit_sha})
    existing=_existing_pr(api,token,owner,branch,commit_sha)
    if existing is not None:
        return {
            "status":"replacement_pr_already_exists",
            "work_order_id":review.get("work_order_id"),
            "branch":branch,
            "commit_sha":commit_sha,
            "pull_request":existing,
            "merged":False,
        }

    body=package.get("body",{})
    pr=_request(api+"/pulls",token,"POST",{
        "title":package.get("title","Architecture replacement"),
        "head":branch,
        "base":"main",
        "body":canonical(body),
        "draft":True,
    })
    number=pr.get("number") if isinstance(pr,dict) else None
    if not isinstance(number,int):
        raise ReplacementPersistenceError("replacement pull request creation failed")
    return {
        "status":"replacement_pr_created",
        "work_order_id":review.get("work_order_id"),
        "branch":branch,
        "commit_sha":commit_sha,
        "pull_request":number,
        "draft":True,
        "merged":False,
    }

def main(argv=None):
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("review")
    parser.add_argument("package")
    parser.add_argument("candidate")
    parser.add_argument("--repo-root",default=".")
    parser.add_argument("--out",default="studio-output")
    args=parser.parse_args(argv)
    out=Path(args.out)
    out.mkdir(parents=True,exist_ok=True)
    try:
        review=json.loads(Path(args.review).read_text(encoding="utf-8"))
        package=json.loads(Path(args.package).read_text(encoding="utf-8"))
        result=persist(
            Path(args.repo_root),
            review,
            package,
            Path(args.candidate),
            os.environ.get("STUDIO_GITHUB_TOKEN",""),
            os.environ.get("GITHUB_REPOSITORY",""),
        )
        (out/"architecture-replacement-persisted.json").write_text(
            canonical(result)+"\n",encoding="utf-8"
        )
        print(canonical(result))
        return 0
    except (OSError,ValueError,json.JSONDecodeError,ReplacementPersistenceError):
        (out/"architecture-replacement-persist-error.json").write_text(
            canonical({"status":"replacement_persistence_blocked"})+"\n",encoding="utf-8"
        )
        return 1

if __name__=="__main__":
    raise SystemExit(main())
