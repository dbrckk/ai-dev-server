"""Persistent integrity-sealed backlog for evidence-derived improvements."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path

VERSION=1
STATUSES={"queued","active","proved","rejected"}


class ImprovementBacklogError(ValueError):
    pass


def _canon(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()


def _seal(value):
    out=dict(value)
    out.pop("backlog_sha256",None)
    out["backlog_sha256"]=hashlib.sha256(_canon(out)).hexdigest()
    return out


def new_backlog():
    return _seal({"version":VERSION,"items":[]})


def validate(backlog):
    if not isinstance(backlog,dict) or backlog.get("version")!=VERSION or not isinstance(backlog.get("items"),list):
        raise ImprovementBacklogError("backlog invalid")
    digest=backlog.get("backlog_sha256")
    unsigned=dict(backlog); unsigned.pop("backlog_sha256",None)
    if not isinstance(digest,str) or hashlib.sha256(_canon(unsigned)).hexdigest()!=digest:
        raise ImprovementBacklogError("backlog integrity failure")
    ids=set()
    active=0
    for item in backlog["items"]:
        if not isinstance(item,dict):
            raise ImprovementBacklogError("backlog item invalid")
        required={"candidate","status","proof"}
        if set(item)!=required:
            raise ImprovementBacklogError("backlog item malformed")
        candidate=item["candidate"]
        if not isinstance(candidate,dict) or not isinstance(candidate.get("id"),str):
            raise ImprovementBacklogError("candidate invalid")
        if candidate["id"] in ids:
            raise ImprovementBacklogError("candidate duplicated")
        ids.add(candidate["id"])
        if item["status"] not in STATUSES:
            raise ImprovementBacklogError("item status invalid")
        if not isinstance(item["proof"],dict):
            raise ImprovementBacklogError("proof invalid")
        if item["status"]=="active":
            active+=1
        if item["status"]=="proved" and not item["proof"]:
            raise ImprovementBacklogError("proved item requires proof")
    if active>1:
        raise ImprovementBacklogError("only one improvement may be active")
    return backlog


def merge_assessment(backlog,assessment):
    validate(backlog)
    if not isinstance(assessment,dict) or not isinstance(assessment.get("candidates"),list):
        raise ImprovementBacklogError("assessment invalid")
    existing={item["candidate"]["id"] for item in backlog["items"]}
    items=[{"candidate":dict(item["candidate"]),"status":item["status"],"proof":dict(item["proof"])}
           for item in backlog["items"]]
    for candidate in assessment["candidates"]:
        if not isinstance(candidate,dict) or not isinstance(candidate.get("id"),str):
            raise ImprovementBacklogError("assessment candidate invalid")
        if candidate["id"] not in existing:
            items.append({"candidate":dict(candidate),"status":"queued","proof":{}})
            existing.add(candidate["id"])
    items.sort(key=lambda x:(x["status"]!="active",-int(x["candidate"].get("priority",0)),x["candidate"]["id"]))
    return _seal({"version":VERSION,"items":items})


def activate_next(backlog):
    validate(backlog)
    if any(item["status"]=="active" for item in backlog["items"]):
        return backlog
    items=[]
    activated=False
    for item in backlog["items"]:
        copy={"candidate":dict(item["candidate"]),"status":item["status"],"proof":dict(item["proof"])}
        if not activated and copy["status"]=="queued":
            copy["status"]="active"; activated=True
        items.append(copy)
    return _seal({"version":VERSION,"items":items})


def prove(backlog,candidate_id,proof):
    validate(backlog)
    if not isinstance(proof,dict) or not proof:
        raise ImprovementBacklogError("proof required")
    items=[]; found=False
    for item in backlog["items"]:
        copy={"candidate":dict(item["candidate"]),"status":item["status"],"proof":dict(item["proof"])}
        if copy["candidate"]["id"]==candidate_id:
            found=True
            if copy["status"]!="active":
                raise ImprovementBacklogError("only active improvement can be proved")
            required=copy["candidate"].get("required_evidence")
            if not isinstance(required,list) or any(key not in proof or proof[key] is False or proof[key] is None for key in required):
                raise ImprovementBacklogError("improvement proof incomplete")
            copy["status"]="proved"; copy["proof"]=dict(proof)
        items.append(copy)
    if not found:
        raise ImprovementBacklogError("candidate not found")
    return _seal({"version":VERSION,"items":items})


def save(path,backlog):
    validate(backlog)
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix=path.name+".",dir=path.parent)
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as handle:
            json.dump(backlog,handle,sort_keys=True,ensure_ascii=False,indent=2)
            handle.write("\n"); handle.flush(); os.fsync(handle.fileno())
        os.replace(tmp,path)
    finally:
        try: os.unlink(tmp)
        except FileNotFoundError: pass


def load(path):
    try:
        value=json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError) as exc:
        raise ImprovementBacklogError("backlog unreadable") from exc
    return validate(value)
