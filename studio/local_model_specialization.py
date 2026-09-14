"""Context-specific verified reputation for local models."""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

ALPHA = 0.25
MIN_CONTEXT_SAMPLES = 3
MAX_CONTEXT_BONUS = 14.0
MAX_CONTEXT_PENALTY = 16.0
MAX_ROWS = 1024


def _key(provider: str, model: str, role: str, context: str) -> str:
    return "|".join((provider, model, role, context))


def load(path: Path) -> dict:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(value, dict):
        return {}
    clean = {}
    for key, row in list(value.items())[:MAX_ROWS]:
        if not isinstance(key, str) or not isinstance(row, dict):
            continue
        try:
            samples = max(0, int(row.get("samples", 0)))
            successes = min(samples, max(0, int(row.get("successes", 0))))
            ema = max(0.0, min(1.0, float(row.get("ema_verified_success", 0.0))))
        except (TypeError, ValueError):
            continue
        clean[key] = {
            "samples": samples,
            "successes": successes,
            "ema_verified_success": ema,
        }
    return clean


def _save(path: Path, data: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, sort_keys=True, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass


def record_verified(
    path: Path,
    *,
    provider: str,
    model: str,
    role: str,
    contexts: list[tuple[str, float]],
    success: bool,
) -> dict:
    data = load(path)
    for context, weight in contexts:
        if not isinstance(context, str) or not context:
            continue
        try:
            relevance = float(weight)
        except (TypeError, ValueError):
            continue
        if relevance <= 0:
            continue
        key = _key(provider, model, role, context)
        row = data.get(key, {
            "samples": 0,
            "successes": 0,
            "ema_verified_success": 0.0,
        })
        samples = int(row["samples"])
        observed = 1.0 if success else 0.0
        previous = float(row.get("ema_verified_success", 0.0))
        alpha = min(0.5, max(0.08, ALPHA * relevance * 2.0))
        ema = observed if samples == 0 else alpha * observed + (1.0 - alpha) * previous
        data[key] = {
            "samples": samples + 1,
            "successes": int(row["successes"]) + int(success),
            "ema_verified_success": ema,
        }
    _save(path, data)
    return data


def specialization_score(
    data: dict,
    *,
    provider: str,
    model: str,
    role: str,
    contexts: list[tuple[str, float]],
) -> dict:
    total_mass = 0.0
    weighted_signal = 0.0
    evidence = []
    for context, relevance in contexts:
        row = data.get(_key(provider, model, role, context)) if isinstance(data, dict) else None
        if not isinstance(row, dict):
            continue
        samples = int(row.get("samples", 0) or 0)
        if samples < MIN_CONTEXT_SAMPLES:
            continue
        try:
            rel = max(0.0, float(relevance))
        except (TypeError, ValueError):
            continue
        confidence = min(1.0, samples / 10.0)
        mass = rel * confidence
        rate = max(0.0, min(1.0, float(row.get("ema_verified_success", 0.0))))
        centered = (rate - 0.5) * 2.0
        weighted_signal += centered * mass
        total_mass += mass
        evidence.append({
            "context": context,
            "samples": samples,
            "ema_verified_success": round(rate, 4),
            "mass": round(mass, 4),
        })

    if total_mass <= 0:
        return {"score": 0.0, "evidence_mass": 0.0, "contexts": []}

    normalized = max(-1.0, min(1.0, weighted_signal / total_mass))
    score = normalized * (MAX_CONTEXT_BONUS if normalized >= 0 else MAX_CONTEXT_PENALTY)
    return {
        "score": round(score, 4),
        "evidence_mass": round(total_mass, 4),
        "contexts": sorted(evidence, key=lambda item: (-item["mass"], item["context"]))[:8],
    }


def snapshot(data: dict) -> list[dict]:
    rows = []
    for key, row in data.items():
        parts = key.split("|", 3)
        if len(parts) != 4 or not isinstance(row, dict):
            continue
        provider, model, role, context = parts
        rows.append({
            "provider": provider,
            "model": model,
            "role": role,
            "context": context,
            **row,
        })
    rows.sort(
        key=lambda item: (
            -int(item.get("samples", 0)),
            -float(item.get("ema_verified_success", 0.0)),
            item["provider"],
            item["model"],
            item["context"],
        )
    )
    return rows
