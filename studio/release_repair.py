"""Generic bounded source repair for release-stage code diagnostics."""
from __future__ import annotations

from pathlib import Path

from core import Model, Sandbox, StudioError, allowed, apply_patch, canonical, patch_check
from diagnostics import repairable
from journeys import validate_journeys

MAX_RELEASE_REPAIR_ROUNDS = 2


def _context(root: Path, state: dict, stage: str, blockers: list[str]) -> str:
    files = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        rel = path.relative_to(root).as_posix()
        if not allowed(rel) or rel.startswith(("test/", "docs/")):
            continue
        files[rel] = path.read_text(errors="replace")
    return canonical({
        "task": "Repair only the supplied release-stage code defects. Do not fake or bypass QA.",
        "stage": stage,
        "blockers": blockers,
        "product": state.get("product"),
        "design": state.get("design"),
        "files": files,
    })


def attempt(
    root: Path,
    state: dict,
    evidence: dict,
    stage: str,
    app_name: str,
    *,
    model_factory=Model,
    sandbox_factory=Sandbox,
) -> dict:
    blockers = repairable(stage, evidence)
    if not blockers:
        return {"attempted": False, "changed": False, "reason": "no_repairable_code_diagnostics"}

    model = model_factory(4)
    patch = model.ask("release_fix", _context(root, state, stage, blockers))
    files = patch_check(patch)
    snapshot = {}
    for item in files:
        if item["path"].startswith(("test/", "docs/")):
            raise StudioError("Release repair may not edit tests or documentation")
        path = root / item["path"]
        snapshot[item["path"]] = path.read_bytes() if path.is_file() else None

    apply_patch(root, patch)

    try:
        journeys = validate_journeys(state.get("product", {}).get("journeys"))
        sandbox = sandbox_factory(root)
        passed, logs = sandbox.gates(app_name, journeys)
    except BaseException:
        _restore(root, snapshot)
        raise

    if not passed:
        _restore(root, snapshot)
        raise StudioError(
            "Release repair failed trusted Flutter gates: " + canonical(logs[-1:])[-4000:]
        )

    return {
        "attempted": True,
        "changed": True,
        "blockers": blockers,
        "model_calls": model.calls,
        "models_used": getattr(model, "models_used", {}),
        "providers_used": getattr(model, "providers_used", {}),
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
