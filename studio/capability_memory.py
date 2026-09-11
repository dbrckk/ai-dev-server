"""Reuse validated cross-project experience as non-authoritative capability hints."""
from __future__ import annotations

try:
    from .project_memory import reusable_for_project, validate
except ImportError:
    from project_memory import reusable_for_project, validate


def capability_hints(memory, target_project_id, capability):
    validate(memory)
    if not isinstance(capability,str) or not capability.strip():
        raise ValueError("capability invalid")
    items=reusable_for_project(memory,target_project_id,tags=["capability",capability])
    hints=[]
    for item in items:
        evidence=item.get("evidence")
        provenance=item.get("provenance")
        if not isinstance(evidence,dict) or not isinstance(provenance,dict):
            continue
        commit=evidence.get("commit_sha")
        if not isinstance(commit,str) or len(commit)!=40:
            continue
        hints.append({
            "entry_id":item["id"],
            "source_project":item["project_id"],
            "summary":item["summary"],
            "validated_commit":commit,
            "confidence":item["confidence"],
            "provenance":dict(provenance),
        })
    hints.sort(key=lambda x:(-x["confidence"],x["entry_id"]))
    return hints


def attach_capability_hints(adaptation_request,memory,target_project_id):
    if not isinstance(adaptation_request,dict):
        raise ValueError("adaptation request invalid")
    result=dict(adaptation_request)
    gaps=result.get("gaps")
    if not isinstance(gaps,list):
        raise ValueError("adaptation gaps invalid")
    attached={}
    for gap in gaps:
        if not isinstance(gap,dict):
            continue
        capability=gap.get("value")
        if not isinstance(capability,str) or not capability:
            continue
        hints=capability_hints(memory,target_project_id,capability)
        if hints:
            attached[capability]=hints
    result["prior_validated_experience"]=attached
    result["memory_policy"]={
        "authority":"hint_only",
        "may_skip_validation":False,
        "may_register_capability":False,
        "must_revalidate_locally":True,
    }
    return result
