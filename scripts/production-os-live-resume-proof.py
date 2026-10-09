"""Two real GitHub Actions jobs proving durable Production-OS goal restoration.

Uses a unique synthetic workflow ID for this Actions run. Does not claim a
production job, invoke a coding model, or write to the target repo main branch.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "studio"))

from capability_registry import new_registry, save as save_registry
from execution_checkpoint import (
    advance, load as load_checkpoint, new as new_checkpoint,
    save as save_checkpoint,
)
from github_execution_checkpoint_store import (
    load as load_remote_checkpoint,
    persist_local as persist_remote_checkpoint,
    restore_local as restore_remote_checkpoint,
)
from github_goal_store import (
    load as load_remote_goal,
    persist_local as persist_remote_goal,
    restore_local as restore_remote_goal,
)
from goal_engine import (
    finalize, load as load_goal, new_goal,
    record_cycle, save as save_goal,
)
from improvement_backlog import new_backlog, save as save_backlog
from production_os_worker import build_studio_request
from run import GitHub


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("checkpoint", "resume"), required=True)
    args = parser.parse_args(argv)

    run_id = os.environ.get("GITHUB_RUN_ID", "")
    control_repo = os.environ.get("GITHUB_REPOSITORY", "")
    baseline_sha = os.environ.get("GITHUB_SHA", "")
    if not run_id.isdigit() or not control_repo or not os.environ.get("STUDIO_GITHUB_TOKEN"):
        raise RuntimeError("Live resume proof requires an authenticated GitHub Actions run")
    if os.environ.get("GITHUB_REF") != "refs/heads/main":
        raise RuntimeError("Live resume proof only runs from trusted main")
    if len(baseline_sha) != 40 or any(c not in "0123456789abcdef" for c in baseline_sha):
        raise RuntimeError("Live resume proof requires a pinned revision")

    digest = hashlib.sha256(("production-os-resume-proof:" + run_id).encode()).hexdigest()
    workflow_id = digest[:32]
    attempt = 1 if args.phase == "checkpoint" else 2
    job = {
        "key": "resume-proof-" + run_id + "-attempt-" + str(attempt),
        "repository": control_repo,
        "task": "Verify resumable production project state",
        "payload": {
            "workflow_id": workflow_id,
            "workflow_task_id": "resume-proof",
            "workflow_attempt": attempt,
            "handoff": {
                "repository": control_repo,
                "task": "Verify resumable production project state",
                "final_goal": "Verify resumable production project state",
            },
        },
    }
    request = build_studio_request(job)
    goal_id = request["id"]
    gh = GitHub(control_repo)

    with TemporaryDirectory(prefix="production-os-live-resume-") as td:
        out = Path(td)
        goal_path = out / ".autonomy/goal.json"
        checkpoint_path = out / ".autonomy/generic-execution-checkpoint.json"

        if args.phase == "checkpoint":
            if restore_remote_goal(gh, goal_id, out):
                raise RuntimeError("Isolated synthetic project unexpectedly has prior goal state")
            if restore_remote_checkpoint(gh, goal_id, checkpoint_path):
                raise RuntimeError("Isolated synthetic project unexpectedly has a prior checkpoint")

            goal = new_goal(
                goal_id,
                "Verify resumable production project state",
                [{"name": "accepted", "required_evidence": ["build", "tests"]}],
                max_attempts=3,
            )
            goal = record_cycle(goal, evidence={"build": "already-done"})
            save_goal(goal_path, goal)
            save_registry(out / ".autonomy/capabilities.json", new_registry())
            save_backlog(out / ".autonomy/improvement-backlog.json", new_backlog())
            checkpoint = advance(
                new_checkpoint(goal_id, "production-os-canary", baseline_sha),
                round_index=1,
                phase="implemented",
                last_verification={"build": "already-done"},
            )
            save_checkpoint(checkpoint_path, checkpoint)
            persist_remote_goal(gh, goal_id, out)
            persist_remote_checkpoint(gh, goal_id, checkpoint_path)
            result = {
                "phase": "checkpoint",
                "saved": True,
                "attempt": goal["attempt"],
                "checkpoint_round": checkpoint["round"],
                "workflow_attempt": attempt,
            }
        else:
            if not restore_remote_goal(gh, goal_id, out):
                raise RuntimeError("Required prior remote goal state was not found")
            if not restore_remote_checkpoint(gh, goal_id, checkpoint_path):
                raise RuntimeError("Required remote execution checkpoint was not found")
            goal = load_goal(goal_path)
            checkpoint = load_checkpoint(checkpoint_path)
            if (goal["attempt"], goal["status"], goal["evidence"]) != (
                1, "active", {"build": "already-done"}
            ):
                raise RuntimeError("Remote goal progress was lost or mutated")
            if (
                checkpoint["project_id"] != goal_id
                or checkpoint["round"] != 1
                or checkpoint["phase"] != "implemented"
                or checkpoint["last_verification"] != {"build": "already-done"}
            ):
                raise RuntimeError("Remote execution checkpoint was lost or mutated")
            goal = finalize(record_cycle(goal, evidence={"tests": "verified"}))
            checkpoint = advance(checkpoint, round_index=2, phase="complete")
            save_goal(goal_path, goal)
            save_checkpoint(checkpoint_path, checkpoint)
            persist_remote_goal(gh, goal_id, out)
            persist_remote_checkpoint(gh, goal_id, checkpoint_path)
            live_goal = load_remote_goal(gh, goal_id)
            live_checkpoint = load_remote_checkpoint(gh, goal_id)
            if (
                live_goal is None
                or live_goal["goal"]["status"] != "complete"
                or live_goal["goal"]["attempt"] != 2
                or live_checkpoint is None
                or live_checkpoint["phase"] != "complete"
                or live_checkpoint["round"] != 2
            ):
                raise RuntimeError("Final GitHub remote state was not committed")
            result = {
                "phase": "resume",
                "restored": True,
                "completed": True,
                "attempt": goal["attempt"],
                "checkpoint_round": checkpoint["round"],
                "workflow_attempt": attempt,
            }
    print("Production-OS live two-session resume proof: " + json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
