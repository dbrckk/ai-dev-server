"""Trusted architecture decision layer built from advisory star-list recommendations."""
from __future__ import annotations

import json
from pathlib import Path

MAX_CHOSEN = 6
MAX_REJECTED = 12

def _clean_rows(value):
    if not isinstance(value, dict):
        return []
    rows=[]
    for row in value.get("matches", [])[:24]:
        if isinstance(row, dict) and isinstance(row.get("repo"), str):
            rows.append(row)
    return rows

def _reason(row):
    parts=[]
    if row.get("tier"):
        parts.append(str(row["tier"]))
    caps=row.get("capabilities")
    if isinstance(caps,list) and caps:
        parts.append("capabilities: " + ", ".join(str(x) for x in caps[:5]))
    best=row.get("best_for")
    if isinstance(best,list) and best:
        parts.append("best for: " + "; ".join(str(x) for x in best[:2]))
    return " | ".join(parts) or "ranked recommendation"

def plan(req: dict, recommendations: dict) -> dict:
    rows=_clean_rows(recommendations)
    chosen=[]
    rejected=[]
    for row in rows:
        repo=row["repo"]
        avoid=row.get("avoid_when") if isinstance(row.get("avoid_when"),list) else []
        if avoid:
            rejected.append({
                "repo":repo,
                "reason":"has avoidWhen constraints; requires explicit fit review: " + "; ".join(str(x) for x in avoid[:3])
            })
            continue
        if len(chosen)<MAX_CHOSEN:
            chosen.append({
                "repo":repo,
                "selection_score":row.get("score"),
                "quality_score":row.get("quality_score"),
                "tier":row.get("tier"),
                "domain":row.get("domain"),
                "reason":_reason(row),
                "capabilities":list(row.get("capabilities", []))[:12],
                "complements":list(row.get("complements", []))[:8],
                "alternatives":list(row.get("alternatives", []))[:8],
            })
        elif len(rejected)<MAX_REJECTED:
            rejected.append({"repo":repo,"reason":"lower-ranked than selected candidates for this phase"})

    return {
        "version":1,
        "status":"planned",
        "advisory_only":True,
        "brief_fingerprint_source":"request.brief",
        "chosen":chosen,
        "rejected":rejected[:MAX_REJECTED],
        "dependency_policy":{
            "allow_automatic_dependency_addition":False,
            "reason":"star-list recommendations are architectural evidence only; project dependency rules remain authoritative",
            "require_explicit_approval_or_existing_policy":True,
        },
        "fallbacks":[
            {"repo":x["repo"],"alternatives":x.get("alternatives", [])}
            for x in chosen if x.get("alternatives")
        ],
        "constraints":{
            "target_repo":req.get("target_repo"),
            "app_name":req.get("app_name"),
            "publication_target":"google-play",
            "framework":"flutter",
        },
    }

def write(req: dict, recommendations: dict, out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    decision=plan(req,recommendations)
    (out/"architecture-decision.json").write_text(
        json.dumps(decision,ensure_ascii=False,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    return decision
