"""Persist verified strategy-efficiency memory."""
from __future__ import annotations

import base64
import json
from pathlib import Path

from strategy_efficiency import load as load_local, VALID_STRATEGIES

STATE_BRANCH = "studio-project-memory"
STATE_PATH = ".studio-memory/strategy-efficiency.json"
MAX_BYTES = 128 * 1024


class StrategyEfficiencyStoreError(RuntimeError):
    pass


def _validate(data):
    if not isinstance(data, dict):
        raise StrategyEfficiencyStoreError("strategy efficiency invalid")
    clean = {}
    for name, row in data.items():
        if name not in VALID_STRATEGIES or not isinstance(row, dict):
            raise StrategyEfficiencyStoreError("strategy efficiency entry invalid")
        if set(row) != {"samples", "successes", "ema_cost_seconds"}:
            raise StrategyEfficiencyStoreError("strategy efficiency fields invalid")
        samples=row["samples"]; successes=row["successes"]; cost=row["ema_cost_seconds"]
        if type(samples) is not int or samples < 0 or type(successes) is not int or successes < 0 or successes > samples:
            raise StrategyEfficiencyStoreError("strategy efficiency counters invalid")
        if not isinstance(cost,(int,float)) or isinstance(cost,bool) or cost < 0:
            raise StrategyEfficiencyStoreError("strategy efficiency cost invalid")
        clean[name]={"samples":samples,"successes":successes,"ema_cost_seconds":float(cost)}
    return clean


def _ref(github):
    refs=github.get("/git/matching-refs/heads/"+STATE_BRANCH)
    if not isinstance(refs,list):
        raise StrategyEfficiencyStoreError("memory branch lookup invalid")
    exact=[x for x in refs if isinstance(x,dict) and x.get("ref")=="refs/heads/"+STATE_BRANCH]
    if len(exact)>1:
        raise StrategyEfficiencyStoreError("memory branch ambiguous")
    return exact[0] if exact else None


def load(github):
    ref=_ref(github)
    if ref is None:
        return {}
    head=ref.get("object",{}).get("sha")
    if not isinstance(head,str) or len(head)!=40:
        raise StrategyEfficiencyStoreError("memory branch head invalid")
    tree=github.get("/git/trees/"+head+"?recursive=1")
    if not isinstance(tree,dict) or tree.get("truncated") or not isinstance(tree.get("tree"),list):
        raise StrategyEfficiencyStoreError("memory tree invalid")
    item=next((x for x in tree["tree"] if isinstance(x,dict) and x.get("path")==STATE_PATH and x.get("type")=="blob"),None)
    if item is None:
        return {}
    blob=github.get("/git/blobs/"+item.get("sha",""))
    if not isinstance(blob,dict) or blob.get("encoding")!="base64":
        raise StrategyEfficiencyStoreError("strategy efficiency blob invalid")
    try:
        raw=base64.b64decode(blob["content"],validate=False)
        if len(raw)>MAX_BYTES:
            raise StrategyEfficiencyStoreError("strategy efficiency too large")
        value=json.loads(raw.decode("utf-8"))
    except (KeyError,ValueError,UnicodeDecodeError,json.JSONDecodeError):
        raise StrategyEfficiencyStoreError("strategy efficiency unreadable") from None
    return _validate(value)


def save(github,data):
    data=_validate(data)
    ref=_ref(github)
    if ref is None:
        meta=github.get("")
        default=meta.get("default_branch") if isinstance(meta,dict) else None
        if not isinstance(default,str) or not default:
            raise StrategyEfficiencyStoreError("default branch invalid")
        info=github.get("/branches/"+default)
        parent=info.get("commit",{}).get("sha") if isinstance(info,dict) else None
    else:
        parent=ref.get("object",{}).get("sha")
        if load(github)==data:
            return parent
    if not isinstance(parent,str) or len(parent)!=40:
        raise StrategyEfficiencyStoreError("memory branch parent invalid")
    commit_info=github.get("/git/commits/"+parent)
    base_tree=commit_info.get("tree",{}).get("sha") if isinstance(commit_info,dict) else None
    if not isinstance(base_tree,str) or len(base_tree)!=40:
        raise StrategyEfficiencyStoreError("memory base tree invalid")
    tree=github.call("POST",github.repo+"/git/trees",{
        "base_tree":base_tree,
        "tree":[{"path":STATE_PATH,"mode":"100644","type":"blob","content":json.dumps(data,sort_keys=True)}],
    })
    tree_sha=tree.get("sha") if isinstance(tree,dict) else None
    if not isinstance(tree_sha,str) or len(tree_sha)!=40:
        raise StrategyEfficiencyStoreError("strategy efficiency tree creation failed")
    commit=github.call("POST",github.repo+"/git/commits",{
        "message":"Persist strategy efficiency memory",
        "tree":tree_sha,
        "parents":[parent],
    })
    commit_sha=commit.get("sha") if isinstance(commit,dict) else None
    if not isinstance(commit_sha,str) or len(commit_sha)!=40:
        raise StrategyEfficiencyStoreError("strategy efficiency commit creation failed")
    if ref is None:
        github.call("POST",github.repo+"/git/refs",{"ref":"refs/heads/"+STATE_BRANCH,"sha":commit_sha})
    else:
        github.call("PATCH",github.repo+"/git/refs/heads/"+STATE_BRANCH,{"sha":commit_sha,"force":False})
    return commit_sha


def restore_local(github,path:Path):
    data=load(github)
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    return data


def persist_local(github,path:Path):
    path=Path(path)
    data=load_local(path) if path.is_file() else {}
    return save(github,_validate(data))
