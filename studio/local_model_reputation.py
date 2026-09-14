"""Persistent per-model reputation learned from real routed executions."""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

ALPHA = 0.25
MIN_SAMPLES = 3
MAX_BONUS = 16.0
MAX_PENALTY = 18.0
MAX_ROWS = 256
QUARANTINE_MIN_VERIFIED = 5
QUARANTINE_VERIFIED_RATE = 0.20
QUARANTINE_PROTOCOL_RATE = 0.60
QUARANTINE_ROUTING_PENALTY = 1000.0


def _key(provider: str, model: str, role: str) -> str:
    return provider + "|" + model + "|" + role


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
            protocol_failures = max(0, int(row.get("protocol_failures", 0)))
            ema_success = max(0.0, min(1.0, float(row.get("ema_success", 0.0))))
            ema_latency = max(0.0, float(row.get("ema_latency_seconds", 0.0)))
            verified_samples = max(0, int(row.get("verified_samples", 0)))
            verified_successes = min(
                verified_samples,
                max(0, int(row.get("verified_successes", 0))),
            )
            ema_verified = max(
                0.0,
                min(1.0, float(row.get("ema_verified_success", 0.0))),
            )
        except (TypeError, ValueError):
            continue
        clean[key] = {
            "samples": samples,
            "successes": successes,
            "protocol_failures": protocol_failures,
            "ema_success": ema_success,
            "ema_latency_seconds": ema_latency,
            "verified_samples": verified_samples,
            "verified_successes": verified_successes,
            "ema_verified_success": ema_verified,
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


def record(
    path: Path,
    *,
    provider: str,
    model: str,
    role: str,
    success: bool,
    latency_seconds: float,
    protocol_failure: bool = False,
) -> dict:
    data = load(path)
    key = _key(provider, model, role)
    row = data.get(key, {
        "samples": 0,
        "successes": 0,
        "protocol_failures": 0,
        "ema_success": 0.0,
        "ema_latency_seconds": 0.0,
        "verified_samples": 0,
        "verified_successes": 0,
        "ema_verified_success": 0.0,
    })
    samples = int(row["samples"])
    observed = 1.0 if success else 0.0
    previous_success = float(row["ema_success"])
    previous_latency = float(row["ema_latency_seconds"])
    latency = max(0.0, float(latency_seconds))
    ema_success = observed if samples == 0 else ALPHA * observed + (1.0 - ALPHA) * previous_success
    ema_latency = latency if samples == 0 else ALPHA * latency + (1.0 - ALPHA) * previous_latency
    data[key] = {
        "samples": samples + 1,
        "successes": int(row["successes"]) + int(success),
        "protocol_failures": int(row["protocol_failures"]) + int(protocol_failure),
        "ema_success": ema_success,
        "ema_latency_seconds": ema_latency,
        "verified_samples": int(row.get("verified_samples", 0)),
        "verified_successes": int(row.get("verified_successes", 0)),
        "ema_verified_success": float(row.get("ema_verified_success", 0.0)),
    }
    _save(path, data)
    return data


def record_verified_outcome(
    path: Path,
    *,
    provider: str,
    model: str,
    role: str,
    verified_success: bool,
) -> dict:
    data = load(path)
    key = _key(provider, model, role)
    row = data.get(key, {
        "samples": 0,
        "successes": 0,
        "protocol_failures": 0,
        "ema_success": 0.0,
        "ema_latency_seconds": 0.0,
        "verified_samples": 0,
        "verified_successes": 0,
        "ema_verified_success": 0.0,
    })
    verified_samples = int(row.get("verified_samples", 0))
    observed = 1.0 if verified_success else 0.0
    previous = float(row.get("ema_verified_success", 0.0))
    ema_verified = (
        observed
        if verified_samples == 0
        else ALPHA * observed + (1.0 - ALPHA) * previous
    )
    row["verified_samples"] = verified_samples + 1
    row["verified_successes"] = int(row.get("verified_successes", 0)) + int(verified_success)
    row["ema_verified_success"] = ema_verified
    data[key] = row
    _save(path, data)
    return data


def score(data: dict, *, provider: str, model: str, role: str) -> float:
    row = data.get(_key(provider, model, role)) if isinstance(data, dict) else None
    if not isinstance(row, dict):
        return 0.0
    samples = int(row.get("samples", 0) or 0)
    verified_samples = int(row.get("verified_samples", 0) or 0)
    if samples < MIN_SAMPLES and verified_samples < MIN_SAMPLES:
        return 0.0

    protocol_success = max(0.0, min(1.0, float(row.get("ema_success", 0.0))))
    protocol_rate = min(1.0, int(row.get("protocol_failures", 0) or 0) / max(1, samples))
    verified_success = max(
        0.0,
        min(1.0, float(row.get("ema_verified_success", 0.0))),
    )

    if verified_samples >= MIN_SAMPLES:
        blended = 0.75 * verified_success + 0.25 * protocol_success
    else:
        blended = protocol_success

    centered = (blended - 0.5) * 2.0
    base = centered * (MAX_BONUS if centered >= 0 else MAX_PENALTY)
    penalty = protocol_rate * 8.0
    return round(max(-MAX_PENALTY, min(MAX_BONUS, base - penalty)), 4)


def quarantine_status(
    data: dict,
    *,
    provider: str,
    model: str,
    role: str,
) -> dict:
    row = data.get(_key(provider, model, role)) if isinstance(data, dict) else None
    if not isinstance(row, dict):
        return {"quarantined": False, "reason": None}

    samples = int(row.get("samples", 0) or 0)
    verified_samples = int(row.get("verified_samples", 0) or 0)
    verified_success = max(
        0.0,
        min(1.0, float(row.get("ema_verified_success", 0.0))),
    )
    protocol_rate = min(
        1.0,
        int(row.get("protocol_failures", 0) or 0) / max(1, samples),
    )

    if (
        verified_samples >= QUARANTINE_MIN_VERIFIED
        and verified_success < QUARANTINE_VERIFIED_RATE
    ):
        return {
            "quarantined": True,
            "reason": "repeated_verified_failure",
        }

    if (
        samples >= QUARANTINE_MIN_VERIFIED
        and protocol_rate >= QUARANTINE_PROTOCOL_RATE
    ):
        return {
            "quarantined": True,
            "reason": "protocol_instability",
        }

    return {"quarantined": False, "reason": None}


def snapshot(data: dict) -> list[dict]:
    rows = []
    for key, row in data.items():
        if not isinstance(row, dict):
            continue
        parts = key.split("|", 2)
        if len(parts) != 3:
            continue
        provider, model, role = parts
        rows.append({
            "provider": provider,
            "model": model,
            "role": role,
            **row,
            "routing_score": score(data, provider=provider, model=model, role=role),
            "quarantine": quarantine_status(
                data,
                provider=provider,
                model=model,
                role=role,
            ),
        })
    rows.sort(key=lambda item: (-item["routing_score"], -item["samples"], item["provider"], item["model"]))
    return rows
