"""Repair-strategy selection and cross-project efficiency learning."""
from __future__ import annotations

import os
from pathlib import Path

from strategy_efficiency import load, record, select_strategy

DEFAULT_STRATEGY = "model_only"
REPAIR_STRATEGIES = {"model_only", "agent_only", "model_to_agent"}


def _path() -> Path | None:
    raw = os.environ.get("STUDIO_STRATEGY_EFFICIENCY_PATH", "")
    return Path(raw) if raw else None


def load_data() -> dict:
    path = _path()
    return load(path) if path is not None else {}


def choose(task: dict | None, *, agent_available: bool) -> dict:
    allowed = {"model_only"}
    if agent_available:
        allowed |= {"agent_only", "model_to_agent"}

    data = load_data()
    selected = select_strategy(data, allowed=allowed)

    if selected is None:
        name = DEFAULT_STRATEGY
        mode = "bootstrap"
        metrics = {}
    else:
        name, metrics = selected
        mode = metrics.get("selection_mode", "learned")

    if task and task.get("rotate_strategy") is True and agent_available:
        previous = task.get("last_strategy")
        alternatives = [
            strategy for strategy in ("agent_only", "model_to_agent", "model_only")
            if strategy in allowed and strategy != previous
        ]
        if alternatives:
            name = alternatives[0]
            mode = "stagnation_rotation"

    return {
        "strategy": name,
        "mode": mode,
        "metrics": metrics,
        "allowed": sorted(allowed),
    }


def record_outcome(strategy: str, *, success: bool, cost_seconds: float) -> None:
    if strategy not in REPAIR_STRATEGIES:
        return
    path = _path()
    if path is None:
        return
    record(path, strategy, success=success, cost_seconds=cost_seconds)
