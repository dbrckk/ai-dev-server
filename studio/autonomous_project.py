"""Persistent fail-closed wrapper around the multi-engine project orchestrator."""
from __future__ import annotations

from pathlib import Path
import json
import os

try:
    from .capability_registry import new_registry, save as save_registry
    from .goal_engine import new_goal, save as save_goal
    from .goal_loop import run_goal
    from .project_memory import new_memory, load as load_memory, save as save_memory
    from .goal_learning import context_for_goal, learn_from_cycle
except ImportError:
    from capability_registry import new_registry, save as save_registry
    from goal_engine import new_goal, save as save_goal
    from goal_loop import run_goal
    from project_memory import new_memory, load as load_memory, save as save_memory
    from goal_learning import context_for_goal, learn_from_cycle


AUTONOMY_DIR = ".autonomy"


def _state_paths(project_out: Path):
    root = Path(project_out) / AUTONOMY_DIR
    return root / "goal.json", root / "capabilities.json", root / "memory.json"


def ensure_project_goal(project_out: Path, goal_id: str, objective: str, *, max_attempts: int = 20):
    goal_path, registry_path, memory_path = _state_paths(project_out)
    if not goal_path.exists():
        save_goal(goal_path, new_goal(
            goal_id,
            objective,
            [{"name": "project_complete", "required_evidence": ["project_completion"]}],
            max_attempts=max_attempts,
        ))
    if not registry_path.exists():
        save_registry(registry_path, new_registry())
    if not memory_path.exists():
        save_memory(memory_path, new_memory())
    return goal_path, registry_path, memory_path


def translate_orchestrator_result(result: dict) -> dict:
    if not isinstance(result, dict):
        return {"failure": "orchestrator returned invalid result"}
    status = result.get("status")
    report = result.get("report")
    next_stage = result.get("next_stage")

    if status == "complete":
        completion = report.get("completion") if isinstance(report, dict) else None
        if not isinstance(completion, dict) or completion.get("finished") is not True:
            return {"blocked_reason": "orchestrator reported complete without completion evidence"}
        return {
            "evidence": {
                "project_completion": {
                    "orchestrator_status": status,
                    "report_status": report.get("status"),
                    "release_status": report.get("release_status"),
                    "finished": True,
                    "next_stage": next_stage,
                }
            }
        }

    if status == "human_action_required":
        action = next_stage if isinstance(next_stage, str) and next_stage else "external_human_action"
        return {"human_action": action}

    if status == "adaptation_required":
        detail = next_stage if isinstance(next_stage, str) and next_stage else "unknown_capability"
        phase = result.get("pending_status") or result.get("promotion_status") or result.get("research_status") or "in_progress"
        return {"failure": f"adaptation_required:{detail}:{phase}"}

    if isinstance(status, str) and status:
        suffix = f":{next_stage}" if isinstance(next_stage, str) and next_stage else ""
        return {"failure": status + suffix}
    return {"failure": "orchestrator result missing status"}


def run_persistent_project(
    request_path,
    project_out,
    work,
    runner,
    deadline,
    clock,
    baseline_sha=None,
    *,
    goal_id="project",
    objective="Complete project with verified release evidence",
    max_attempts=20,
    max_cycles=20,
    run_once=None,
):
    project_out = Path(project_out)
    project_out.mkdir(parents=True, exist_ok=True)
    goal_path, registry_path, memory_path = ensure_project_goal(
        project_out, goal_id, objective, max_attempts=max_attempts
    )
    if run_once is None:
        try:
            from .multi_engine_orchestrator import run_project as run_once
        except ImportError:
            from multi_engine_orchestrator import run_project as run_once

    context_path = project_out / AUTONOMY_DIR / "learned-context.json"

    def context_provider(_goal_state):
        memory = load_memory(memory_path)
        items = context_for_goal(memory, goal_id)
        context_path.write_text(json.dumps(items, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
        return items

    def execute_cycle(_goal_state):
        previous = os.environ.get("STUDIO_LEARNED_CONTEXT_PATH")
        os.environ["STUDIO_LEARNED_CONTEXT_PATH"] = str(context_path)
        try:
            result = run_once(
                request_path, project_out, work, runner, deadline, clock, baseline_sha
            )
        finally:
            if previous is None: os.environ.pop("STUDIO_LEARNED_CONTEXT_PATH", None)
            else: os.environ["STUDIO_LEARNED_CONTEXT_PATH"] = previous
        translated = translate_orchestrator_result(result)
        if translated.get("evidence"):
            translated["tests_passed"] = True
            translated["learning_summary"] = "Verified completion evidence for goal " + goal_id
            translated["learning_tags"] = ["goal-cycle","verified-completion"]
        return translated

    def cycle_observer(goal_state, result):
        if not baseline_sha or len(str(baseline_sha)) != 40: return
        memory = load_memory(memory_path)
        learned = learn_from_cycle(memory, goal_id, goal_state, result, str(baseline_sha))
        if learned != memory: save_memory(memory_path, learned)

    return run_goal(
        goal_path,
        registry_path,
        execute_cycle,
        max_cycles=max_cycles,
        context_provider=context_provider,
        cycle_observer=cycle_observer,
    )
