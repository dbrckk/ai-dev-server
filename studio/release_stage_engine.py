"""Shared bounded repair loop for release QA stages."""
from __future__ import annotations

from diagnostics import classify, repairable, retryable_environment
from core import StudioError
from release_repair import MAX_RELEASE_REPAIR_ROUNDS, attempt as repair_attempt
from release_repair import MAX_MODEL_CALLS_PER_BRANCH
from repair_planner import plan
from repair_queue import begin_attempt, complete_stage_tasks, enqueue, finish_attempt, summarize
from project_budget import branch_should_stop, budget_status, can_spend, configure as configure_budget, record_repair_outcome
from task_scheduler import dispatch as scheduler_dispatch, select as scheduler_select


def evaluate_and_repair(
    root,
    out,
    state: dict,
    req: dict,
    stage: str,
    validator,
) -> dict:
    configure_budget(state, req)
    evidence = validator(root, out)
    history = []
    environment_retries = []

    initial_diagnostics = classify(stage, evidence)
    initial_plan = plan(stage, initial_diagnostics)
    initial_task = None
    if evidence.get("passed") is not True:
        initial_task = enqueue(
            state,
            initial_plan,
            estimated_model_calls=MAX_MODEL_CALLS_PER_BRANCH if initial_plan.get("action") == "repair_code" else 0,
        )

    for retry_index in range(2):
        retryable = retryable_environment(stage, evidence)
        diagnostics = classify(stage, evidence)
        if not retryable:
            break
        if diagnostics["human_or_external"] or diagnostics["prerequisite"] or diagnostics["code"]:
            break
        selected = scheduler_select(state)
        if initial_task is None:
            break
        if selected is not None and selected.get("id") != initial_task.get("id"):
            break
        if initial_task.get("status") in {"pending", "retry"}:
            begin_attempt(initial_task)
        environment_retries.append({
            "retry": retry_index + 1,
            "blockers": list(retryable),
        })
        evidence = validator(root, out)
        finish_attempt(
            initial_task,
            success=evidence.get("passed") is True,
            model_calls=0,
            improved=evidence.get("passed") is True,
        )
        if evidence.get("passed") is True:
            break

    for round_index in range(MAX_RELEASE_REPAIR_ROUNDS):
        diagnostics = classify(stage, evidence)
        if evidence.get("passed") is True:
            break
        if diagnostics["human_or_external"] or diagnostics["environment"] or diagnostics["prerequisite"]:
            break
        if not repairable(stage, evidence):
            break
        repair_plan = plan(stage, diagnostics)
        task = initial_task
        if (
            task is None
            or task.get("action") != repair_plan.get("action")
            or sorted(task.get("blockers", [])) != sorted(repair_plan.get("blockers", []))
        ):
            task = enqueue(state, repair_plan, estimated_model_calls=MAX_MODEL_CALLS_PER_BRANCH)
        selected = scheduler_select(state)
        if task is None or (
            selected is not None and selected.get("id") != task.get("id")
        ):
            history.append({
                "round": round_index + 1,
                "changed": False,
                "deferred": True,
                "scheduler": scheduler_dispatch(state),
            })
            break
        if task is not None and branch_should_stop(task):
            task['status'] = 'exhausted'
            history.append({
                'round': round_index + 1,
                'changed': False,
                'error': 'repair_branch_efficiency_below_threshold',
            })
            break
        if not can_spend(state, MAX_MODEL_CALLS_PER_BRANCH, repair=True):
            history.append({
                'round': round_index + 1,
                'changed': False,
                'error': 'project_repair_budget_exhausted',
            })
            if task is not None:
                task['status'] = 'exhausted'
            break
        if task is not None:
            begin_attempt(task)
        blockers_before = len(evidence.get('blockers', []))
        try:
            result = repair_attempt(
                root,
                state,
                evidence,
                stage,
                req["app_name"],
                task=task,
                artifact_cache_enabled=True,
            )
        except StudioError as exc:
            if task is not None:
                finish_attempt(task, success=False, model_calls=0, improved=False)
            record_repair_outcome(
                state,
                success=False,
                calls=0,
                blockers_before=blockers_before,
                blockers_after=blockers_before,
            )
            history.append({
                "round": round_index + 1,
                "changed": False,
                "error": str(exc),
            })
            break

        history.append({
            "round": round_index + 1,
            "changed": result.get("changed") is True,
            "blockers": list(result.get("blockers", [])),
            "model_calls": result.get("model_calls", 0),
            "models_used": dict(result.get("models_used", {})),
            "providers_used": dict(result.get("providers_used", {})),
            "gate_count": result.get("gate_count", 0),
            "strategy": result.get("strategy"),
            "strategy_selection": result.get("strategy_selection"),
            "strategy_cost_seconds": result.get("strategy_cost_seconds"),
            "agent": result.get("agent"),
        })
        if task is not None:
            finish_attempt(
                task,
                success=result.get("changed") is True,
                model_calls=result.get("model_calls", 0),
                improved=result.get("changed") is True,
                providers_used=result.get("providers_used", {}),
                strategy=result.get("strategy"),
                strategy_cost_seconds=result.get("strategy_cost_seconds"),
            )
        record_repair_outcome(
            state,
            success=result.get("changed") is True,
            calls=result.get("model_calls", 0),
            blockers_before=blockers_before,
            blockers_after=0 if result.get("changed") is True else blockers_before,
        )
        if result.get("changed") is not True:
            break
        evidence = {
            "passed": False,
            "blockers": ["release_artifact_rebuild_required"],
            "source_repaired": True,
            "repaired_stage": stage,
        }
        break

    diagnostics = classify(stage, evidence)
    evidence["diagnostics"] = diagnostics
    evidence["repair_plan"] = plan(stage, diagnostics)
    if evidence.get("passed") is True:
        complete_stage_tasks(state, stage)
    else:
        final_plan = evidence["repair_plan"]
        if (
            initial_task is None
            or initial_task.get("action") != final_plan.get("action")
            or sorted(initial_task.get("blockers", [])) != sorted(final_plan.get("blockers", []))
        ):
            enqueue(
                state,
                final_plan,
                estimated_model_calls=MAX_MODEL_CALLS_PER_BRANCH if final_plan.get("action") == "repair_code" else 0,
            )
    evidence["scheduler"] = scheduler_dispatch(state)
    evidence["repair_queue"] = summarize(state)
    evidence["project_budget"] = budget_status(state)
    evidence["environment_retry"] = {
        "attempted": bool(environment_retries),
        "retries": environment_retries,
        "max_retries": 2,
        "converged": evidence.get("passed") is True,
    }
    evidence["agentic_remediation"] = {
        "attempted": bool(history),
        "rounds": history,
        "max_rounds": MAX_RELEASE_REPAIR_ROUNDS,
        "converged": evidence.get("passed") is True,
    }
    return evidence


def apply_external_gate(state: dict, stage: str, evidence: dict) -> bool:
    diagnostics = evidence.get("diagnostics") or classify(stage, evidence)
    blockers = list(diagnostics.get("human_or_external", []))
    if not blockers:
        return False
    state["human_action"] = {
        "action": "release_external_evidence_required",
        "stage": stage,
        "detail": "Provide or verify external evidence that cannot be safely fabricated by the autonomous runner.",
        "blockers": blockers,
    }
    state["status"] = "human_action_required"
    state["release_status"] = "human_action_required"
    return True



def invalidate_for_source_change(state: dict, evidence: dict) -> bool:
    if evidence.get("source_repaired") is not True:
        return False
    state["release_evidence"] = {}
    state["release_status"] = "not_store_ready"
    return True
