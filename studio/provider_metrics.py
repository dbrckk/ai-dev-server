"""Role-scoped provider performance metrics used by adaptive routing."""
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
            ema = max(0.0, float(row.get("ema_latency_seconds", 0.0)))
        except (TypeError, ValueError):
            continue
        clean[key] = {"calls": calls, "ema_latency_seconds": ema}
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


def record(path: Path, provider: str, role: str, duration_seconds: float) -> dict:
    duration = max(0.0, float(duration_seconds))
    data = load(path)
    key = _key(provider, role)
    row = data.get(key, {"calls": 0, "ema_latency_seconds": 0.0})
    calls = int(row["calls"])
    previous = float(row["ema_latency_seconds"])
    ema = duration if calls == 0 else (ALPHA * duration + (1.0 - ALPHA) * previous)
    data[key] = {"calls": calls + 1, "ema_latency_seconds": ema}
    _save(path, data)
    return data


def latency_bonus(data: dict, provider: str, role: str) -> float:
    """Bounded bonus: fast providers gain modestly, slow ones lose modestly."""
    row = data.get(_key(provider, role))
    if not isinstance(row, dict) or int(row.get("calls", 0)) < 2:
        return 0.0
    latency = float(row.get("ema_latency_seconds", 0.0))
    if latency <= 2.0:
        return 12.0
    if latency <= 5.0:
        return 8.0
    if latency <= 12.0:
        return 4.0
    if latency <= 30.0:
        return 0.0
    if latency <= 60.0:
        return -6.0
    return -12.0
