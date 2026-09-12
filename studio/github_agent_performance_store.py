"""Persist learned agent routing statistics on the trusted memory branch."""
from __future__ import annotations
import base64,json
from pathlib import Path

STATE_BRANCH="studio-project-memory"
STATE_PATH=".studio-memory/agent-performance.json"
MAX_BYTES=256*1024

class AgentPerformanceStoreError(RuntimeError): pass

def _validate(data):
    if not isinstance(data,dict): raise AgentPerformanceStoreError("agent performance invalid")
    for key,row in data.items():
        if not isinstance(key,str) or ":" not in key or not isinstance(row,dict):
            raise AgentPerformanceStoreError("agent performance entry invalid")
        if set(row)!={"runs","successes","duration_total"}:
            raise AgentPerformanceStoreError("agent performance fields invalid")
        runs=row["runs"]; successes=row["successes"]; duration=row["duration_total"]
        if type(runs) is not int or type(successes) is not int or not 0<=successes<=runs or runs<0:
            raise AgentPerformanceStoreError("agent performance counts invalid")
        if not isinstance(duration,(int,float)) or isinstance(duration,bool) or duration<0:
            raise AgentPerformanceStoreError("agent performance duration invalid")
    return data

def _ref(github):
    refs=github.get("/git/matching-refs/heads/"+STATE_BRANCH)
    exact=[x for x in refs if isinstance(x,dict) and x.get("ref")=="refs/heads/"+STATE_BRANCH]
    if len(exact)>1: raise AgentPerformanceStoreError("memory branch ambiguous")
    return exact[0] if exact else None

def load(github):
    ref=_ref(github)
    if ref is None: return {}
    head=ref.get("object",{}).get("sha")
    tree=github.get("/git/trees/"+head+"?recursive=1")
    if not isinstance(tree,dict) or tree.get("truncated") or not isinstance(tree.get("tree"),list):
        raise AgentPerformanceStoreError("memory tree invalid")
    item=next((x for x in tree["tree"] if isinstance(x,dict) and x.get("path")==STATE_PATH and x.get("type")=="blob"),None)
    if item is None: return {}
    blob=github.get("/git/blobs/"+item["sha"])
    try:
        raw=base64.b64decode(blob["content"],validate=False)
        if len(raw)>MAX_BYTES: raise AgentPerformanceStoreError("agent performance too large")
        return _validate(json.loads(raw.decode("utf-8")))
    except (KeyError,ValueError,UnicodeDecodeError,json.JSONDecodeError):
        raise AgentPerformanceStoreError("agent performance unreadable") from None

def save(github,data):
    data=_validate(data)
    ref=_ref(github)
    if ref is None:
        meta=github.get(""); default=meta.get("default_branch")
        parent=github.get("/branches/"+default).get("commit",{}).get("sha")
    else:
        parent=ref.get("object",{}).get("sha")
        if load(github)==data: return parent
    if not isinstance(parent,str) or len(parent)!=40:
        raise AgentPerformanceStoreError("memory branch parent invalid")
    base_tree=github.get("/git/commits/"+parent).get("tree",{}).get("sha")
    tree=github.call("POST",github.repo+"/git/trees",{"base_tree":base_tree,"tree":[{
        "path":STATE_PATH,"mode":"100644","type":"blob","content":json.dumps(data,sort_keys=True)
    }]})
    commit=github.call("POST",github.repo+"/git/commits",{"message":"Persist agent performance memory","tree":tree["sha"],"parents":[parent]})
    sha=commit.get("sha")
    if ref is None:
        github.call("POST",github.repo+"/git/refs",{"ref":"refs/heads/"+STATE_BRANCH,"sha":sha})
    else:
        github.call("PATCH",github.repo+"/git/refs/heads/"+STATE_BRANCH,{"sha":sha,"force":False})
    return sha

def restore_local(github,path:Path):
    data=load(github); path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,sort_keys=True,indent=2)+"\n")
    return data

def persist_local(github,path:Path):
    try: data=json.loads(path.read_text())
    except (OSError,json.JSONDecodeError): data={}
    return save(github,_validate(data))
