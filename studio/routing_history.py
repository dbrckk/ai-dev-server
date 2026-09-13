"""Bounded routing-decision history and conservative weight learning."""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

MAX_EVENTS = 500
MIN_EVENTS_FOR_LEARNING = 8
MIN_WEIGHT = 0.75
MAX_WEIGHT = 1.25
DEFAULT_WEIGHTS = {
    "priority": 1.0,
    "free": 1.0,
    "reliability": 1.0,
    "latency": 1.0,
    "capability_fit": 1.0,
    "long_task": 1.0,
}


def load(path: Path) -> list[dict]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(value, list):
        return []
    clean = []
    for event in value[-MAX_EVENTS:]:
        if not isinstance(event, dict):
            continue
        if event.get("kind") not in {"provider", "agent", "model_candidate"}:
            continue
        if not isinstance(event.get("name"), str) or not isinstance(event.get("role"), str):
            continue
        if type(event.get("success")) is not bool:
            continue
        score = event.get("score")
        if not isinstance(score, dict) or not isinstance(score.get("components"), dict):
            continue
        clean.append(event)
    return clean


def _save(path: Path, events: list[dict]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(events[-MAX_EVENTS:], handle, sort_keys=True, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass


def record(path: Path, *, kind: str, name: str, role: str, score: dict, success: bool, duration_seconds: float) -> list[dict]:
    if kind not in {"provider", "agent", "model_candidate"}:
        raise ValueError("routing kind invalid")
    if not isinstance(name, str) or not name or not isinstance(role, str) or not role:
        raise ValueError("routing identity invalid")
    components = score.get("components") if isinstance(score, dict) else None
    if not isinstance(components, dict):
        raise ValueError("routing score invalid")
    safe_components = {}
    for key, value in components.items():
        if isinstance(key, str) and isinstance(value, (int, float)) and not isinstance(value, bool):
            safe_components[key] = float(value)
    event = {
        "kind": kind,
        "name": name,
        "role": role,
        "score": {
            "total": float(score.get("total", sum(safe_components.values()))),
            "components": safe_components,
        },
        "success": bool(success),
        "duration_seconds": max(0.0, float(duration_seconds)),
    }
    events = load(path)
    events.append(event)
    _save(path, events)
    return events


def learned_weights(events: list[dict], *, kind: str, role: str) -> dict[str, float]:
    relevant = [e for e in events if e.get("kind") == kind and e.get("role") == role]
    weights = dict(DEFAULT_WEIGHTS)
    if len(relevant) < MIN_EVENTS_FOR_LEARNING:
        return weights
    component_names = set()
    for event in relevant:
        component_names.update(event["score"]["components"])
    for component in component_names:
        success_values = [
            float(e["score"]["components"].get(component, 0.0))
            for e in relevant if e["success"]
        ]
        failure_values = [
            float(e["score"]["components"].get(component, 0.0))
            for e in relevant if not e["success"]
        ]
        if not success_values or not failure_values:
            continue
        success_mean = sum(success_values) / len(success_values)
        failure_mean = sum(failure_values) / len(failure_values)
        scale = max(1.0, max(abs(success_mean), abs(failure_mean)))
        signal = max(-1.0, min(1.0, (success_mean - failure_mean) / scale))
        weights[component] = max(MIN_WEIGHT, min(MAX_WEIGHT, 1.0 + 0.25 * signal))
    return weights


def weighted_total(components: dict[str, float], weights: dict[str, float]) -> float:
    return sum(float(value) * float(weights.get(name, 1.0)) for name, value in components.items())
