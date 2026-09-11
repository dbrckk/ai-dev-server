"""Trusted ingestion helpers for project/research/experience memory."""
from __future__ import annotations

import hashlib
import json

try:
    from .project_memory import add_entry
except ImportError:
    from project_memory import add_entry


def _digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def remember_research(memory, project_id, research):
    if not isinstance(research, dict) or research.get("status") != "research_complete":
        raise ValueError("research not validated")
    candidate_id = research.get("candidate_id")
    items = research.get("items")
    if not isinstance(candidate_id, str) or not candidate_id or not isinstance(items, list) or not items:
        raise ValueError("research evidence invalid")
    out = memory
    for index, item in enumerate(items):
        if not isinstance(item, dict) or not isinstance(item.get("content_sha256"), str):
            raise ValueError("research item invalid")
        kind = item.get("kind")
        source = item.get("source")
        summary = item.get("notes")
        if not all(isinstance(x, str) and x for x in (kind, source, summary)):
            raise ValueError("research item metadata invalid")
        entry_id = "research:" + candidate_id + ":" + str(index)
        out = add_entry(
            out,
            entry_id=entry_id,
            kind="research",
            project_id=project_id,
            summary=summary[:4000],
            tags=["research", kind],
            evidence={
                "candidate_id": candidate_id,
                "content_sha256": item["content_sha256"],
                "item_sha256": _digest(item),
            },
            provenance={"source": source, "kind": kind},
            reusable=False,
            confidence=100,
        )
    return out


def remember_experience(memory, project_id, *, entry_id, summary, tags, proof, reusable=False, confidence=100):
    if not isinstance(proof, dict) or proof.get("tests_passed") is not True:
        raise ValueError("experience proof missing tests")
    commit = proof.get("commit_sha")
    if not isinstance(commit, str) or len(commit) != 40 or any(ch not in "0123456789abcdef" for ch in commit):
        raise ValueError("experience proof commit invalid")
    if reusable and proof.get("regression_suite_passed") is not True:
        raise ValueError("reusable experience requires regression proof")
    return add_entry(
        memory,
        entry_id=entry_id,
        kind="experience",
        project_id=project_id,
        summary=summary,
        tags=tags,
        evidence=proof,
        provenance={"source": "validated_project_execution", "commit_sha": commit},
        reusable=reusable,
        confidence=confidence,
    )
