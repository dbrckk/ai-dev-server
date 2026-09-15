"""Apply checkpoint-safe fleet preemption decisions."""
from __future__ import annotations

import json
from pathlib import Path

from atomic_file import write_text as atomic_write_text
from capacity_ledger import release_project
from execution_checkpoint import load as load_checkpoint, ExecutionCheckpointError
from preemption_controller import SAFE_CHECKPOINT_PHASES

STATE_FILE = "preemption-state.json"


def execute(root: Path | str = "studio-output", *, apply: bool = False) -> dict:
    root = Path(root)
    plan_path = root / "capacity-plan.json"
    try:
        capacity_plan = json.loads(plan_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {"apply": bool(apply), "results": [], "status": "capacity_plan_unavailable"}

    preemption = capacity_plan.get("preemption")
    actions = preemption.get("actions") if isinstance(preemption, dict) else None
    results = []
    for action in actions if isinstance(actions, list) else []:
        if not isinstance(action, dict) or action.get("action") != "preempt":
            continue
        victim = str(action.get("victim_id") or "")
        contender = str(action.get("contender_id") or "")
        row = {"victim_id": victim, "contender_id": contender, "executed": False}
        checkpoint_path = root / victim / ".autonomy" / "execution-checkpoint.json"
        try:
            checkpoint = load_checkpoint(checkpoint_path)
        except (OSError, ExecutionCheckpointError):
            row["status"] = "checkpoint_invalid"
            results.append(row)
            continue
        if checkpoint.get("phase") not in SAFE_CHECKPOINT_PHASES:
            row["status"] = "checkpoint_not_safe"
            results.append(row)
            continue
        if not apply:
            row["status"] = "dry_run"
            results.append(row)
            continue

        released = release_project(root / "capacity-ledger.json", victim)
        state = {
            "schema": 1,
            "victim_id": victim,
            "contender_id": contender,
            "victim_checkpoint": {
                "base_sha": checkpoint.get("base_sha"),
                "round": checkpoint.get("round"),
                "phase": checkpoint.get("phase"),
                "sha256": checkpoint.get("sha256"),
            },
            "released": released,
            "status": "preempted",
        }
        state_path = root / victim / ".autonomy" / STATE_FILE
        atomic_write_text(
            state_path,
            json.dumps(state, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        row["executed"] = True
        row["status"] = "preempted"
        row["released_tokens"] = released.get("released_tokens", 0)
        results.append(row)

    return {
        "apply": bool(apply),
        "status": "complete",
        "preemptions_executed": sum(1 for row in results if row["executed"]),
        "results": results,
    }
