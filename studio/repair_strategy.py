"""Repair-strategy selection and cross-project efficiency learning."""
from __future__ import annotations

import os
from pathlib import Path

from strategy_efficiency import load, record, select_strategy
from contextual_strategy_efficiency import load as load_contextual, record as record_contextual, rows_for

DEFAULT_STRATEGY = "model_only"
REPAIR_STRATEGIES = {"model_only", "agent_only", "model_to_agent"}


def _path() -> Path | None:
    raw = os.environ.get("STUDIO_STRATEGY_EFFICIENCY_PATH", "")
    return Path(raw) if raw else None


def load_data() -> dict:
    path = _path()
    return load(path) if path is not None else {}


def _contextual_path() -> Path | None:
    raw = os.environ.get("STUDIO_CONTEXTUAL_STRATEGY_EFFICIENCY_PATH", "")
    return Path(raw) if raw else None


def _context(stage: str) -> str:
    return "repair:" + stage


def choose(task: dict | None, *, stage: str, agent_available: bool) -> dict:
    allowed = {"model_only"}
    if agent_available:
        allowed |= {"agent_only", "model_to_agent"}

    data = load_data()
    source = "global"
    contextual_path = _contextual_path()
    contextual_rows = {}
    if contextual_path is not None:
        contextual_rows = rows_for(load_contextual(contextual_path), _context(stage))
    selected = select_strategy(contextual_rows, allowed=allowed) if contextual_rows else None
    if selected is not None:
        source = "stage_context"
    else:
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
        "evidence_source": source,
    }


def record_outcome(strategy: str, *, stage: str, success: bool, cost_seconds: float) -> None:
    if strategy not in REPAIR_STRATEGIES:
        return
    path = _path()
    if path is None:
        return
    record(path, strategy, success=success, cost_seconds=cost_seconds)
    contextual_path = _contextual_path()
    if contextual_path is not None:
        record_contextual(
            contextual_path,
            _context(stage),
            strategy,
            success=success,
            cost_seconds=cost_seconds,
        )
