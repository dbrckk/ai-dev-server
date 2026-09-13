"""Verified-success efficiency memory for execution strategies."""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

ALPHA = 0.25
SUCCESS_ALPHA = 0.25
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
            successes = min(successes, samples)
            ema_cost = max(0.0, float(row.get("ema_cost_seconds", 0.0)))
            fallback_rate = (successes / samples) if samples else 0.0
            ema_success = float(row.get("ema_success_rate", fallback_rate))
            ema_success = max(0.0, min(1.0, ema_success))
        except (TypeError, ValueError):
            continue
        clean[name] = {
            "samples": samples,
            "successes": successes,
            "ema_cost_seconds": ema_cost,
            "ema_success_rate": ema_success,
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
    row = data.get(strategy, {
        "samples": 0,
        "successes": 0,
        "ema_cost_seconds": 0.0,
        "ema_success_rate": 0.0,
    })
    samples = int(row["samples"])
    cost = max(0.0, float(cost_seconds))
    previous = float(row["ema_cost_seconds"])
    ema = cost if samples == 0 else (ALPHA * cost + (1.0 - ALPHA) * previous)
    observed_success = 1.0 if success else 0.0
    previous_success = float(
        row.get(
            "ema_success_rate",
            (int(row["successes"]) / samples) if samples else observed_success,
        )
    )
    ema_success = (
        observed_success
        if samples == 0
        else SUCCESS_ALPHA * observed_success + (1.0 - SUCCESS_ALPHA) * previous_success
    )
    data[strategy] = {
        "samples": samples + 1,
        "successes": int(row["successes"]) + int(bool(success)),
        "ema_cost_seconds": ema,
        "ema_success_rate": max(0.0, min(1.0, ema_success)),
    }
    _save(path, data)
    return data


def metrics(data: dict, strategy: str) -> dict | None:
    row = data.get(strategy)
    if not isinstance(row, dict) or int(row.get("samples", 0)) < MIN_SAMPLES:
        return None
    samples = int(row["samples"])
    successes = int(row["successes"])
    cumulative_success_rate = successes / samples if samples else 0.0
    recent_success_rate = max(
        0.0,
        min(1.0, float(row.get("ema_success_rate", cumulative_success_rate))),
    )
    # Blend long-term evidence with recent behavior. Recent performance gets
    # more weight so regime changes are detected without discarding history.
    success_rate = 0.4 * cumulative_success_rate + 0.6 * recent_success_rate
    cost = max(1.0, float(row.get("ema_cost_seconds", 0.0)))
    # Scale to verified successes per 100 seconds for readable values.
    efficiency = success_rate * 100.0 / cost
    return {
        "samples": samples,
        "success_rate": success_rate,
        "cumulative_success_rate": cumulative_success_rate,
        "recent_success_rate": recent_success_rate,
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
    candidates.sort(key=lambda item: (
        -item[1]["efficiency"],
        -item[1]["recent_success_rate"],
        -item[1]["success_rate"],
        item[1]["ema_cost_seconds"],
        item[0],
    ))
    return candidates[0]


EXPLORATION_EVERY = 6
MIN_EXPLORATION_EVERY = 4
MAX_EXPLORATION_EVERY = 12


def exploration_cadence(data: dict, *, allowed: set[str] | None = None) -> int:
    """Return a deterministic exploration interval from evidence strength.

    Close strategies or shallow evidence explore more often. A durable,
    materially superior winner explores less often, but never less frequently
    than MAX_EXPLORATION_EVERY.
    """
    allowed_set = set(VALID_STRATEGIES if allowed is None else allowed) & VALID_STRATEGIES
    mature = []
    for strategy in allowed_set:
        info = metrics(data, strategy)
        if info is not None:
            mature.append((strategy, info))
    if not mature:
        return EXPLORATION_EVERY
    mature.sort(key=lambda item: (-item[1]["efficiency"], item[0]))
    winner = mature[0][1]
    winner_samples = int(winner["samples"])
    if len(mature) == 1:
        if winner_samples >= 16:
            return 10
        if winner_samples >= 8:
            return 8
        return EXPLORATION_EVERY
    runner_up = mature[1][1]
    best_eff = float(winner["efficiency"])
    second_eff = float(runner_up["efficiency"])
    relative_gap = 0.0 if best_eff <= 0 else max(0.0, (best_eff - second_eff) / best_eff)
    evidence = min(winner_samples, int(runner_up["samples"]))
    if relative_gap < 0.10 or evidence < 6:
        return MIN_EXPLORATION_EVERY
    if relative_gap < 0.25 or evidence < 12:
        return EXPLORATION_EVERY
    if relative_gap < 0.50 or evidence < 20:
        return 8
    return MAX_EXPLORATION_EVERY


def select_strategy(
    data: dict,
    *,
    allowed: set[str] | None = None,
    exploration_every: int | None = None,
) -> tuple[str, dict] | None:
    """Deterministic bounded explore/exploit policy.

    Exploit the best mature strategy most of the time. Every Nth observed
    decision, explore the least-sampled allowed alternative so stale winners
    can be challenged without introducing randomness.
    """
    if exploration_every is not None and (type(exploration_every) is not int or exploration_every < 2):
        raise ValueError("exploration cadence invalid")
    allowed_set = set(VALID_STRATEGIES if allowed is None else allowed)
    allowed_set &= VALID_STRATEGIES
    if not allowed_set:
        return None

    exploit = best_strategy(data, allowed=allowed_set)
    if exploit is None:
        return None

    cadence = exploration_cadence(data, allowed=allowed_set) if exploration_every is None else exploration_every
    total_samples = sum(
        max(0, int(data.get(name, {}).get("samples", 0)))
        for name in allowed_set
        if isinstance(data.get(name), dict)
    )
    if total_samples > 0 and total_samples % cadence == 0:
        exploit_name = exploit[0]
        alternatives = [name for name in allowed_set if name != exploit_name]
        if alternatives:
            alternatives.sort(
                key=lambda name: (
                    max(0, int(data.get(name, {}).get("samples", 0)))
                    if isinstance(data.get(name), dict) else 0,
                    name,
                )
            )
            selected = alternatives[0]
            selected_metrics = metrics(data, selected)
            info = dict(selected_metrics or {
                "samples": max(0, int(data.get(selected, {}).get("samples", 0)))
                if isinstance(data.get(selected), dict) else 0,
                "success_rate": 0.0,
                "ema_cost_seconds": max(1.0, float(data.get(selected, {}).get("ema_cost_seconds", 0.0)))
                if isinstance(data.get(selected), dict) else 1.0,
                "efficiency": 0.0,
            })
            info["selection_mode"] = "explore"
            info["exploited_strategy"] = exploit_name
            info["exploration_cadence"] = cadence
            return selected, info

    info = dict(exploit[1])
    info["selection_mode"] = "exploit"
    info["exploration_cadence"] = cadence
    return exploit[0], info
