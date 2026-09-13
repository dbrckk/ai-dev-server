"""Historical phase-cost baselines keyed by toolchain and phase."""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from verification_cost import stack_key

ALPHA = 0.25
MAX_ROWS = 128
MIN_SAMPLES = 4


def _key(toolchain: dict | None, phase: str) -> str:
    return stack_key(toolchain) + ":" + phase


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
            ema = max(0.0, float(row.get("ema_seconds", 0.0)))
            mad = max(0.0, float(row.get("ema_abs_deviation", 0.0)))
        except (TypeError, ValueError):
            continue
        clean[key] = {
            "samples": samples,
            "ema_seconds": ema,
            "ema_abs_deviation": mad,
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


def record(path: Path, toolchain: dict | None, phase: str, observed_seconds: float) -> dict:
    observed = max(0.0, float(observed_seconds))
    data = load(path)
    key = _key(toolchain, phase)
    row = data.get(key, {"samples": 0, "ema_seconds": 0.0, "ema_abs_deviation": 0.0})
    samples = int(row["samples"])
    previous = float(row["ema_seconds"])
    previous_dev = float(row["ema_abs_deviation"])
    if samples == 0:
        ema = observed
        deviation = 0.0
    else:
        delta = abs(observed - previous)
        ema = ALPHA * observed + (1.0 - ALPHA) * previous
        deviation = ALPHA * delta + (1.0 - ALPHA) * previous_dev
    data[key] = {
        "samples": samples + 1,
        "ema_seconds": ema,
        "ema_abs_deviation": deviation,
    }
    _save(path, data)
    return data


def baseline(data: dict, toolchain: dict | None, phase: str) -> dict | None:
    row = data.get(_key(toolchain, phase))
    if not isinstance(row, dict) or int(row.get("samples", 0)) < MIN_SAMPLES:
        return None
    return {
        "samples": int(row["samples"]),
        "ema_seconds": float(row["ema_seconds"]),
        "ema_abs_deviation": float(row["ema_abs_deviation"]),
    }
