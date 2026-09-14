"""Isolated candidate search for release repair strategies."""
from __future__ import annotations

from pathlib import Path
import time

from flutter_workspace import snapshot as snapshot_workspace, restore as restore_workspace, delta as validate_delta
from core import StudioError, apply_patch, canonical
from journeys import validate_journeys
from repair_search_policy import should_continue_after_quick_failure, should_refine
from diff_quick_gates import plan as plan_quick_gates
from quick_gate_cache import cache_key, delta_hash, get as cache_get, put as cache_put

MAX_CANDIDATES = 2
MAX_BRANCH_STEPS = 3
MAX_LOCAL_REFINEMENTS = 1


def _candidate_score(candidate: dict) -> float:
    if candidate.get("passed") is not True:
        return -1_000_000.0
    changed_count = len(candidate.get("changed_files", []))
    model_calls = max(0, int(candidate.get("model_calls", 0)))
    elapsed = max(0.0, float(candidate.get("elapsed_seconds", 0.0)))
    strategy_prior = float(candidate.get("strategy_prior_score", 0.0))
    return (
        1000.0
        + strategy_prior
        - changed_count * 2.0
        - model_calls * 5.0
        - min(50.0, elapsed / 6.0)
    )


def select_winner(candidates: list[dict]) -> dict | None:
    passing = [item for item in candidates if item.get("passed") is True]
    if not passing:
        return None
    ranked = sorted(
        passing,
        key=lambda item: (-_candidate_score(item), str(item.get("strategy", ""))),
    )
    winner = dict(ranked[0])
    winner["candidate_score"] = round(_candidate_score(winner), 3)
    return winner


def run_candidate(
    root: Path,
    *,
    strategy: str,
    strategy_prior_score: float,
    mutate,
    state: dict,
    app_name: str,
    sandbox_factory,
) -> dict:
    if quick_gate_cache is None:
        quick_gate_cache = {}
    baseline = snapshot_workspace(root)
    started = time.monotonic()
    metadata = {}
    try:
        metadata = mutate()
        delta = validate_delta(root, baseline)
        changed = list(delta.get("changed", []))
        if not changed:
            raise StudioError("Repair candidate produced no source delta")
        journeys = validate_journeys(state.get("product", {}).get("journeys"))
        sandbox = sandbox_factory(root)
        passed, logs = sandbox.gates(app_name, journeys)
        elapsed = max(0.0, time.monotonic() - started)
        candidate = {
            "strategy": strategy,
            "strategy_prior_score": float(strategy_prior_score),
            "passed": passed is True,
            "changed_files": changed,
            "files": list(delta.get("files", [])),
            "gate_count": len(logs),
            "elapsed_seconds": round(elapsed, 3),
            **metadata,
        }
        if not passed:
            candidate["failure"] = canonical(logs[-1:])[-4000:]
        candidate["candidate_score"] = round(_candidate_score(candidate), 3)
        return candidate
    except (StudioError, ValueError) as exc:
        elapsed = max(0.0, time.monotonic() - started)
        return {
            "strategy": strategy,
            "strategy_prior_score": float(strategy_prior_score),
            "passed": False,
            "changed_files": [],
            "files": [],
            "gate_count": 0,
            "elapsed_seconds": round(elapsed, 3),
            "failure": str(exc),
            **metadata,
            "candidate_score": -1_000_000.0,
        }
    finally:
        restore_workspace(root, baseline)


def apply_winner(root: Path, winner: dict) -> None:
    files = winner.get("files", [])
    if not isinstance(files, list) or not files:
        raise StudioError("Winning repair candidate has no patch")
    apply_patch(root, {"files": files})



def run_branch(
    root: Path,
    *,
    strategy: str,
    strategy_prior_score: float,
    steps: list,
    refine,
    state: dict,
    app_name: str,
    sandbox_factory,
    strategy_row: dict | None = None,
    remaining_model_calls: int = 0,
    step_model_calls: list[int] | None = None,
    quick_gate_cache: dict | None = None,
) -> dict:
    if not 1 <= len(steps) <= MAX_BRANCH_STEPS:
        raise StudioError("Repair branch step count invalid")
    if step_model_calls is None:
        step_model_calls = [1] * len(steps)
    if len(step_model_calls) != len(steps) or any(
        type(value) is not int or value < 0 for value in step_model_calls
    ):
        raise StudioError("Repair branch step-cost metadata invalid")
    baseline = snapshot_workspace(root)
    started = time.monotonic()
    metadata = {
        "steps": [],
        "model_calls": 0,
        "models_used": {},
        "providers_used": {},
        "agent": None,
    }
    try:
        pending_failure = None
        for index, step in enumerate(steps, start=1):
            before_step = snapshot_workspace(root)
            step_started = time.monotonic()
            result = step(pending_failure)
            pending_failure = None
            if not isinstance(result, dict):
                result = {}
            step_trace = {
                "step": index,
                "metadata": result,
                "elapsed_seconds": round(max(0.0, time.monotonic() - step_started), 3),
            }
            metadata["model_calls"] += max(0, int(result.get("model_calls", 0)))
            if isinstance(result.get("models_used"), dict):
                metadata["models_used"].update(result["models_used"])
            if isinstance(result.get("providers_used"), dict):
                metadata["providers_used"].update(result["providers_used"])
            if result.get("agent") is not None:
                metadata["agent"] = result.get("agent")

            if index < len(steps):
                step_delta = validate_delta(root, before_step)
                quick_plan = plan_quick_gates(root, list(step_delta.get("changed", [])))
                digest = delta_hash(list(step_delta.get("files", [])))
                step_trace["delta"] = quick_plan
                quick_sandbox = sandbox_factory(root)
                progressive = []
                quick_passed = True
                quick_failure = None
                gate_specs = (
                    ("dependency", "quick_dependency_gate", quick_plan["dependency"]),
                    ("analyze", "quick_analyze_gate", quick_plan["analyze"]),
                    ("test", "quick_test_gate", quick_plan["test"]),
                )
                for gate_name, gate_method_name, required in gate_specs:
                    if not required:
                        progressive.append({
                            "gate": gate_name,
                            "passed": True,
                            "skipped": True,
                            "reason": "delta_not_relevant",
                            "logs": [],
                        })
                        continue
                    gate_method = getattr(quick_sandbox, gate_method_name, None)
                    if gate_method is None:
                        fallback = getattr(quick_sandbox, "quick_gates")
                        gate_ok, gate_logs = fallback()
                        progressive.append({
                            "gate": "compatibility",
                            "passed": gate_ok is True,
                            "skipped": False,
                            "logs": gate_logs,
                        })
                        quick_passed = gate_ok is True
                        if not quick_passed:
                            quick_failure = canonical(gate_logs[-1:])[-4000:]
                        break
                    targets = quick_plan["targeted_tests"] if gate_name == "test" else []
                    key = cache_key(digest, gate_name, targets)
                    cached = cache_get(quick_gate_cache, key)
                    if cached is not None:
                        gate_ok = cached["passed"]
                        gate_logs = cached["logs"]
                        from_cache = True
                    else:
                        if gate_name == "test":
                            try:
                                gate_ok, gate_logs = gate_method(targets)
                            except TypeError:
                                gate_ok, gate_logs = gate_method()
                        else:
                            gate_ok, gate_logs = gate_method()
                        cache_put(
                            quick_gate_cache,
                            key,
                            passed=gate_ok is True,
                            logs=gate_logs,
                        )
                        from_cache = False
                    progressive.append({
                        "gate": gate_name,
                        "passed": gate_ok is True,
                        "skipped": False,
                        "cached": from_cache,
                        "cache_key": key,
                        "mode": quick_plan["test_mode"] if gate_name == "test" else None,
                        "targets": targets,
                        "logs": gate_logs,
                    })
                    if not gate_ok:
                        quick_passed = False
                        quick_failure = canonical(gate_logs[-1:])[-4000:]
                        break
                step_trace["quick_gates"] = {
                    "passed": quick_passed,
                    "progressive": progressive,
                    "failure": quick_failure,
                }
                if not quick_passed:
                    pending_failure = quick_failure
                    next_step_model_calls = step_model_calls[index]
                    if not should_continue_after_quick_failure(
                        next_step_model_calls=next_step_model_calls,
                        remaining_model_calls=max(
                            0,
                            int(remaining_model_calls) - int(metadata["model_calls"]),
                        ),
                        strategy_row=strategy_row or {},
                    ):
                        metadata["steps"].append(step_trace)
                        raise StudioError("Repair branch pruned after failed quick gates")
            metadata["steps"].append(step_trace)

        journeys = validate_journeys(state.get("product", {}).get("journeys"))
        sandbox = sandbox_factory(root)
        passed, logs = sandbox.gates(app_name, journeys)
        refinements = 0
        while (
            not passed
            and refine is not None
            and refinements < MAX_LOCAL_REFINEMENTS
            and should_refine(
                failure_present=True,
                refinement_model_calls=1,
                remaining_model_calls=max(0, int(remaining_model_calls) - int(metadata["model_calls"])),
                strategy_row=strategy_row or {},
            )
        ):
            refinements += 1
            failure = canonical(logs[-1:])[-4000:]
            refine_started = time.monotonic()
            result = refine(failure)
            if not isinstance(result, dict):
                result = {}
            metadata["steps"].append({
                "step": len(metadata["steps"]) + 1,
                "kind": "local_refinement",
                "metadata": result,
                "elapsed_seconds": round(max(0.0, time.monotonic() - refine_started), 3),
            })
            metadata["model_calls"] += max(0, int(result.get("model_calls", 0)))
            if isinstance(result.get("models_used"), dict):
                metadata["models_used"].update(result["models_used"])
            if isinstance(result.get("providers_used"), dict):
                metadata["providers_used"].update(result["providers_used"])
            if result.get("agent") is not None:
                metadata["agent"] = result.get("agent")
            sandbox = sandbox_factory(root)
            passed, logs = sandbox.gates(app_name, journeys)

        delta = validate_delta(root, baseline)
        changed = list(delta.get("changed", []))
        if not changed:
            raise StudioError("Repair branch produced no source delta")
        elapsed = max(0.0, time.monotonic() - started)
        candidate = {
            "strategy": strategy,
            "strategy_prior_score": float(strategy_prior_score),
            "passed": passed is True,
            "changed_files": changed,
            "files": list(delta.get("files", [])),
            "gate_count": len(logs),
            "elapsed_seconds": round(elapsed, 3),
            "refinements": refinements,
            **metadata,
        }
        if not passed:
            candidate["failure"] = canonical(logs[-1:])[-4000:]
        candidate["candidate_score"] = round(_candidate_score(candidate), 3)
        return candidate
    except (StudioError, ValueError) as exc:
        elapsed = max(0.0, time.monotonic() - started)
        return {
            "strategy": strategy,
            "strategy_prior_score": float(strategy_prior_score),
            "passed": False,
            "changed_files": [],
            "files": [],
            "gate_count": 0,
            "elapsed_seconds": round(elapsed, 3),
            "failure": str(exc),
            **metadata,
            "candidate_score": -1_000_000.0,
        }
    finally:
        restore_workspace(root, baseline)
