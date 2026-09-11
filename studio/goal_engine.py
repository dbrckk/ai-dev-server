"""Persistent evidence-gated goal state for autonomous studio runs."""
from __future__ import annotations
import hashlib, json, os, tempfile
from pathlib import Path

VERSION=1
TERMINAL={"complete","human_action_required","blocked"}

class GoalStateError(ValueError): pass

def _canon(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def _seal(v):
    x=dict(v); x.pop("state_sha256",None)
    x["state_sha256"]=hashlib.sha256(_canon(x)).hexdigest()
    return x

def new_goal(goal_id,objective,criteria,max_attempts=20):
    if not isinstance(goal_id,str) or not goal_id.strip(): raise GoalStateError("goal_id invalid")
    if not isinstance(objective,str) or not objective.strip(): raise GoalStateError("objective invalid")
    if not isinstance(criteria,list) or not criteria: raise GoalStateError("criteria required")
    if not isinstance(max_attempts,int) or isinstance(max_attempts,bool) or not 1<=max_attempts<=1000: raise GoalStateError("max_attempts invalid")
    names=set(); normalized=[]
    for c in criteria:
        if not isinstance(c,dict) or set(c)!={"name","required_evidence"}: raise GoalStateError("criterion malformed")
        n=c["name"]; ev=c["required_evidence"]
        if not isinstance(n,str) or not n.strip() or n in names: raise GoalStateError("criterion name invalid")
        if not isinstance(ev,list) or not ev or any(not isinstance(k,str) or not k.strip() for k in ev): raise GoalStateError("criterion evidence invalid")
        if len(set(ev))!=len(ev): raise GoalStateError("criterion evidence duplicated")
        names.add(n); normalized.append({"name":n,"required_evidence":ev})
    return _seal({"version":VERSION,"goal_id":goal_id,"objective":objective,"criteria":normalized,"attempt":0,"max_attempts":max_attempts,"evidence":{},"failures":[],"missing_capabilities":[],"human_action":None,"blocked_reason":None,"history":[],"status":"active"})

def validate(state):
    if not isinstance(state,dict): raise GoalStateError("state invalid")
    digest=state.get("state_sha256")
    if not isinstance(digest,str) or len(digest)!=64: raise GoalStateError("digest invalid")
    unsigned=dict(state); unsigned.pop("state_sha256")
    if hashlib.sha256(_canon(unsigned)).hexdigest()!=digest: raise GoalStateError("state integrity failure")
    if state.get("status") not in {"active",*TERMINAL}: raise GoalStateError("status invalid")
    if not isinstance(state.get("attempt"),int) or not isinstance(state.get("max_attempts"),int) or not 0<=state["attempt"]<=state["max_attempts"]: raise GoalStateError("attempt invalid")
    return state

def save(path,state):
    validate(state); path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix=path.name+".",dir=path.parent)
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as f:
            json.dump(state,f,sort_keys=True,ensure_ascii=False,indent=2); f.write("\n"); f.flush(); os.fsync(f.fileno())
        os.replace(tmp,path)
    finally:
        try: os.unlink(tmp)
        except FileNotFoundError: pass

def load(path):
    try: value=json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError) as e: raise GoalStateError("state unreadable") from e
    return validate(value)

def missing_evidence(state):
    validate(state); found=state["evidence"]; out=[]
    for c in state["criteria"]:
        for key in c["required_evidence"]:
            if key not in found and key not in out: out.append(key)
    return out

def record_cycle(state,evidence=None,failure=None,missing_capability=None,human_action=None,blocked_reason=None):
    validate(state)
    if state["status"]!="active": raise GoalStateError("terminal state immutable")
    if state["attempt"]>=state["max_attempts"]: raise GoalStateError("attempt budget exhausted")
    x={**state,"evidence":dict(state["evidence"]),"failures":list(state["failures"]),"missing_capabilities":list(state["missing_capabilities"]),"history":list(state["history"])}
    x["attempt"]+=1
    if evidence:
        if not isinstance(evidence,dict) or any(not isinstance(k,str) or not k or v is None or v is False for k,v in evidence.items()): raise GoalStateError("evidence invalid")
        x["evidence"].update(evidence)
    event={"attempt":x["attempt"],"evidence_keys":sorted((evidence or {}).keys())}
    if failure: x["failures"].append(str(failure)); event["failure"]=str(failure)
    if missing_capability:
        m=str(missing_capability)
        if m not in x["missing_capabilities"]: x["missing_capabilities"].append(m)
        event["missing_capability"]=m
    if human_action: x["human_action"]=str(human_action); event["human_action"]=x["human_action"]
    if blocked_reason: x["blocked_reason"]=str(blocked_reason); event["blocked_reason"]=x["blocked_reason"]
    x["history"].append(event)
    return _seal(x)

def resolve_capability(state,name,evidence=None):
    validate(state)
    if state["status"]!="active": raise GoalStateError("terminal state immutable")
    if not isinstance(name,str) or not name.strip(): raise GoalStateError("capability name invalid")
    if name not in state["missing_capabilities"]: raise GoalStateError("capability not pending")
    x={**state,"evidence":dict(state["evidence"]),"missing_capabilities":list(state["missing_capabilities"]),"history":list(state["history"])}
    x["missing_capabilities"].remove(name)
    if evidence is not None:
        if not isinstance(evidence,dict) or not evidence: raise GoalStateError("capability evidence invalid")
        x["evidence"]["capability:"+name]=evidence
    x["history"].append({"attempt":x["attempt"],"resolved_capability":name})
    return _seal(x)

def decide(state):
    validate(state); missing=missing_evidence(state)
    if state["status"]!="active": return {"decision":state["status"],"missing_evidence":missing,"next_action":None}
    if state["human_action"]: return {"decision":"human_action_required","missing_evidence":missing,"next_action":state["human_action"]}
    if state["blocked_reason"]: return {"decision":"blocked","missing_evidence":missing,"next_action":state["blocked_reason"]}
    if state["attempt"]>=state["max_attempts"] and missing: return {"decision":"blocked","missing_evidence":missing,"next_action":"attempt_budget_exhausted"}
    if state["missing_capabilities"]: return {"decision":"replan","missing_evidence":missing,"next_action":"adapt:"+state["missing_capabilities"][0]}
    if not missing: return {"decision":"complete","missing_evidence":[],"next_action":None}
    return {"decision":"relaunch","missing_evidence":missing,"next_action":"continue_goal"}

def finalize(state):
    d=decide(state)
    if d["decision"] not in TERMINAL: raise GoalStateError("work remains")
    x=dict(state); x["status"]=d["decision"]; return _seal(x)
