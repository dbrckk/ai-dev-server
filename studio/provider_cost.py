"""Persistent provider monetary-cost memory."""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

ALPHA = 0.25
MAX_ROWS = 128


def _key(provider: str, role: str) -> str:
    return provider + ":" + role


def load(path: Path) -> dict:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(value, dict):
        return {}
    clean = {}
    for key, row in list(value.items())[:MAX_ROWS]:
        if not isinstance(key, str) or ":" not in key or not isinstance(row, dict):
            continue
        try:
            calls = max(0, int(row.get("calls", 0)))
            ema = max(0.0, float(row.get("ema_cost_usd", 0.0)))
            total = max(0.0, float(row.get("total_cost_usd", 0.0)))
        except (TypeError, ValueError):
            continue
        clean[key] = {"calls": calls, "ema_cost_usd": ema, "total_cost_usd": total}
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


def estimate_call_cost(
    *,
    prompt_tokens: int,
    completion_tokens: int,
    input_cost_per_million: float,
    output_cost_per_million: float,
) -> float:
    prompt = max(0, int(prompt_tokens))
    completion = max(0, int(completion_tokens))
    input_rate = max(0.0, float(input_cost_per_million))
    output_rate = max(0.0, float(output_cost_per_million))
    return (prompt / 1_000_000.0) * input_rate + (completion / 1_000_000.0) * output_rate


def record(path: Path, provider: str, role: str, cost_usd: float) -> dict:
    cost = max(0.0, float(cost_usd))
    data = load(path)
    key = _key(provider, role)
    row = data.get(key, {"calls": 0, "ema_cost_usd": 0.0, "total_cost_usd": 0.0})
    calls = int(row["calls"])
    previous = float(row["ema_cost_usd"])
    ema = cost if calls == 0 else ALPHA * cost + (1.0 - ALPHA) * previous
    data[key] = {
        "calls": calls + 1,
        "ema_cost_usd": ema,
        "total_cost_usd": float(row["total_cost_usd"]) + cost,
    }
    _save(path, data)
    return data


def ema_cost(data: dict, provider: str, role: str) -> float:
    row = data.get(_key(provider, role))
    if not isinstance(row, dict):
        return 0.0
    return max(0.0, float(row.get("ema_cost_usd", 0.0)))
