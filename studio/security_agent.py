"""Bounded model-assisted remediation for technical security findings."""
from __future__ import annotations

import json
from pathlib import Path

from core import Model, Sandbox, StudioError, allowed, apply_patch, canonical, patch_check
from journeys import validate_journeys

MAX_AGENTIC_ROUNDS = 2
AGENTIC_BLOCKERS = {
    "cleartext_network_traffic_detected",
    "runtime_process_execution_detected",
}


def eligible_blockers(evidence: dict) -> list[str]:
    blockers = set(evidence.get("blockers", []))
    if "credential_material_detected" in blockers:
        return []
    return sorted(blockers & AGENTIC_BLOCKERS)


def _context(root: Path, state: dict, blockers: list[str]) -> str:
    files = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        rel = path.relative_to(root).as_posix()
        if not allowed(rel):
            continue
        text = path.read_text(errors="replace")
        files[rel] = text
    return canonical({
        "task": "Repair only the listed technical security findings without weakening behavior or tests.",
        "blockers": blockers,
        "product": state.get("product"),
        "design": state.get("design"),
        "files": files,
    })


def attempt(
    root: Path,
    state: dict,
    evidence: dict,
    app_name: str,
    *,
    model_factory=Model,
    sandbox_factory=Sandbox,
) -> dict:
    blockers = eligible_blockers(evidence)
    if not blockers:
        return {"attempted": False, "changed": False, "reason": "no_eligible_blockers"}

    model = model_factory(4)
    patch = model.ask("security_fix", _context(root, state, blockers))
    files = patch_check(patch)
    snapshot = {}
    for item in files:
        path = root / item["path"]
        snapshot[item["path"]] = path.read_bytes() if path.is_file() else None

    apply_patch(root, patch)

    journeys = validate_journeys(state.get("product", {}).get("journeys"))
    sandbox = sandbox_factory(root)
    passed, logs = sandbox.gates(
        app_name,
        journeys,
    )
    if not passed:
        for rel, original in snapshot.items():
            path = root / rel
            if original is None:
                path.unlink(missing_ok=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(original)
        raise StudioError("Security repair failed trusted Flutter gates: " + canonical(logs[-1:])[-4000:])

    return {
        "attempted": True,
        "changed": True,
        "blockers": blockers,
        "model_calls": model.calls,
        "models_used": getattr(model, "models_used", {}),
        "providers_used": getattr(model, "providers_used", {}),
        "gate_count": len(logs),
    }
