"""Evidence-backed agent performance memory."""
from __future__ import annotations
import json
from pathlib import Path

def load(path:Path)->dict:
    try:
        x=json.loads(path.read_text())
        return x if isinstance(x,dict) else {}
    except (OSError,json.JSONDecodeError):
        return {}

def record(path:Path,agent:str,role:str,*,success:bool,duration:float)->dict:
    data=load(path); key=agent+":"+role
    row=data.get(key,{"runs":0,"successes":0,"duration_total":0.0})
    row["runs"]+=1; row["successes"]+=int(success); row["duration_total"]+=max(0.0,float(duration))
    data[key]=row; path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,sort_keys=True,indent=2)+"\n")
    return data

def bonus(data:dict,agent:str,role:str)->float:
    row=data.get(agent+":"+role)
    if not isinstance(row,dict) or row.get("runs",0)<2: return 0.0
    runs=max(1,int(row["runs"])); rate=float(row.get("successes",0))/runs
    # bounded empirical adjustment: enough to learn, never enough to erase capability fit
    return max(-25.0,min(25.0,(rate-0.5)*50.0))


def eligible(data:dict,agent:str,role:str)->bool:
    row=data.get(agent+":"+role)
    if not isinstance(row,dict): return True
    runs=int(row.get("runs",0)); successes=int(row.get("successes",0))
    if runs<3: return True
    # Cool down agents that have repeatedly produced changes that fail the
    # trusted verifier. Fresh evidence can re-enable them once statistics improve.
    return (successes/runs)>=0.34
