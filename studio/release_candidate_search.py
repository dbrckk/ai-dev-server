"""Isolated candidate search for release repair strategies."""
from __future__ import annotations

from pathlib import Path
import time

from flutter_workspace import snapshot as snapshot_workspace, restore as restore_workspace, delta as validate_delta
from core import StudioError, apply_patch, canonical
from journeys import validate_journeys
from repair_search_policy import should_continue_after_quick_failure, should_refine
from diff_quick_gates import plan as plan_quick_gates
from quick_gate_cache import cache_key, delta_hash, get as cache_get, put as cache_put, workspace_hash
from full_gate_cache import hit as full_cache_hit, record_success as full_cache_record_success, validation_key as full_validation_key
from immutable_artifact_cache import capture as capture_artifacts, restore as restore_artifacts, touch as touch_artifact_cache

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

        def validate_full_state():
            key = full_validation_key(root, app_name=app_name, journeys=journeys)
            restored = None
            restore_error = None
            cached = False
            if (
                artifact_cache_enabled
                and full_cache_hit(full_gate_cache, key)
                and key in artifact_cache
            ):
                try:
                    restored = restore_artifacts(
                        root,
                        artifact_cache[key],
                        key,
                    )
                except StudioError as exc:
                    restore_error = str(exc)
                    artifact_cache.pop(key, None)
                    full_gate_cache.pop(key, None)
                else:
                    touch_artifact_cache(artifact_cache, key)
                    return (
                        True,
                        [{
                            "command": ["cached-full-candidate-validation"],
                            "exit_code": 0,
                            "output": key,
                        }],
                        True,
                        restored,
                        restore_error,
                        key,
                    )

            sandbox = sandbox_factory(root)
            gate_passed, gate_logs = sandbox.gates(app_name, journeys)
            if gate_passed:
                full_cache_record_success(full_gate_cache, key)
                if artifact_cache_enabled:
                    artifact_cache[key] = capture_artifacts(root, key)
            return (
                gate_passed,
                gate_logs,
                cached,
                restored,
                restore_error,
                key,
            )

        (
            passed,
            logs,
            cached_full_validation,
            artifact_restore,
            cache_restore_error,
            full_key,
        ) = validate_full_state()
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
            (
                passed,
                logs,
                cached_full_validation,
                artifact_restore,
                cache_restore_error,
                full_key,
            ) = validate_full_state()

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
            "cached_full_validation": cached_full_validation,
            "full_validation_key": full_key,
            "artifact_restore": artifact_restore,
            "artifact_cache_restore_error": cache_restore_error,
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
