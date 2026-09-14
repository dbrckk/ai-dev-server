"""Learn whether portfolio diversity and independent review improve verified outcomes."""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

ALPHA = 0.25
MIN_SAMPLES = 4
MAX_ROWS = 32


def _bucket(audit: dict) -> str:
    independent = audit.get("review_independent")
    try:
        diversity = float(audit.get("diversity_ratio", 0.0) or 0.0)
    except (TypeError, ValueError):
        diversity = 0.0
    if diversity >= 0.75:
        diversity_bucket = "high"
    elif diversity >= 0.40:
        diversity_bucket = "medium"
    else:
        diversity_bucket = "low"
    independent_bucket = (
        "independent"
        if independent is True
        else "same_identity"
        if independent is False
        else "unknown"
    )
    return independent_bucket + "|" + diversity_bucket


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
            ema = max(0.0, min(1.0, float(row.get("ema_success", 0.0))))
        except (TypeError, ValueError):
            continue
        clean[key] = {
            "samples": samples,
            "successes": successes,
            "ema_success": ema,
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


def record(path: Path, *, audit: dict, success: bool) -> dict:
    data = load(path)
    key = _bucket(audit)
    row = data.get(key, {"samples": 0, "successes": 0, "ema_success": 0.0})
    samples = int(row["samples"])
    observed = 1.0 if success else 0.0
    previous = float(row.get("ema_success", 0.0))
    ema = observed if samples == 0 else ALPHA * observed + (1.0 - ALPHA) * previous
    data[key] = {
        "samples": samples + 1,
        "successes": int(row["successes"]) + int(success),
        "ema_success": ema,
    }
    _save(path, data)
    return data


def recommendation(data: dict) -> dict:
    eligible = []
    for key, row in data.items():
        if not isinstance(row, dict):
            continue
        samples = int(row.get("samples", 0) or 0)
        if samples < MIN_SAMPLES:
            continue
        eligible.append({
            "portfolio_class": key,
            "samples": samples,
            "ema_success": round(float(row.get("ema_success", 0.0)), 4),
        })
    eligible.sort(key=lambda row: (-row["ema_success"], -row["samples"], row["portfolio_class"]))
    return {
        "recommended_class": eligible[0]["portfolio_class"] if eligible else None,
        "rankings": eligible,
        "minimum_samples": MIN_SAMPLES,
    }
