"""Persist context-scoped strategy efficiency memory."""
from __future__ import annotations

import base64
import json
from pathlib import Path

from contextual_strategy_efficiency import load as load_local
from strategy_efficiency import VALID_STRATEGIES

STATE_BRANCH="studio-project-memory"
STATE_PATH=".studio-memory/contextual-strategy-efficiency.json"
MAX_BYTES=256*1024
MAX_CONTEXTS=16


class ContextualStrategyEfficiencyStoreError(RuntimeError):
    pass


def _validate(data):
    if not isinstance(data,dict) or len(data)>MAX_CONTEXTS:
        raise ContextualStrategyEfficiencyStoreError("contextual strategy efficiency invalid")
    clean={}
    for context,rows in data.items():
        if not isinstance(context,str) or not context or not isinstance(rows,dict):
            raise ContextualStrategyEfficiencyStoreError("contextual strategy context invalid")
        valid={}
        for strategy,row in rows.items():
            if strategy not in VALID_STRATEGIES or not isinstance(row,dict):
                raise ContextualStrategyEfficiencyStoreError("contextual strategy entry invalid")
            required={"samples","successes","ema_cost_seconds"}
            allowed=required|{"ema_success_rate"}
            if not required.issubset(row) or not set(row).issubset(allowed):
                raise ContextualStrategyEfficiencyStoreError("contextual strategy fields invalid")
            samples=row["samples"]; successes=row["successes"]; cost=row["ema_cost_seconds"]
            if type(samples) is not int or samples<0 or type(successes) is not int or successes<0 or successes>samples:
                raise ContextualStrategyEfficiencyStoreError("contextual strategy counters invalid")
            if not isinstance(cost,(int,float)) or isinstance(cost,bool) or cost<0:
                raise ContextualStrategyEfficiencyStoreError("contextual strategy cost invalid")
            fallback=(successes/samples) if samples else 0.0
            recent=row.get("ema_success_rate",fallback)
            if not isinstance(recent,(int,float)) or isinstance(recent,bool) or not 0.0<=float(recent)<=1.0:
                raise ContextualStrategyEfficiencyStoreError("contextual strategy recent success invalid")
            valid[strategy]={
                "samples":samples,
                "successes":successes,
                "ema_cost_seconds":float(cost),
                "ema_success_rate":float(recent),
            }
        clean[context]=valid
    return clean


def _ref(github):
    refs=github.get("/git/matching-refs/heads/"+STATE_BRANCH)
    if not isinstance(refs,list):
        raise ContextualStrategyEfficiencyStoreError("memory branch lookup invalid")
    exact=[x for x in refs if isinstance(x,dict) and x.get("ref")=="refs/heads/"+STATE_BRANCH]
    if len(exact)>1:
        raise ContextualStrategyEfficiencyStoreError("memory branch ambiguous")
    return exact[0] if exact else None


def load(github):
    ref=_ref(github)
    if ref is None:
        return {}
    head=ref.get("object",{}).get("sha")
    if not isinstance(head,str) or len(head)!=40:
        raise ContextualStrategyEfficiencyStoreError("memory branch head invalid")
    tree=github.get("/git/trees/"+head+"?recursive=1")
    if not isinstance(tree,dict) or tree.get("truncated") or not isinstance(tree.get("tree"),list):
        raise ContextualStrategyEfficiencyStoreError("memory tree invalid")
    item=next((x for x in tree["tree"] if isinstance(x,dict) and x.get("path")==STATE_PATH and x.get("type")=="blob"),None)
    if item is None:
        return {}
    blob=github.get("/git/blobs/"+item.get("sha",""))
    if not isinstance(blob,dict) or blob.get("encoding")!="base64":
        raise ContextualStrategyEfficiencyStoreError("contextual strategy blob invalid")
    try:
        raw=base64.b64decode(blob["content"],validate=False)
        if len(raw)>MAX_BYTES:
            raise ContextualStrategyEfficiencyStoreError("contextual strategy memory too large")
        value=json.loads(raw.decode("utf-8"))
    except (KeyError,ValueError,UnicodeDecodeError,json.JSONDecodeError):
        raise ContextualStrategyEfficiencyStoreError("contextual strategy memory unreadable") from None
    return _validate(value)


def save(github,data):
    data=_validate(data)
    ref=_ref(github)
    if ref is None:
        meta=github.get("")
        default=meta.get("default_branch") if isinstance(meta,dict) else None
        if not isinstance(default,str) or not default:
            raise ContextualStrategyEfficiencyStoreError("default branch invalid")
        info=github.get("/branches/"+default)
        parent=info.get("commit",{}).get("sha") if isinstance(info,dict) else None
    else:
        parent=ref.get("object",{}).get("sha")
        if load(github)==data:
            return parent
    if not isinstance(parent,str) or len(parent)!=40:
        raise ContextualStrategyEfficiencyStoreError("memory branch parent invalid")
    commit_info=github.get("/git/commits/"+parent)
    base_tree=commit_info.get("tree",{}).get("sha") if isinstance(commit_info,dict) else None
    if not isinstance(base_tree,str) or len(base_tree)!=40:
        raise ContextualStrategyEfficiencyStoreError("memory base tree invalid")
    tree=github.call("POST",github.repo+"/git/trees",{
        "base_tree":base_tree,
        "tree":[{"path":STATE_PATH,"mode":"100644","type":"blob","content":json.dumps(data,sort_keys=True)}],
    })
    tree_sha=tree.get("sha") if isinstance(tree,dict) else None
    if not isinstance(tree_sha,str) or len(tree_sha)!=40:
        raise ContextualStrategyEfficiencyStoreError("contextual strategy tree creation failed")
    commit=github.call("POST",github.repo+"/git/commits",{
        "message":"Persist contextual strategy efficiency",
        "tree":tree_sha,
        "parents":[parent],
    })
    commit_sha=commit.get("sha") if isinstance(commit,dict) else None
    if not isinstance(commit_sha,str) or len(commit_sha)!=40:
        raise ContextualStrategyEfficiencyStoreError("contextual strategy commit creation failed")
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
