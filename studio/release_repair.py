"""Generic bounded source repair for release-stage code diagnostics."""
from __future__ import annotations

from pathlib import Path
import os
import time

from core import Model, Sandbox, StudioError, SECRET, allowed, apply_patch, canonical, patch_check
from diagnostics import repairable
from journeys import validate_journeys
from agents.orchestrator import execute_named as execute_named_agent, ranked_agent_names
from agents.workspace import snapshot as snapshot_agent_workspace, restore as restore_agent_workspace, validate_delta as validate_agent_delta
from repair_strategy import choose as choose_strategy, record_outcome as record_strategy_outcome

MAX_RELEASE_REPAIR_ROUNDS = 2


def _context(root: Path, state: dict, stage: str, blockers: list[str]) -> str:
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


def _run_agent(root: Path, blockers: list[str], stage: str) -> dict:
    names = _agent_candidates()
    if not names:
        raise StudioError("No eligible repair agent is available")
    before = snapshot_agent_workspace(root)
    prompt = (
        "Repair only the listed Flutter release defect(s). Preserve behavior and tests. "
        "Do not modify tests, docs, native platform files, CI, credentials, or generated files. "
        "Do not commit, push, publish, deploy, or ask questions. "
        "Stage and blockers: " + canonical({"stage": stage, "blockers": blockers})
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
    strategy = choose_strategy(task, stage=stage, agent_available=bool(agents))
    strategy_name = strategy["strategy"]
    started = time.monotonic()
    model = None
    model_calls = 0
    models_used = {}
    providers_used = {}
    agent_evidence = None
    before_strategy = snapshot_agent_workspace(root)

    try:
        if strategy_name in {"model_only", "model_to_agent"}:
            model = model_factory(4)
            if task and task.get("rotate_strategy") is True:
                last_provider = task.get("last_provider")
                if isinstance(last_provider, str) and last_provider and hasattr(model, "avoid_providers"):
                    model.avoid_providers.add(last_provider)
            patch = model.ask("release_fix", _context(root, state, stage, blockers))
            files = patch_check(patch)
            for item in files:
                if item["path"].startswith(("test/", "docs/")):
                    raise StudioError("Release repair may not edit tests or documentation")
            apply_patch(root, patch)
            model_calls = model.calls
            models_used = getattr(model, "models_used", {})
            providers_used = getattr(model, "providers_used", {})

        if strategy_name in {"agent_only", "model_to_agent"}:
            agent_evidence = _run_agent(root, blockers, stage)

        journeys = validate_journeys(state.get("product", {}).get("journeys"))
        sandbox = sandbox_factory(root)
        passed, logs = sandbox.gates(app_name, journeys)
        if not passed:
            raise StudioError(
                "Release repair failed trusted Flutter gates: " + canonical(logs[-1:])[-4000:]
            )
    except BaseException:
        restore_agent_workspace(root, before_strategy)
        record_strategy_outcome(
            strategy_name,
            stage=stage,
            success=False,
            cost_seconds=max(0.0, time.monotonic() - started),
        )
        raise

    changed = validate_agent_delta(root, before_strategy).get("changed", [])
    if not changed:
        restore_agent_workspace(root, before_strategy)
        record_strategy_outcome(
            strategy_name,
            success=False,
            cost_seconds=max(0.0, time.monotonic() - started),
        )
        raise StudioError("Release repair strategy produced no source delta")

    elapsed = max(0.0, time.monotonic() - started)
    record_strategy_outcome(strategy_name, success=True, cost_seconds=elapsed)
    return {
        "attempted": True,
        "changed": True,
        "changed_files": changed,
        "blockers": blockers,
        "model_calls": model_calls,
        "models_used": models_used,
        "providers_used": providers_used,
        "agent": agent_evidence,
        "strategy": strategy_name,
        "strategy_selection": strategy,
        "strategy_cost_seconds": round(elapsed, 3),
        "gate_count": len(logs),
    }

def _restore(root: Path, snapshot: dict[str, bytes | None]) -> None:
    for rel, original in snapshot.items():
        path = root / rel
        if original is None:
            path.unlink(missing_ok=True)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(original)
