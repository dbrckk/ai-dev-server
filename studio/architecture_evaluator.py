"""Evaluate architecture choices against observed project evidence without auto-changing dependencies."""
from __future__ import annotations

import json
import re
from pathlib import Path

_NEGATIVE_STATUSES={"failed","blocked","repair_needed","release_failed","human_action_required"}
_POSITIVE_STATUSES={"validated_preview","finished","complete"}

def _tokens(values):
    if isinstance(values,str):
        text=values
    elif isinstance(values,list):
        text=" ".join(str(x) for x in values)
    else:
        text=""
    return {t for t in re.sub(r"[^a-z0-9+.#_-]+"," ",text.lower()).split() if len(t)>1}

def _blockers(report):
    out=[]
    for source in (
        report.get("blockers",[]),
        (report.get("completion") or {}).get("blockers",[]) if isinstance(report.get("completion"),dict) else [],
    ):
        if isinstance(source,list):
            out.extend(str(x) for x in source if isinstance(x,(str,int,float)))
    for key in ("code_review","visual_review"):
        value=report.get(key)
        if isinstance(value,dict) and value.get("passed") is False:
            items=value.get("blockers",[])
            if isinstance(items,list):
                out.extend(str(x) for x in items)
    return out[:50]

def evaluate(decision:dict, report:dict)->dict:
    chosen=decision.get("chosen",[]) if isinstance(decision,dict) else []
    blockers=_blockers(report)
    btoks=_tokens(blockers)
    status=str(report.get("status","unknown"))

    findings=[]
    reconsider=[]
    for row in chosen[:12]:
        if not isinstance(row,dict) or not isinstance(row.get("repo"),str):
            continue
        caps=set(str(x).lower() for x in row.get("capabilities",[]) if isinstance(x,str))
        overlap=sorted(btoks & caps)
        if overlap:
            findings.append({
                "repo":row["repo"],
                "signal":"capability_overlap_with_blocker",
                "matched":overlap,
            })
        alts=row.get("alternatives",[])
        if blockers and isinstance(alts,list) and alts:
            reconsider.append({
                "repo":row["repo"],
                "alternatives":[str(x) for x in alts[:8]],
                "reason":"observed blockers exist; alternatives should be benchmarked before any stack change",
            })

    release=(report.get("release_evidence") or {}) if isinstance(report.get("release_evidence"),dict) else {}
    failed_evidence=[]
    for name,value in release.items():
        if isinstance(value,dict) and value.get("passed") is False:
            failed_evidence.append(str(name))

    if not blockers and not failed_evidence and status in _POSITIVE_STATUSES:
        verdict="retain"
        confidence="high"
    elif blockers or failed_evidence or status in _NEGATIVE_STATUSES:
        verdict="review"
        confidence="medium"
    else:
        verdict="insufficient_evidence"
        confidence="low"

    return {
        "version":1,
        "status":"evaluated",
        "verdict":verdict,
        "confidence":confidence,
        "advisory_only":True,
        "observed_status":status,
        "blockers":blockers,
        "failed_release_evidence":failed_evidence,
        "findings":findings,
        "reconsider_candidates":reconsider[:8],
        "policy":{
            "auto_replace_dependencies":False,
            "require_benchmark_before_stack_change":True,
            "preserve_existing_dependency_policy":True,
        },
    }

def write(decision:dict, report:dict, out:Path)->dict:
    out.mkdir(parents=True,exist_ok=True)
    result=evaluate(decision,report)
    (out/"architecture-evaluation.json").write_text(
        json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    return result
