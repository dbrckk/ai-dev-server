"""Shared bounded repair loop for release QA stages."""
from __future__ import annotations

from diagnostics import classify, repairable, retryable_environment
from core import StudioError
from release_repair import MAX_RELEASE_REPAIR_ROUNDS, attempt as repair_attempt
from repair_planner import plan


def evaluate_and_repair(
    root,
    out,
    state: dict,
    req: dict,
    stage: str,
    validator,
) -> dict:
    evidence = validator(root, out)
    history = []
    environment_retries = []

    for retry_index in range(2):
        retryable = retryable_environment(stage, evidence)
        diagnostics = classify(stage, evidence)
        if not retryable:
            break
        if diagnostics["human_or_external"] or diagnostics["prerequisite"] or diagnostics["code"]:
            break
        environment_retries.append({
            "retry": retry_index + 1,
            "blockers": list(retryable),
        })
        evidence = validator(root, out)
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
        try:
            result = repair_attempt(
                root,
                state,
                evidence,
                stage,
                req["app_name"],
            )
        except StudioError as exc:
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
        })
        if result.get("changed") is not True:
            break
        evidence = validator(root, out)

    diagnostics = classify(stage, evidence)
    evidence["diagnostics"] = diagnostics
    evidence["repair_plan"] = plan(stage, diagnostics)
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
