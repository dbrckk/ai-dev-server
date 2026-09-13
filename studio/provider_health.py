"""Persistent provider health and circuit-breaker state.

Only aggregate counters and cooldown timestamps are stored. Credentials,
prompts, provider response bodies, and exception messages are never persisted.
"""
from __future__ import annotations

import json
import os
import tempfile
import time
from pathlib import Path

DEFAULT_THRESHOLD = 3
DEFAULT_COOLDOWN_SECONDS = 300
MAX_COOLDOWN_SECONDS = 3600
MAX_ROWS = 64


def _row(value):
    if not isinstance(value, dict):
        return {"successes": 0, "failures": 0, "consecutive_failures": 0, "opened_until": 0.0}
    try:
        successes = max(0, int(value.get("successes", 0)))
        failures = max(0, int(value.get("failures", 0)))
        consecutive = max(0, int(value.get("consecutive_failures", 0)))
        opened_until = max(0.0, float(value.get("opened_until", 0.0)))
    except (TypeError, ValueError):
        return {"successes": 0, "failures": 0, "consecutive_failures": 0, "opened_until": 0.0}
    return {
        "successes": successes,
        "failures": failures,
        "consecutive_failures": consecutive,
        "opened_until": opened_until,
    }


def load(path: Path) -> dict:
    path = Path(path)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(value, dict):
        return {}
    clean = {}
    for name, value_row in list(value.items())[:MAX_ROWS]:
        if isinstance(name, str) and name.strip():
            clean[name] = _row(value_row)
    return clean


def _save(path: Path, data: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, sort_keys=True, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass


def eligible(path: Path, provider: str, *, now: float | None = None) -> bool:
    row = load(path).get(provider)
    if row is None:
        return True
    current = time.time() if now is None else float(now)
    return float(row.get("opened_until", 0.0)) <= current


def record_success(path: Path, provider: str) -> dict:
    data = load(path)
    row = _row(data.get(provider))
    row["successes"] += 1
    row["consecutive_failures"] = 0
    row["opened_until"] = 0.0
    data[provider] = row
    _save(path, data)
    return data


def record_failure(
    path: Path,
    provider: str,
    *,
    threshold: int = DEFAULT_THRESHOLD,
    cooldown_seconds: int = DEFAULT_COOLDOWN_SECONDS,
    now: float | None = None,
) -> dict:
    if type(threshold) is not int or threshold < 1:
        raise ValueError("provider failure threshold invalid")
    if type(cooldown_seconds) is not int or cooldown_seconds < 1:
        raise ValueError("provider cooldown invalid")
    data = load(path)
    row = _row(data.get(provider))
    row["failures"] += 1
    row["consecutive_failures"] += 1
    if row["consecutive_failures"] >= threshold:
        current = time.time() if now is None else float(now)
        exponent = row["consecutive_failures"] - threshold
        cooldown = min(MAX_COOLDOWN_SECONDS, cooldown_seconds * (2 ** exponent))
        row["opened_until"] = current + cooldown
    data[provider] = row
    _save(path, data)
    return data


def reliability_bonus(data: dict, provider: str) -> float:
    """Return a bounded empirical routing bonus from observed success history."""
    row = data.get(provider)
    if not isinstance(row, dict):
        return 0.0
    successes = int(row.get("successes", 0))
    failures = int(row.get("failures", 0))
    runs = successes + failures
    if runs < 2:
        return 0.0
    rate = successes / runs
    return max(-30.0, min(30.0, (rate - 0.5) * 60.0))
