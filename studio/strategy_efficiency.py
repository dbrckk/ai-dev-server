"""Verified-success efficiency memory for execution strategies."""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

ALPHA = 0.25
MAX_STRATEGIES = 8
MIN_SAMPLES = 4
VALID_STRATEGIES = {
    "model_only",
    "agent_only",
    "model_to_agent",
    "agent_to_model",
    "dual",
}


def load(path: Path) -> dict:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(value, dict):
        return {}
    clean = {}
    for name, row in list(value.items())[:MAX_STRATEGIES]:
        if name not in VALID_STRATEGIES or not isinstance(row, dict):
            continue
        try:
            samples = max(0, int(row.get("samples", 0)))
            successes = max(0, int(row.get("successes", 0)))
            ema_cost = max(0.0, float(row.get("ema_cost_seconds", 0.0)))
        except (TypeError, ValueError):
            continue
        clean[name] = {
            "samples": samples,
            "successes": min(successes, samples),
            "ema_cost_seconds": ema_cost,
        }
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


def record(path: Path, strategy: str, *, success: bool, cost_seconds: float) -> dict:
    if strategy not in VALID_STRATEGIES:
        raise ValueError("strategy invalid")
    data = load(path)
    row = data.get(strategy, {"samples": 0, "successes": 0, "ema_cost_seconds": 0.0})
    samples = int(row["samples"])
    cost = max(0.0, float(cost_seconds))
    previous = float(row["ema_cost_seconds"])
    ema = cost if samples == 0 else (ALPHA * cost + (1.0 - ALPHA) * previous)
    data[strategy] = {
        "samples": samples + 1,
        "successes": int(row["successes"]) + int(bool(success)),
        "ema_cost_seconds": ema,
    }
    _save(path, data)
    return data


def metrics(data: dict, strategy: str) -> dict | None:
    row = data.get(strategy)
    if not isinstance(row, dict) or int(row.get("samples", 0)) < MIN_SAMPLES:
        return None
    samples = int(row["samples"])
    successes = int(row["successes"])
    success_rate = successes / samples if samples else 0.0
    cost = max(1.0, float(row.get("ema_cost_seconds", 0.0)))
    # Scale to successes per 100 seconds for readable values.
    efficiency = success_rate * 100.0 / cost
    return {
        "samples": samples,
        "success_rate": success_rate,
        "ema_cost_seconds": cost,
        "efficiency": efficiency,
    }


def best_strategy(data: dict, *, allowed: set[str] | None = None) -> tuple[str, dict] | None:
    candidates = []
    for strategy in VALID_STRATEGIES:
        if allowed is not None and strategy not in allowed:
            continue
        info = metrics(data, strategy)
        if info is not None:
            candidates.append((strategy, info))
    if not candidates:
        return None
    candidates.sort(key=lambda item: (-item[1]["efficiency"], -item[1]["success_rate"], item[1]["ema_cost_seconds"], item[0]))
    return candidates[0]
