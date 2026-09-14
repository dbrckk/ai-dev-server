"""Generic bounded source repair for release-stage code diagnostics."""
from __future__ import annotations

from pathlib import Path
import os
import time

from core import Model, Sandbox, StudioError, SECRET, allowed, apply_patch, canonical, patch_check
from diagnostics import repairable
from journeys import validate_journeys
from agents.orchestrator import execute_named as execute_named_agent, ranked_agent_names
from flutter_workspace import snapshot as snapshot_agent_workspace, restore as restore_agent_workspace, delta as validate_agent_delta
from repair_strategy import choose as choose_strategy, record_outcome as record_strategy_outcome
from release_candidate_search import MAX_CANDIDATES, apply_winner, run_branch, select_winner

MAX_RELEASE_REPAIR_ROUNDS = 2
MAX_MODEL_CALLS_PER_BRANCH = 2


def _context(root: Path, state: dict, stage: str, blockers: list[str], failure: str | None = None) -> str:
    files = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        rel = path.relative_to(root).as_posix()
        if not allowed(rel) or rel.startswith(("test/", "docs/")):
            continue
        text = path.read_text(errors="replace")
        if SECRET.search(text):
            raise StudioError("Release repair context contains credential material")
        files[rel] = text
    return canonical({
        "task": "Repair only the supplied release-stage code defects. Do not fake or bypass QA.",
        "stage": stage,
        "blockers": blockers,
        "product": state.get("product"),
        "design": state.get("design"),
        "files": files,
        "trusted_gate_failure": failure,
    })


def _agent_memory_path() -> Path:
    raw = os.environ.get("STUDIO_AGENT_PERFORMANCE_PATH", "")
    return Path(raw) if raw else Path("/tmp/studio-agent-performance.json")


def _agent_candidates() -> list[str]:
    try:
        return ranked_agent_names(
            {"code_editing", "repo_analysis"},
            role="release_fix",
            memory_path=_agent_memory_path(),
            limit=1,
        )
    except (OSError, ValueError, RuntimeError):
        return []


def _validate_agent_scope(root: Path, before: dict[str, str]) -> dict:
    delta = validate_agent_delta(root, before)
    for item in delta.get("files", []):
        rel = item["path"]
        if not allowed(rel) or rel.startswith(("test/", "docs/")):
            restore_agent_workspace(root, before)
            raise StudioError("Release repair agent edited forbidden path: " + rel)
    if not delta.get("changed"):
        restore_agent_workspace(root, before)
        raise StudioError("Release repair agent produced no allowed source change")
    return delta


def _run_agent(root: Path, blockers: list[str], stage: str, failure: str | None = None) -> dict:
    names = _agent_candidates()
    if not names:
        raise StudioError("No eligible repair agent is available")
    before = snapshot_agent_workspace(root)
    prompt = (
        "Repair only the listed Flutter release defect(s). Preserve behavior and tests. "
        "Do not modify tests, docs, native platform files, CI, credentials, or generated files. "
        "Do not commit, push, publish, deploy, or ask questions. "
        "Stage, blockers, and trusted gate failure: "
        + canonical({"stage": stage, "blockers": blockers, "failure": failure})
    )
    result = execute_named_agent(names[0], prompt, cwd=root, timeout=900)
    if result.get("status") != "passed":
        restore_agent_workspace(root, before)
        raise StudioError("Release repair agent failed")
    delta = _validate_agent_scope(root, before)
    return {
        "agent": result.get("selected"),
        "attempts": result.get("attempts", []),
        "changed": delta.get("changed", []),
    }


def _strategy_prior(selection: dict, strategy: str) -> float:
    for row in selection.get("candidate_ranking", []):
        if row.get("strategy") == strategy:
            return float(row.get("score", 0.0))
    return 0.0


def _model_mutation(root: Path, state: dict, stage: str, blockers: list[str], task: dict | None, model_factory, failure: str | None = None):
    model = model_factory(4)
    if task and task.get("rotate_strategy") is True:
        last_provider = task.get("last_provider")
        if isinstance(last_provider, str) and last_provider and hasattr(model, "avoid_providers"):
            model.avoid_providers.add(last_provider)
    patch = model.ask("release_fix", _context(root, state, stage, blockers, failure))
    files = patch_check(patch)
    for item in files:
        if item["path"].startswith(("test/", "docs/")):
            raise StudioError("Release repair may not edit tests or documentation")
    apply_patch(root, patch)
    return {
        "model_calls": model.calls,
        "models_used": getattr(model, "models_used", {}),
        "providers_used": getattr(model, "providers_used", {}),
        "agent": None,
    }


def _agent_mutation(root: Path, blockers: list[str], stage: str, failure: str | None = None):
    evidence = _run_agent(root, blockers, stage, failure)
    return {
        "model_calls": 0,
        "models_used": {},
        "providers_used": {},
        "agent": evidence,
    }


def _hybrid_mutation(root: Path, state: dict, stage: str, blockers: list[str], task: dict | None, model_factory):
    metadata = _model_mutation(root, state, stage, blockers, task, model_factory)
    metadata["agent"] = _run_agent(root, blockers, stage)
    return metadata


def _agent_to_model_mutation(root: Path, state: dict, stage: str, blockers: list[str], task: dict | None, model_factory):
    metadata = _agent_mutation(root, blockers, stage)
    model_meta = _model_mutation(root, state, stage, blockers, task, model_factory)
    metadata["model_calls"] += model_meta.get("model_calls", 0)
    metadata["models_used"].update(model_meta.get("models_used", {}))
    metadata["providers_used"].update(model_meta.get("providers_used", {}))
    return metadata


def attempt(
    root: Path,
    state: dict,
    evidence: dict,
    stage: str,
    app_name: str,
    task: dict | None = None,
    *,
    model_factory=Model,
    sandbox_factory=Sandbox,
) -> dict:
    blockers = repairable(stage, evidence)
    if not blockers:
        return {"attempted": False, "changed": False, "reason": "no_repairable_code_diagnostics"}

    agents = _agent_candidates()
    selection = choose_strategy(task, stage=stage, agent_available=bool(agents))
    preferred = selection["strategy"]

    strategies = [preferred]
    if len(strategies) < MAX_CANDIDATES:
        for row in selection.get("candidate_ranking", []):
            name = row.get("strategy")
            if name in {"model_only", "agent_only", "model_to_agent", "agent_to_model"} and name not in strategies:
                if name == "agent_only" and not agents:
                    continue
                if name in {"model_to_agent", "agent_to_model"} and not agents:
                    continue
                strategies.append(name)
                if len(strategies) >= MAX_CANDIDATES:
                    break

    candidates = []
    for strategy_name in strategies:
        prior = _strategy_prior(selection, strategy_name)

        if strategy_name == "model_only":
            steps = [
                lambda s=state, st=stage, b=blockers, t=task:
                    _model_mutation(root, s, st, b, t, model_factory)
            ]
            refine = lambda failure, s=state, st=stage, b=blockers, t=task: (
                _model_mutation(root, s, st, b, t, model_factory, failure)
            )
        elif strategy_name == "agent_only":
            steps = [
                lambda st=stage, b=blockers:
                    _agent_mutation(root, b, st)
            ]
            refine = lambda failure, st=stage, b=blockers: (
                _agent_mutation(root, b, st, failure)
            )
        elif strategy_name == "agent_to_model":
            steps = [
                lambda st=stage, b=blockers:
                    _agent_mutation(root, b, st),
                lambda s=state, st=stage, b=blockers, t=task:
                    _model_mutation(root, s, st, b, t, model_factory),
            ]
            refine = lambda failure, s=state, st=stage, b=blockers, t=task: (
                _model_mutation(root, s, st, b, t, model_factory, failure)
            )
        else:
            steps = [
                lambda s=state, st=stage, b=blockers, t=task:
                    _model_mutation(root, s, st, b, t, model_factory),
                lambda st=stage, b=blockers:
                    _agent_mutation(root, b, st),
            ]
            refine = lambda failure, s=state, st=stage, b=blockers, t=task: (
                _model_mutation(root, s, st, b, t, model_factory, failure)
            )

        candidate = run_branch(
            root,
            strategy=strategy_name,
            strategy_prior_score=prior,
            steps=steps,
            refine=refine,
            state=state,
            app_name=app_name,
            sandbox_factory=sandbox_factory,
        )
        candidates.append(candidate)
        record_strategy_outcome(
            strategy_name,
            stage=stage,
            success=candidate.get("passed") is True,
            cost_seconds=float(candidate.get("elapsed_seconds", 0.0)),
        )

    winner = select_winner(candidates)
    if winner is None:
        raise StudioError(
            "No isolated release repair candidate passed trusted gates: "
            + canonical([
                {
                    "strategy": item.get("strategy"),
                    "failure": item.get("failure"),
                }
                for item in candidates
            ])[-4000:]
        )

    apply_winner(root, winner)
    return {
        "attempted": True,
        "changed": True,
        "changed_files": winner.get("changed_files", []),
        "blockers": blockers,
        "model_calls": sum(max(0, int(item.get("model_calls", 0))) for item in candidates),
        "models_used": winner.get("models_used", {}),
        "providers_used": winner.get("providers_used", {}),
        "agent": winner.get("agent"),
        "strategy": winner.get("strategy"),
        "strategy_selection": selection,
        "strategy_cost_seconds": round(sum(float(item.get("elapsed_seconds", 0.0)) for item in candidates), 3),
        "candidate_search": {
            "evaluated": len(candidates),
            "winner": winner.get("strategy"),
            "candidates": [
                {
                    "strategy": item.get("strategy"),
                    "passed": item.get("passed"),
                    "candidate_score": item.get("candidate_score"),
                    "changed_files": item.get("changed_files", []),
                    "model_calls": item.get("model_calls", 0),
                    "gate_count": item.get("gate_count", 0),
                    "elapsed_seconds": item.get("elapsed_seconds", 0.0),
                    "failure": item.get("failure"),
                }
                for item in candidates
            ],
        },
        "gate_count": winner.get("gate_count", 0),
    }

def _restore(root: Path, snapshot: dict[str, bytes | None]) -> None:
    for rel, original in snapshot.items():
        path = root / rel
        if original is None:
            path.unlink(missing_ok=True)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(original)
