"""Evidence-backed agent performance by repository zone."""
from __future__ import annotations

import json
from pathlib import Path

VERSION = 1


def zone_for(path: str) -> str:
    parts=[p for p in str(path).split("/") if p]
    if len(parts)<=1:
        return "<root>"
    return "/".join(parts[:-1][:3])


def load(path: Path) -> dict:
    path=Path(path)
    if not path.is_file():
        return {"version":VERSION,"rows":{}}
    try:
        value=json.loads(path.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError):
        return {"version":VERSION,"rows":{}}
    if not isinstance(value,dict) or value.get("version")!=VERSION or not isinstance(value.get("rows"),dict):
        return {"version":VERSION,"rows":{}}
    return value


def save(path: Path,data: dict)->None:
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,sort_keys=True,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


def record(path: Path,agent: str,files: list[str],*,success: bool,duration: float)->dict:
    data=load(path)
    rows=data.setdefault("rows",{})
    zones=sorted({zone_for(rel) for rel in files if rel})
    for zone in zones:
        key=f"{agent}|{zone}"
        row=rows.get(key,{"agent":agent,"zone":zone,"runs":0,"successes":0,"duration_total":0.0})
        row["runs"]=int(row.get("runs",0))+1
        row["successes"]=int(row.get("successes",0))+(1 if success else 0)
        row["duration_total"]=round(float(row.get("duration_total",0.0))+max(0.0,float(duration)),3)
        row["success_rate"]=round(row["successes"]/row["runs"],4)
        row["mean_seconds"]=round(row["duration_total"]/row["runs"],3)
        rows[key]=row
    save(path,data)
    return data


def bonus(data: dict,agent: str,zones: list[str])->float:
    if not isinstance(data,dict):
        return 0.0
    values=[]
    rows=data.get("rows",{})
    if not isinstance(rows,dict):
        return 0.0
    for zone in sorted(set(zones)):
        row=rows.get(f"{agent}|{zone}")
        if not isinstance(row,dict) or int(row.get("runs",0))<2:
            continue
        runs=max(1,int(row["runs"]))
        rate=float(row.get("successes",0))/runs
        values.append((rate-0.5)*40.0)
    if not values:
        return 0.0
    return max(-20.0,min(20.0,sum(values)/len(values)))
