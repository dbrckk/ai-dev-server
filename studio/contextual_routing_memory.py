"""Context-scoped routing memory for providers and agents."""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

MAX_CONTEXTS = 32
MAX_ACTORS_PER_CONTEXT = 32
ALPHA = 0.25
MIN_SAMPLES = 4
MAX_CONTEXT_BONUS = 12.0
MAX_CONTEXT_PENALTY = 18.0


def load(path: Path) -> dict:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(value, dict):
        return {}
    clean = {}
    for context, actors in list(value.items())[:MAX_CONTEXTS]:
        if not isinstance(context, str) or not context or not isinstance(actors, dict):
            continue
        context_rows = {}
        for key, row in list(actors.items())[:MAX_ACTORS_PER_CONTEXT]:
            if not isinstance(key, str) or not isinstance(row, dict):
                continue
            try:
                samples = max(0, int(row.get("samples", 0)))
                successes = min(samples, max(0, int(row.get("successes", 0))))
                ema = max(0.0, min(1.0, float(row.get("ema_success_rate", (successes / samples) if samples else 0.0))))
            except (TypeError, ValueError):
                continue
            context_rows[key] = {
                "samples": samples,
                "successes": successes,
                "ema_success_rate": ema,
            }
        if context_rows:
            clean[context] = context_rows
    return clean


def _save(path: Path, data: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, sort_keys=True, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass


def record(
    path: Path,
    *,
    context: str,
    kind: str,
    name: str,
    success: bool,
) -> dict:
    if not all(isinstance(value, str) and value for value in (context, kind, name)):
        raise ValueError("context routing identity invalid")
    data = load(path)
    rows = data.setdefault(context, {})
    key = kind + ":" + name
    row = rows.get(key, {"samples": 0, "successes": 0, "ema_success_rate": 0.0})
    samples = int(row["samples"])
    observed = 1.0 if success else 0.0
    previous = float(row.get("ema_success_rate", observed))
    ema = observed if samples == 0 else ALPHA * observed + (1.0 - ALPHA) * previous
    rows[key] = {
        "samples": samples + 1,
        "successes": int(row["successes"]) + int(success),
        "ema_success_rate": max(0.0, min(1.0, ema)),
    }
    _save(path, data)
    return data


def contextual_adjustment(
    data: dict,
    *,
    weighted_contexts: list[tuple[str, float]],
    kind: str,
    name: str,
) -> float:
    if not isinstance(data, dict):
        return 0.0
    total_weight = 0.0
    signal = 0.0
    for context, relevance in weighted_contexts:
        rows = data.get(context)
        if not isinstance(rows, dict):
            continue
        row = rows.get(kind + ":" + name)
        if not isinstance(row, dict):
            continue
        samples = int(row.get("samples", 0) or 0)
        if samples < MIN_SAMPLES:
            continue
        relevance = max(0.0, float(relevance))
        if relevance <= 0:
            continue
        confidence = min(1.0, samples / 12.0)
        rate = max(0.0, min(1.0, float(row.get("ema_success_rate", 0.0))))
        centered = (rate - 0.5) * 2.0
        mass = relevance * confidence
        signal += centered * mass
        total_weight += mass
    if total_weight <= 0:
        return 0.0
    normalized = max(-1.0, min(1.0, signal / total_weight))
    if normalized >= 0:
        return round(normalized * MAX_CONTEXT_BONUS, 4)
    return round(normalized * MAX_CONTEXT_PENALTY, 4)
