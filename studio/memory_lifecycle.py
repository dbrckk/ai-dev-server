"""Ingest trusted run evidence into persistent project memory."""
from __future__ import annotations

import json
from pathlib import Path

try:
    from .memory_bridge import remember_experience, remember_research
except ImportError:
    from memory_bridge import remember_experience, remember_research


def _read(path):
    try:
        value=json.loads(Path(path).read_text())
    except (OSError,json.JSONDecodeError):
        return None
    return value if isinstance(value,dict) else None


def ingest_run(memory, project_id, out):
    out=Path(out)

    # Generic-project learning: only retain experience backed by a real verifier
    # and a persisted Git commit. This global memory is later reusable by other
    # projects through the existing project-memory bridge.
    verifier=_read(out/"generic-verifier.json")
    generic=_read(out/"generic-report.json")
    if isinstance(generic,dict):
        rounds=generic.get("rounds")
        commit=generic.get("checkpoint_commit")
        if isinstance(rounds,list) and rounds and isinstance(commit,str) and len(commit)==40:
            last=rounds[-1] if isinstance(rounds[-1],dict) else {}
            verification=last.get("verification") if isinstance(last,dict) else {}
            if isinstance(verification,dict) and verification.get("passed") is True:
                entry_id="generic:"+project_id+":"+commit[:16]
                existing={item.get("id") for item in memory.get("entries",[]) if isinstance(item,dict)}
                if entry_id not in existing:
                    review=last.get("review") if isinstance(last.get("review"),dict) else {}
                    changed=last.get("changed_files") if isinstance(last.get("changed_files"),list) else []
                    summary="Verified generic-project cycle; changed "+str(len(changed))+" files."
                    reason=review.get("reason")
                    if isinstance(reason,str) and reason.strip():
                        summary=(summary+" "+reason.strip())[:4000]
                    tags=["generic-project","verified-cycle"]
                    if isinstance(verifier,dict) and verifier.get("status")=="validated_recipe":
                        recipe=verifier.get("recipe") if isinstance(verifier.get("recipe"),dict) else {}
                        commands=recipe.get("commands") if isinstance(recipe.get("commands"),list) else []
                        if commands:
                            summary=(summary+" Adaptive verifier recipe: "+json.dumps(commands,ensure_ascii=False))[:4000]
                            tags.append("adaptive-verifier")
                    memory=remember_experience(
                        memory,
                        project_id,
                        entry_id=entry_id,
                        summary=summary,
                        tags=tags,
                        proof={
                            "tests_passed":True,
                            "regression_suite_passed":True,
                            "commit_sha":commit,
                            "engine":"generic",
                            "changed_files":changed[:80],
                        },
                        reusable=True,
                        confidence=90,
                    )
    research=_read(out/"evolution-research.json")
    if research is not None:
        candidate_id=research.get("candidate_id")
        items=research.get("items")
        if not isinstance(candidate_id,str) or not isinstance(items,list):
            raise ValueError("research evidence invalid")
        expected={"research:"+candidate_id+":"+str(i) for i in range(len(items))}
        existing={item.get("id") for item in memory.get("entries",[]) if isinstance(item,dict)}
        overlap=expected & existing
        if overlap and overlap != expected:
            raise ValueError("research memory partially recorded")
        if not overlap:
            memory=remember_research(memory,project_id,research)

    persisted=_read(out/"evolution-persisted.json")
    promotion=_read(out/"evolution-promotion.json")
    benchmark=_read(out/"evolution-isolated-benchmark.json")
    if not persisted or not promotion or not benchmark:
        return memory
    if persisted.get("status") not in {"promotion_persisted","already_persisted"}:
        return memory
    if promotion.get("status")!="promotion_approved" or promotion.get("promotion_decision")!="approve":
        return memory
    candidate=benchmark.get("candidate")
    if not isinstance(candidate,dict):
        return memory
    unit=candidate.get("unit_tests")
    if not isinstance(unit,dict) or unit.get("passed") is not True:
        return memory
    if candidate.get("flutter_smoke_passed") is not True:
        return memory
    commit=persisted.get("commit_sha")
    gap=persisted.get("gap")
    candidate_id=persisted.get("candidate_id")
    if not all(isinstance(x,str) and x for x in (commit,gap,candidate_id)):
        return memory
    proof={
        "tests_passed":True,
        "regression_suite_passed":True,
        "commit_sha":commit,
        "promotion_status":"approved",
        "candidate_id":candidate_id,
        "gap":gap,
    }
    entry_id="experience:"+candidate_id
    existing={item.get("id") for item in memory.get("entries",[]) if isinstance(item,dict)}
    if entry_id in existing:
        return memory
    return remember_experience(
        memory,
        project_id,
        entry_id=entry_id,
        summary="Validated autonomous capability promotion for "+gap+".",
        tags=["capability",gap,"autonomous-promotion"],
        proof=proof,
        reusable=True,
        confidence=95,
    )
