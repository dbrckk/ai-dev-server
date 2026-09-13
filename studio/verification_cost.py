"""Persistent verification-cost memory keyed by detected toolchain."""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

ALPHA = 0.25
MAX_ROWS = 64


def stack_key(toolchain: dict | None) -> str:
    stacks = toolchain.get("stacks") if isinstance(toolchain, dict) else None
    if not isinstance(stacks, list):
        return "unknown"
    clean = sorted({str(x).strip().lower() for x in stacks if str(x).strip()})
    return "+".join(clean) if clean else "unknown"


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
            runs = max(0, int(row.get("runs", 0)))
            successes = max(0, int(row.get("successes", 0)))
            ema = max(0.0, float(row.get("ema_seconds", 0.0)))
        except (TypeError, ValueError):
            continue
        clean[key] = {"runs": runs, "successes": min(successes, runs), "ema_seconds": ema}
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


def record(path: Path, toolchain: dict | None, *, elapsed_seconds: float, success: bool) -> dict:
    key = stack_key(toolchain)
    data = load(path)
    row = data.get(key, {"runs": 0, "successes": 0, "ema_seconds": 0.0})
    runs = int(row["runs"])
    previous = float(row["ema_seconds"])
    elapsed = max(0.0, float(elapsed_seconds))
    ema = elapsed if runs == 0 else (ALPHA * elapsed + (1.0 - ALPHA) * previous)
    data[key] = {
        "runs": runs + 1,
        "successes": int(row["successes"]) + int(bool(success)),
        "ema_seconds": ema,
    }
    _save(path, data)
    return data


def estimate_seconds(data: dict, toolchain: dict | None, *, fallback: float | None = None) -> float | None:
    row = data.get(stack_key(toolchain))
    if isinstance(row, dict) and int(row.get("runs", 0)) >= 2:
        return max(0.0, float(row.get("ema_seconds", 0.0)))
    return fallback
