"""Record measurable outcomes for trusted architecture decisions."""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

from atomic_file import write_text as atomic_write_text


SUCCESS_STATUSES = {
    "validated_preview",
    "finished",
    "complete",
    "technical_store_ready",
    "godot_preview_validated",
    "godot_technical_store_ready",
    "godot_play_validated",
    "godot_published",
}


def _count(value) -> int:
    if isinstance(value, bool):
        return 0
    if isinstance(value, int):
        return max(0, value)
    if isinstance(value, (list, tuple, set, dict)):
        return len(value)
    return 0


def _decision_id(decision: dict) -> str:
    raw = json.dumps(decision, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def build(state: dict) -> dict:
    decision = state.get("architecture_decision")
    if not isinstance(decision, dict):
        decision = {"status": "unavailable", "chosen": []}
    chosen = decision.get("chosen")
    chosen = chosen if isinstance(chosen, list) else []
    status = str(state.get("status", "unknown"))
    blockers = state.get("blockers")
    blockers = blockers if isinstance(blockers, list) else []
    evaluation = state.get("architecture_evaluation")
    if not isinstance(evaluation, dict):
        evaluation = {}
    benchmark = state.get("architecture_benchmark")
    if not isinstance(benchmark, dict):
        benchmark = {}
    migration_candidates = benchmark.get("migration_candidates")
    migration_candidates = migration_candidates if isinstance(migration_candidates, list) else []
    return {
        "schema": 1,
        "observed_at": round(time.time(), 3),
        "decision_id": _decision_id(decision),
        "decision_status": decision.get("status"),
        "evaluation_verdict": evaluation.get("verdict"),
        "evaluation_confidence": evaluation.get("confidence"),
        "benchmark_status": benchmark.get("status"),
        "migration_candidate_count": len(migration_candidates),
        "chosen_repositories": [
            row.get("repo")
            for row in chosen
            if isinstance(row, dict) and isinstance(row.get("repo"), str)
        ][:12],
        "chosen_contexts": [
            {
                "repo": row.get("repo"),
                "domain": row.get("domain"),
                "tier": row.get("tier"),
            }
            for row in chosen
            if isinstance(row, dict) and isinstance(row.get("repo"), str)
        ][:12],
        "decision_constraints": dict(decision.get("constraints") or {}),
        "outcome": {
            "status": status,
            "successful": status in SUCCESS_STATUSES,
            "cycles": _count(state.get("cycles", 0)),
            "rounds": _count(state.get("rounds", 0)),
            "model_calls_this_cycle": int(state.get("model_calls_this_cycle", 0) or 0),
            "checkpoint_replays_this_cycle": int(state.get("checkpoint_replays_this_cycle", 0) or 0),
            "blocker_count": len(blockers),
        },
    }


def write(state: dict, out: Path) -> dict:
    result = build(state)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    atomic_write_text(
        out / "architecture-outcome.json",
        json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return result
