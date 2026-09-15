"""Read-only status for an autonomous project output directory."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from .durable_state import load as load_runtime_state
    from .goal_engine import load as load_goal, missing_evidence
except ImportError:
    from durable_state import load as load_runtime_state
    from goal_engine import load as load_goal, missing_evidence


AUTONOMY_DIR = ".autonomy"


def _read_handoff(project_out: Path) -> dict | None:
    path = project_out / "user-input-required.json"
    if not path.is_file():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {"status": "unreadable"}
    if not isinstance(value, dict):
        return {"status": "invalid"}
    return value


def read_status(project_out: Path | str) -> dict:
    """Return persisted status without invoking models, verifiers or project code."""
    project_out = Path(project_out)
    autonomy_root = project_out / AUTONOMY_DIR
    goal = load_goal(autonomy_root / "goal.json")
    runtime_path = autonomy_root / "runtime-state.json"
    runtime = load_runtime_state(runtime_path, default={}) if runtime_path.is_file() else {}
    handoff = _read_handoff(project_out)
    completion = (goal.get("evidence") or {}).get("project_completion")

    return {
        "goal_id": goal.get("goal_id"),
        "objective": goal.get("objective"),
        "status": goal.get("status"),
        "attempt": goal.get("attempt"),
        "max_attempts": goal.get("max_attempts"),
        "missing_evidence": missing_evidence(goal),
        "missing_capabilities": list(goal.get("missing_capabilities") or []),
        "human_action_required": goal.get("status") == "human_action_required",
        "human_action": goal.get("human_action"),
        "blocked_reason": goal.get("blocked_reason"),
        "runtime_status": runtime.get("status") if isinstance(runtime, dict) else None,
        "runtime_attempt": runtime.get("attempt") if isinstance(runtime, dict) else None,
        "completion_evidence": completion,
        "handoff": handoff,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Read autonomous project status without executing work")
    parser.add_argument("--project-out", required=True, help="Autonomous project output directory")
    parser.add_argument("--compact", action="store_true", help="Emit compact JSON")
    args = parser.parse_args(argv)

    status = read_status(Path(args.project_out))
    if args.compact:
        print(json.dumps(status, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    else:
        print(json.dumps(status, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
