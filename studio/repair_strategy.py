"""Repair-strategy selection and cross-project efficiency learning."""
from __future__ import annotations

import os
from pathlib import Path

from strategy_efficiency import load, metrics as strategy_metrics, record, select_strategy
from contextual_strategy_efficiency import load as load_contextual, record as record_contextual, rows_for

DEFAULT_STRATEGY = "model_only"
REPAIR_STRATEGIES = {"model_only", "agent_only", "model_to_agent", "agent_to_model"}

RISK_PRIOR = {
    "model_only": 0.15,
    "agent_only": 0.25,
    "model_to_agent": 0.35,
    "agent_to_model": 0.35,
}
CALL_COST_PRIOR = {
    "model_only": 1,
    "agent_only": 0,
    "model_to_agent": 1,
    "agent_to_model": 1,
}


def rank_candidates(data: dict, allowed: set[str]) -> list[dict]:
    rows = []
    for strategy in sorted(allowed):
        info = strategy_metrics(data, strategy)
        success = float(info.get("conservative_success_rate", 0.5)) if info else 0.5
        seconds = float(info.get("ema_cost_seconds", 30.0)) if info else 30.0
        risk = float(RISK_PRIOR.get(strategy, 0.4))
        calls = int(CALL_COST_PRIOR.get(strategy, 1))
        score = success * 100.0 - min(25.0, seconds / 12.0) - risk * 30.0 - calls * 4.0
        rows.append({
            "strategy": strategy,
            "score": round(score, 3),
            "conservative_success_rate": round(success, 4),
            "estimated_seconds": round(seconds, 3),
            "risk": risk,
            "estimated_model_calls": calls,
            "mature": info is not None,
        })
    return sorted(rows, key=lambda row: (-row["score"], row["strategy"]))



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
        allowed |= {"agent_only", "model_to_agent", "agent_to_model"}

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
            strategy for strategy in ("agent_only", "model_to_agent", "agent_to_model", "model_only")
            if strategy in allowed and strategy != previous
        ]
        if alternatives:
            name = alternatives[0]
            mode = "stagnation_rotation"

    ranking_source = contextual_rows if source == "stage_context" else data
    return {
        "strategy": name,
        "mode": mode,
        "metrics": metrics,
        "allowed": sorted(allowed),
        "evidence_source": source,
        "candidate_ranking": rank_candidates(ranking_source, allowed),
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
