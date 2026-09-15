"""Reliability scoring from durable worker liveness evidence."""
from __future__ import annotations

WEIGHTS = {"completed": 1.0, "crashed": -1.0, "stalled": -0.75, "orphaned": -0.5}


def summarize(liveness: dict) -> dict:
    workers = liveness.get("workers") if isinstance(liveness, dict) else None
    buckets = {}
    for row in workers if isinstance(workers, list) else []:
        if not isinstance(row, dict):
            continue
        project = str(row.get("project_id") or "").strip()
        if not project:
            continue
        classification = str(row.get("classification") or "")
        bucket = buckets.setdefault(project, {
            "completed": 0, "crashed": 0, "stalled": 0, "orphaned": 0, "samples": 0,
        })
        if classification in WEIGHTS:
            bucket[classification] += 1
            bucket["samples"] += 1

    projects = {}
    for project, bucket in buckets.items():
        samples = bucket["samples"]
        positive = bucket["completed"]
        negative_weight = (
            bucket["crashed"] * 1.0
            + bucket["stalled"] * 0.75
            + bucket["orphaned"] * 0.5
        )
        # Beta prior keeps sparse histories near neutral instead of overreacting.
        reliability = (positive + 2.0) / (positive + negative_weight + 4.0)
        confidence = min(1.0, samples / 8.0)
        multiplier = 1.0 + (reliability - 0.5) * confidence
        projects[project] = {
            **bucket,
            "reliability_score": round(max(0.05, min(0.95, reliability)), 6),
            "confidence": round(confidence, 6),
            "capacity_multiplier": round(max(0.75, min(1.25, multiplier)), 6),
        }
    return {"schema": 1, "projects": projects}


def project_multiplier(summary: dict, project_id: str) -> float:
    row = (summary.get("projects") or {}).get(project_id) if isinstance(summary, dict) else None
    if not isinstance(row, dict):
        return 1.0
    return max(0.75, min(1.25, float(row.get("capacity_multiplier", 1.0) or 1.0)))
