"""Provider/model runtime reliability derived from worker liveness evidence."""
from __future__ import annotations


def summarize(liveness: dict) -> dict:
    workers = liveness.get("workers") if isinstance(liveness, dict) else []
    buckets = {}
    for row in workers if isinstance(workers, list) else []:
        if not isinstance(row, dict):
            continue
        provider = str(row.get("provider") or "").strip()
        model = str(row.get("model") or "").strip()
        if not provider or provider == "__admission_slot__":
            continue
        key = provider + "::" + (model or "*")
        bucket = buckets.setdefault(key, {
            "provider": provider, "model": model or "*", "samples": 0,
            "completed": 0, "crashed": 0, "stalled": 0, "orphaned": 0,
        })
        classification = str(row.get("classification") or "")
        if classification in {"completed", "crashed", "stalled", "orphaned"}:
            bucket[classification] += 1
            bucket["samples"] += 1
    rows = {}
    for key, bucket in buckets.items():
        positive = bucket["completed"]
        negative = bucket["crashed"] + 0.75 * bucket["stalled"] + 0.5 * bucket["orphaned"]
        score = (positive + 2.0) / (positive + negative + 4.0)
        confidence = min(1.0, bucket["samples"] / 8.0)
        rows[key] = {
            **bucket,
            "reliability_score": round(max(0.05, min(0.95, score)), 6),
            "confidence": round(confidence, 6),
        }
    return {"schema": 1, "routes": rows}


def routing_bonus(summary: dict, provider: str, model: str) -> float:
    routes = summary.get("routes") if isinstance(summary, dict) else {}
    row = routes.get(str(provider) + "::" + str(model)) if isinstance(routes, dict) else None
    if row is None and isinstance(routes, dict):
        row = routes.get(str(provider) + "::*")
    if not isinstance(row, dict):
        return 0.0
    confidence = max(0.0, min(1.0, float(row.get("confidence", 0.0) or 0.0)))
    score = max(0.05, min(0.95, float(row.get("reliability_score", 0.5) or 0.5)))
    return round(max(-12.0, min(12.0, (score - 0.5) * 24.0 * confidence)), 6)
