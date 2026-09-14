"""Bounded model-assisted remediation for technical security findings."""
from __future__ import annotations

import json
from pathlib import Path

from core import Model, Sandbox, StudioError, allowed, apply_patch, canonical
from journeys import validate_journeys

MAX_AGENTIC_ROUNDS = 2
AGENTIC_BLOCKERS = {
    "cleartext_network_traffic_detected",
    "runtime_process_execution_detected",
}


def eligible_blockers(evidence: dict) -> list[str]:
    return sorted(set(evidence.get("blockers", [])) & AGENTIC_BLOCKERS)


def _context(root: Path, state: dict, blockers: list[str]) -> str:
    files = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        rel = path.relative_to(root).as_posix()
        if not allowed(rel):
            continue
        text = path.read_text(errors="replace")
        # Secret-bearing files are intentionally withheld from external models.
        if "credential_material_detected" in state.get("release_evidence", {}).get("security_scan", {}).get("blockers", []):
            continue
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
    *,
    model_factory=Model,
    sandbox_factory=Sandbox,
) -> dict:
    blockers = eligible_blockers(state.get("release_evidence", {}).get("security_scan", {}))
    if not blockers:
        return {"attempted": False, "changed": False, "reason": "no_eligible_blockers"}

    model = model_factory(4)
    patch = model.ask("security_fix", _context(root, state, blockers))
    apply_patch(root, patch)

    journeys = validate_journeys(state.get("product", {}).get("journeys"))
    sandbox = sandbox_factory(root)
    passed, logs = sandbox.gates(
        state.get("app_name") or state.get("request", {}).get("app_name") or "studio_app",
        journeys,
    )
    if not passed:
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
