"""Context-scoped verified strategy efficiency memory."""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from strategy_efficiency import VALID_STRATEGIES, load as load_global_row, record as record_global_row

MAX_CONTEXTS = 16


def load(path: Path) -> dict:
    try:
        value=json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError):
        return {}
    if not isinstance(value,dict):
        return {}
    clean={}
    for context,rows in list(value.items())[:MAX_CONTEXTS]:
        if not isinstance(context,str) or not context or not isinstance(rows,dict):
            continue
        valid={}
        for strategy,row in rows.items():
            if strategy not in VALID_STRATEGIES or not isinstance(row,dict):
                continue
            try:
                samples=max(0,int(row.get("samples",0)))
                successes=min(samples,max(0,int(row.get("successes",0))))
                cost=max(0.0,float(row.get("ema_cost_seconds",0.0)))
                fallback=(successes/samples) if samples else 0.0
                recent=max(0.0,min(1.0,float(row.get("ema_success_rate",fallback))))
            except (TypeError,ValueError):
                continue
            valid[strategy]={
                "samples":samples,
                "successes":successes,
                "ema_cost_seconds":cost,
                "ema_success_rate":recent,
            }
        if valid:
            clean[context]=valid
    return clean


def _save(path:Path,data:dict)->None:
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix=path.name+".",dir=path.parent)
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as handle:
            json.dump(data,handle,sort_keys=True,indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp,path)
    finally:
        try: os.unlink(tmp)
        except FileNotFoundError: pass


def record(path:Path,context:str,strategy:str,*,success:bool,cost_seconds:float)->dict:
    if not isinstance(context,str) or not context:
        raise ValueError("context invalid")
    if strategy not in VALID_STRATEGIES:
        raise ValueError("strategy invalid")
    data=load(path)
    rows=data.setdefault(context,{})
    row=rows.get(strategy,{
        "samples":0,
        "successes":0,
        "ema_cost_seconds":0.0,
        "ema_success_rate":0.0,
    })
    samples=int(row["samples"])
    cost=max(0.0,float(cost_seconds))
    previous=float(row["ema_cost_seconds"])
    alpha=0.25
    cost_ema=cost if samples==0 else alpha*cost+(1.0-alpha)*previous
    observed=1.0 if success else 0.0
    previous_success=float(row.get("ema_success_rate",(int(row["successes"])/samples) if samples else observed))
    recent=observed if samples==0 else alpha*observed+(1.0-alpha)*previous_success
    rows[strategy]={
        "samples":samples+1,
        "successes":int(row["successes"])+int(bool(success)),
        "ema_cost_seconds":cost_ema,
        "ema_success_rate":max(0.0,min(1.0,recent)),
    }
    _save(path,data)
    return data


def rows_for(data:dict,context:str)->dict:
    rows=data.get(context,{})
    return rows if isinstance(rows,dict) else {}
