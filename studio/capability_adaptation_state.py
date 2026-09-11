"""Integrity-sealed persistent state for generic capability adaptation."""
from __future__ import annotations

import hashlib
import json
import re

VERSION=1
STATUSES={"research_required","research_complete","synthesis_required","validation_required","promotion_required","awaiting_merge","complete","blocked"}
CAP_RE=re.compile(r"[a-z][a-z0-9_.-]{2,120}")


class CapabilityAdaptationStateError(ValueError):
    pass


def _canon(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()


def _seal(value):
    out=dict(value)
    out.pop("state_sha256",None)
    out["state_sha256"]=hashlib.sha256(_canon(out)).hexdigest()
    return out


def new_state(project_id,capability,source_candidate_id):
    if not isinstance(project_id,str) or not project_id.strip():
        raise CapabilityAdaptationStateError("project id invalid")
    if not isinstance(capability,str) or not CAP_RE.fullmatch(capability):
        raise CapabilityAdaptationStateError("capability invalid")
    if not isinstance(source_candidate_id,str) or not source_candidate_id.strip():
        raise CapabilityAdaptationStateError("source candidate invalid")
    return _seal({
        "version":VERSION,
        "project_id":project_id,
        "capability":capability,
        "source_candidate_id":source_candidate_id,
        "adaptation_candidate_id":"capability:"+capability,
        "status":"research_required",
        "research_status":"not_started",
        "synthesis_status":"not_started",
        "validation_status":"not_started",
        "promotion_status":"not_ready",
    })


def validate(value):
    required={
        "version","project_id","capability","source_candidate_id","adaptation_candidate_id",
        "status","research_status","synthesis_status","validation_status","promotion_status","state_sha256",
    }
    if not isinstance(value,dict) or set(value)!=required or value.get("version")!=VERSION:
        raise CapabilityAdaptationStateError("adaptation state invalid")
    digest=value.get("state_sha256")
    unsigned=dict(value); unsigned.pop("state_sha256",None)
    if not isinstance(digest,str) or hashlib.sha256(_canon(unsigned)).hexdigest()!=digest:
        raise CapabilityAdaptationStateError("adaptation state integrity failure")
    if not isinstance(value["project_id"],str) or not value["project_id"].strip():
        raise CapabilityAdaptationStateError("project id invalid")
    if not isinstance(value["capability"],str) or not CAP_RE.fullmatch(value["capability"]):
        raise CapabilityAdaptationStateError("capability invalid")
    if value["adaptation_candidate_id"]!="capability:"+value["capability"]:
        raise CapabilityAdaptationStateError("adaptation candidate mismatch")
    if not isinstance(value["source_candidate_id"],str) or not value["source_candidate_id"].strip():
        raise CapabilityAdaptationStateError("source candidate invalid")
    if value["status"] not in STATUSES:
        raise CapabilityAdaptationStateError("adaptation status invalid")
    for key in ("research_status","synthesis_status","validation_status","promotion_status"):
        if not isinstance(value[key],str) or not value[key]:
            raise CapabilityAdaptationStateError(key+" invalid")
    return value


def record_research(value, research_status):
    validate(value)
    if value["status"]!="research_required":
        raise CapabilityAdaptationStateError("research transition invalid")
    if research_status=="research_complete":
        status="synthesis_required"
        synthesis_status="required"
    elif research_status in {"research_incomplete","insufficient_sources","insufficient_valid_sources"}:
        status="research_required"
        synthesis_status="not_started"
    else:
        raise CapabilityAdaptationStateError("research status invalid")
    out=dict(value)
    out.update({
        "status":status,
        "research_status":research_status,
        "synthesis_status":synthesis_status,
    })
    return _seal(out)


def record_synthesis(value, candidate_sha256):
    validate(value)
    if value["status"]!="synthesis_required" or value["research_status"]!="research_complete":
        raise CapabilityAdaptationStateError("synthesis transition invalid")
    if not isinstance(candidate_sha256,str) or not re.fullmatch(r"[0-9a-f]{64}",candidate_sha256):
        raise CapabilityAdaptationStateError("candidate digest invalid")
    out=dict(value)
    out.update({
        "status":"validation_required",
        "synthesis_status":"candidate_synthesized:"+candidate_sha256,
        "validation_status":"required",
    })
    return _seal(out)


def record_validation(value, validation_status):
    validate(value)
    if value["status"]!="validation_required" or value["validation_status"]!="required":
        raise CapabilityAdaptationStateError("validation transition invalid")
    if validation_status=="candidate_validated":
        status="promotion_required"
        promotion_status="eligible"
    elif validation_status=="candidate_rejected":
        status="blocked"
        promotion_status="not_ready"
    else:
        raise CapabilityAdaptationStateError("validation result invalid")
    out=dict(value)
    out.update({
        "status":status,
        "validation_status":validation_status,
        "promotion_status":promotion_status,
    })
    return _seal(out)
