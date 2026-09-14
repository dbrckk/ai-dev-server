"""Summaries and leaderboards for local-model contextual specialization."""
from __future__ import annotations

from collections import defaultdict


def leaderboards(data: dict, *, min_samples: int = 3, limit_per_context: int = 8) -> dict:
    grouped: dict[str, list[dict]] = defaultdict(list)
    if not isinstance(data, dict):
        return {"contexts": {}, "context_count": 0}

    for key, row in data.items():
        if not isinstance(key, str) or not isinstance(row, dict):
            continue
        parts = key.split("|", 3)
        if len(parts) != 4:
            continue
        provider, model, role, context = parts
        try:
            samples = int(row.get("samples", 0) or 0)
            rate = float(row.get("ema_verified_success", 0.0) or 0.0)
        except (TypeError, ValueError):
            continue
        if samples < min_samples:
            continue
        confidence = min(1.0, samples / 10.0)
        specialist_score = (rate - 0.5) * 2.0 * confidence
        grouped[context].append({
            "provider": provider,
            "model": model,
            "role": role,
            "samples": samples,
            "ema_verified_success": round(max(0.0, min(1.0, rate)), 4),
            "confidence": round(confidence, 4),
            "specialist_score": round(specialist_score, 4),
        })

    contexts = {}
    for context, rows in grouped.items():
        rows.sort(
            key=lambda item: (
                -item["specialist_score"],
                -item["samples"],
                item["provider"],
                item["model"],
            )
        )
        contexts[context] = rows[:max(1, int(limit_per_context))]

    return {
        "contexts": dict(sorted(contexts.items())),
        "context_count": len(contexts),
    }
