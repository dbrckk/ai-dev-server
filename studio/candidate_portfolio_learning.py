"""Learn verified efficiency of speculative candidate portfolio widths."""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

ALPHA = 0.25
MIN_SAMPLES = 4
MAX_WIDTH = 3


def _key(width: int) -> str:
    return "width:" + str(max(1, min(MAX_WIDTH, int(width))))


def load(path: Path) -> dict:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


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


def record(
    path: Path,
    *,
    width: int,
    success: bool,
    cost_seconds: float,
) -> dict:
    data = load(path)
    key = _key(width)
    row = data.get(key, {
        "samples": 0,
        "successes": 0,
        "ema_success": 0.0,
        "ema_cost_seconds": 0.0,
    })
    samples = int(row.get("samples", 0) or 0)
    observed = 1.0 if success else 0.0
    cost = max(0.0, float(cost_seconds or 0.0))
    previous_success = float(row.get("ema_success", 0.0) or 0.0)
    previous_cost = float(row.get("ema_cost_seconds", 0.0) or 0.0)
    row = {
        "samples": samples + 1,
        "successes": int(row.get("successes", 0) or 0) + int(success),
        "ema_success": (
            observed if samples == 0
            else ALPHA * observed + (1.0 - ALPHA) * previous_success
        ),
        "ema_cost_seconds": (
            cost if samples == 0
            else ALPHA * cost + (1.0 - ALPHA) * previous_cost
        ),
    }
    data[key] = row
    _save(path, data)
    return data


def recommendation(data: dict) -> dict:
    rows = []
    for width in range(1, MAX_WIDTH + 1):
        row = data.get(_key(width)) if isinstance(data, dict) else None
        if not isinstance(row, dict):
            continue
        samples = int(row.get("samples", 0) or 0)
        if samples < MIN_SAMPLES:
            continue
        success = max(0.0, min(1.0, float(row.get("ema_success", 0.0) or 0.0)))
        cost = max(1.0, float(row.get("ema_cost_seconds", 0.0) or 0.0))
        # Reward verified success first; cost only breaks close outcomes.
        utility = success * 100.0 - min(30.0, cost / 30.0)
        rows.append({
            "width": width,
            "samples": samples,
            "ema_success": round(success, 4),
            "ema_cost_seconds": round(cost, 2),
            "utility": round(utility, 4),
        })
    rows.sort(key=lambda row: (-row["utility"], -row["ema_success"], row["width"]))
    return {
        "recommended_width": rows[0]["width"] if rows else None,
        "rankings": rows,
        "minimum_samples": MIN_SAMPLES,
    }
