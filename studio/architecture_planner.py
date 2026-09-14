"""Trusted architecture decision layer built from advisory star-list recommendations."""
from __future__ import annotations

import json
from pathlib import Path

from architecture_feedback import apply as apply_feedback, stack_adjustment
from atomic_file import write_text as atomic_write_text

MAX_CHOSEN = 6
MAX_REJECTED = 12
HIGH_CONFIDENCE_MARGIN = 1.5
MEDIUM_CONFIDENCE_MARGIN = 0.5

def _selection_confidence(margin: float | None) -> str:
    if margin is None or margin >= HIGH_CONFIDENCE_MARGIN:
        return "high"
    if margin >= MEDIUM_CONFIDENCE_MARGIN:
        return "medium"
    return "low"

def _clean_rows(value):
    if not isinstance(value, dict):
        return []
    rows=[]
    for row in value.get("matches", [])[:24]:
        if isinstance(row, dict) and isinstance(row.get("repo"), str):
            rows.append(row)
    return rows

def _project_type(req: dict) -> str:
    brief = req.get("brief") if isinstance(req.get("brief"), str) else ""
    text = brief.lower()
    rules = (
        ("game", ("game", "jeu", "godot", "multiplayer", "rpg", "platformer")),
        ("trading", ("trading", "xauusd", "gold", "forex", "crypto", "backtest")),
        ("commerce", ("shop", "store", "ecommerce", "e-commerce", "marketplace", "commerce")),
        ("social", ("social", "chat", "community", "messaging", "dating")),
        ("media", ("video", "audio", "music", "photo", "camera", "streaming")),
        ("education", ("education", "learning", "course", "quiz", "school", "study")),
        ("health", ("health", "fitness", "wellness", "medical")),
        ("productivity", ("productivity", "task", "todo", "calendar", "notes", "workflow")),
    )
    for name, terms in rules:
        if any(term in text for term in terms):
            return name
    return "general"

def _primary_domain(rows: list[dict]) -> str | None:
    counts = {}
    for row in rows:
        domain = row.get("domain") if isinstance(row, dict) else None
        if isinstance(domain, str) and domain:
            counts[domain] = counts.get(domain, 0) + 1
    if not counts:
        return None
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0][0]

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

def plan(
    req: dict,
    recommendations: dict,
    learning: dict | None = None,
    *,
    framework: str | None = None,
    publication_target: str | None = None,
) -> dict:
    resolved_framework = (
        framework
        if isinstance(framework, str) and framework
        else req.get("framework")
        if isinstance(req.get("framework"), str) and req.get("framework")
        else "flutter"
    )
    resolved_project_type = _project_type(req)
    resolved_publication = (
        publication_target
        if isinstance(publication_target, str) and publication_target
        else req.get("publication_target")
        if isinstance(req.get("publication_target"), str) and req.get("publication_target")
        else "google-play" if resolved_framework in {"flutter", "godot"} else "unspecified"
    )
    raw_rows = _clean_rows(recommendations)
    resolved_primary_domain = _primary_domain(raw_rows)
    recommendations = apply_feedback(
        recommendations,
        learning,
        framework=resolved_framework,
        project_type=resolved_project_type,
        primary_domain=resolved_primary_domain,
    )
    rows=_clean_rows(recommendations)
    chosen=[]
    rejected=[]
    pending=[]
    for row in rows:
        repo=row["repo"]
        avoid=row.get("avoid_when") if isinstance(row.get("avoid_when"),list) else []
        if avoid:
            rejected.append({
                "repo":repo,
                "reason":"has avoidWhen constraints; requires explicit fit review: " + "; ".join(str(x) for x in avoid[:3])
            })
            continue
        pending.append(dict(row))

    # Greedy selection: base recommendation/history score first, then a tightly bounded
    # bonus for combinations that repeatedly succeeded together in prior projects.
    while pending and len(chosen)<MAX_CHOSEN:
        chosen_names=[x["repo"] for x in chosen]
        scored=[]
        for row in pending:
            synergy=stack_adjustment(
                row["repo"],
                chosen_names,
                learning,
                framework=resolved_framework,
                project_type=resolved_project_type,
                primary_domain=resolved_primary_domain,
            )
            base=row.get("feedback_score", row.get("score"))
            base_score=float(base) if isinstance(base,(int,float)) else 0.0
            effective=round(base_score + float(synergy.get("bonus",0.0)),4)
            scored.append((effective,row,synergy))
        scored.sort(key=lambda item: (
            item[0],
            float(item[1].get("quality_score",0.0) or 0.0),
            item[1]["repo"],
        ), reverse=True)
        effective,row,synergy=scored[0]
        runner_up_score = scored[1][0] if len(scored) > 1 else None
        selection_margin = (
            round(effective - runner_up_score, 4)
            if runner_up_score is not None
            else None
        )
        pending=[x for x in pending if x["repo"]!=row["repo"]]
        chosen.append({
            "repo":row["repo"],
            "selection_score":effective,
            "selection_margin":selection_margin,
            "selection_confidence":_selection_confidence(selection_margin),
            "base_selection_score":row.get("score"),
            "repo_feedback_score":row.get("feedback_score", row.get("score")),
            "stack_synergy_bonus":synergy.get("bonus",0.0),
            "stack_historical_evidence":synergy.get("evidence",[]),
            "historical_evidence":row.get("historical_evidence"),
            "quality_score":row.get("quality_score"),
            "tier":row.get("tier"),
            "domain":row.get("domain"),
            "reason":_reason(row),
            "capabilities":list(row.get("capabilities", []))[:12],
            "complements":list(row.get("complements", []))[:8],
            "alternatives":list(row.get("alternatives", []))[:8],
        })

    for row in pending[:max(0,MAX_REJECTED-len(rejected))]:
        rejected.append({"repo":row["repo"],"reason":"lower-ranked than selected candidates for this phase"})

    return {
        "version":2,
        "status":"planned",
        "advisory_only":True,
        "feedback_applied": bool(recommendations.get("feedback_applied")),
        "feedback_policy": recommendations.get("feedback_policy"),
        "stack_feedback_policy":{
            "advisory_only":True,
            "can_add_dependency":False,
            "greedy_synergy_rerank":True,
            "selection_margin_confidence":True,
            "high_confidence_margin":HIGH_CONFIDENCE_MARGIN,
            "medium_confidence_margin":MEDIUM_CONFIDENCE_MARGIN,
        },
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
            "publication_target":resolved_publication,
            "framework":resolved_framework,
            "project_type":resolved_project_type,
            "primary_domain":resolved_primary_domain,
        },
    }

def write(
    req: dict,
    recommendations: dict,
    out: Path,
    learning: dict | None = None,
    *,
    framework: str | None = None,
    publication_target: str | None = None,
) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    decision=plan(
        req,
        recommendations,
        learning=learning,
        framework=framework,
        publication_target=publication_target,
    )
    atomic_write_text(
        out/"architecture-decision.json",
        json.dumps(decision,ensure_ascii=False,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    return decision
