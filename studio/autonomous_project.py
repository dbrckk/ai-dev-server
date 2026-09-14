"""Persistent fail-closed wrapper around the multi-engine project orchestrator."""
from __future__ import annotations

from pathlib import Path
import json
import os

try:
    from .capability_registry import new_registry, save as save_registry, load as load_registry, register, has_capability
    from .goal_engine import new_goal, save as save_goal
    from .goal_loop import run_goal
    from .promoted_capabilities import sync_into_registry
    from .capability_runtime import execute_capability
    from .project_memory import new_memory, load as load_memory, save as save_memory
    from .goal_learning import context_for_goal, learn_from_cycle
    from .human_input_request import requires_human_input
except ImportError:
    from capability_registry import new_registry, save as save_registry, load as load_registry, register, has_capability
    from goal_engine import new_goal, save as save_goal
    from goal_loop import run_goal
    from promoted_capabilities import sync_into_registry
    from capability_runtime import execute_capability
    from project_memory import new_memory, load as load_memory, save as save_memory
    from goal_learning import context_for_goal, learn_from_cycle
    from human_input_request import requires_human_input


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
        save_registry(registry_path, sync_into_registry(new_registry()))
    else:
        current_registry = load_registry(registry_path)
        promoted_registry = sync_into_registry(current_registry)
        if promoted_registry != current_registry:
            save_registry(registry_path, promoted_registry)
    if not memory_path.exists():
        save_memory(memory_path, new_memory())
    return goal_path, registry_path, memory_path


def _sync_promoted_capabilities(registry_path: Path, repo_root: Path = Path(".")):
    path = repo_root / "control" / "promoted_stages.json"
    if not path.is_file():
        return
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return
    stages = value.get("stages") if isinstance(value, dict) else None
    if not isinstance(stages, dict):
        return
    registry = load_registry(registry_path)
    changed = False
    for name, item in sorted(stages.items()):
        if has_capability(registry, name) or not isinstance(item, dict):
            continue
        script = item.get("script")
        candidate_id = item.get("candidate_id")
        candidate_sha = item.get("candidate_sha")
        if not all(isinstance(x, str) and x for x in (script, candidate_id, candidate_sha)):
            continue
        registry = register(registry, name, script, {
            "source": "promoted_stage_registry",
            "candidate_id": candidate_id,
            "candidate_sha": candidate_sha,
            "baseline_sha": item.get("baseline_sha"),
        })
        changed = True
    if changed:
        save_registry(registry_path, registry)


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
        return {
            "yield_run": True,
            "evidence": {
                "adaptation_progress": {
                    "capability": detail,
                    "phase": phase,
                    "research_status": result.get("research_status"),
                    "promotion_status": result.get("promotion_status"),
                    "persistence_status": result.get("persistence_status"),
                    "automerge_status": result.get("automerge_status"),
                }
            }
        }

    if isinstance(status, str) and status:
        details = [status]
        if isinstance(next_stage, str) and next_stage:
            details.append(next_stage)
        if isinstance(report, dict):
            blockers = report.get("blockers")
            if isinstance(blockers, list):
                details.extend(str(item) for item in blockers)
        detail = ":".join(details)
        if requires_human_input(detail):
            return {"human_action": detail}
        return {"failure": detail}
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
    autonomy_root = project_out / AUTONOMY_DIR
    autonomy_root.mkdir(parents=True, exist_ok=True)
    runtime_paths = {
        "STUDIO_QUICK_GATE_CACHE_PATH": autonomy_root / "quick-gate-cache.json",
        "STUDIO_FULL_GATE_CACHE_PATH": autonomy_root / "full-gate-cache.json",
        "STUDIO_ARTIFACT_CACHE_PATH": autonomy_root / "artifact-cache.json",
        "STUDIO_ARTIFACT_CAS_PATH": autonomy_root / "artifact-cas",
        "STUDIO_ARTIFACT_CAS_STATS_PATH": autonomy_root / "artifact-cas-stats.json",
        "STUDIO_CHECKPOINT_PATH": autonomy_root / "workflow-checkpoints.json",
        "STUDIO_TELEMETRY_PATH": autonomy_root / "telemetry.jsonl",
    }
    for env_name, env_path in runtime_paths.items():
        os.environ.setdefault(env_name, str(env_path))
    os.environ.setdefault("STUDIO_PROJECT_ID", str(goal_id))
    goal_path, registry_path, memory_path = ensure_project_goal(
        project_out, goal_id, objective, max_attempts=max_attempts
    )
    _sync_promoted_capabilities(registry_path)
    if run_once is None:
        try:
            from .multi_engine_orchestrator import run_project as run_once
        except ImportError:
            from multi_engine_orchestrator import run_project as run_once

    context_path = project_out / AUTONOMY_DIR / "learned-context.json"
    provider_health_path = project_out / AUTONOMY_DIR / "provider-health.json"
    provider_metrics_path = project_out / AUTONOMY_DIR / "provider-metrics.json"
    routing_history_path = project_out / AUTONOMY_DIR / "routing-history.json"

    def context_provider(_goal_state):
        memory = load_memory(memory_path)
        items = context_for_goal(memory, goal_id)
        portfolio_path=project_out/"portfolio-research.json"
        if portfolio_path.is_file():
            try:
                portfolio=json.loads(portfolio_path.read_text())
            except (OSError,json.JSONDecodeError):
                portfolio={}
            for candidate in portfolio.get("similar",[])[:6] if isinstance(portfolio,dict) else []:
                if not isinstance(candidate,dict) or not isinstance(candidate.get("repo"),str):
                    continue
                profile=candidate.get("deep_profile") if isinstance(candidate.get("deep_profile"),dict) else {}
                summary="Similar owned repository: "+candidate["repo"]
                description=candidate.get("description")
                if isinstance(description,str) and description.strip():
                    summary+=" — "+description.strip()
                markers=profile.get("markers") if isinstance(profile.get("markers"),list) else []
                if markers:
                    summary+="; markers: "+", ".join(str(x) for x in markers[:10])
                excerpt=profile.get("readme_excerpt")
                if isinstance(excerpt,str) and excerpt.strip():
                    summary+="; README: "+excerpt.strip()[:700]
                items.append({
                    "summary":summary[:1200],
                    "tags":["portfolio","similar-project"],
                    "same_project":False,
                    "provenance":{"source":candidate["repo"],"kind":"owned_repository"},
                })
        items=items[:20]
        from atomic_file import write_text as atomic_write_text
        atomic_write_text(context_path, json.dumps(items, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
        return items

    def execute_cycle(_goal_state):
        previous = os.environ.get("STUDIO_LEARNED_CONTEXT_PATH")
        previous_health = os.environ.get("STUDIO_PROVIDER_HEALTH_PATH")
        previous_metrics = os.environ.get("STUDIO_PROVIDER_METRICS_PATH")
        previous_history = os.environ.get("STUDIO_ROUTING_HISTORY_PATH")
        os.environ["STUDIO_LEARNED_CONTEXT_PATH"] = str(context_path)
        os.environ["STUDIO_PROVIDER_HEALTH_PATH"] = str(provider_health_path)
        os.environ["STUDIO_PROVIDER_METRICS_PATH"] = str(provider_metrics_path)
        os.environ["STUDIO_ROUTING_HISTORY_PATH"] = str(routing_history_path)
        try:
            result = run_once(
                request_path, project_out, work, runner, deadline, clock, baseline_sha
            )
        finally:
            if previous is None: os.environ.pop("STUDIO_LEARNED_CONTEXT_PATH", None)
            else: os.environ["STUDIO_LEARNED_CONTEXT_PATH"] = previous
            if previous_health is None: os.environ.pop("STUDIO_PROVIDER_HEALTH_PATH", None)
            else: os.environ["STUDIO_PROVIDER_HEALTH_PATH"] = previous_health
            if previous_metrics is None: os.environ.pop("STUDIO_PROVIDER_METRICS_PATH", None)
            else: os.environ["STUDIO_PROVIDER_METRICS_PATH"] = previous_metrics
            if previous_history is None: os.environ.pop("STUDIO_ROUTING_HISTORY_PATH", None)
            else: os.environ["STUDIO_ROUTING_HISTORY_PATH"] = previous_history
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

    def execute_registered_capability(registry, capability, goal_state):
        return execute_capability(
            registry,
            capability,
            {"goal_id": goal_id, "objective": objective, "goal_state": goal_state},
            repo_root=Path("."),
        )

    from durable_state import save as save_durable_state
    from telemetry import emit as emit_telemetry
    runtime_state_path = autonomy_root / "runtime-state.json"
    emit_telemetry("goal_run_started", goal_id=goal_id, max_cycles=max_cycles)
    result = run_goal(
        goal_path,
        registry_path,
        execute_cycle,
        max_cycles=max_cycles,
        context_provider=context_provider,
        cycle_observer=cycle_observer,
        execute_registered_capability=execute_registered_capability,
    )
    save_durable_state(runtime_state_path, {
        "goal_id": goal_id,
        "objective": objective,
        "status": result.get("status"),
        "attempt": result.get("attempt"),
        "evidence_keys": sorted((result.get("evidence") or {}).keys()),
        "missing_capabilities": list(result.get("missing_capabilities") or []),
        "human_action": result.get("human_action"),
        "blocked_reason": result.get("blocked_reason"),
    })
    emit_telemetry("goal_run_finished", goal_id=goal_id, status=result.get("status"))
    return result
