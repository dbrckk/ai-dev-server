"""Machine-readable health report for one persistent autonomous project."""
from __future__ import annotations

import json
from pathlib import Path

from durable_state import load_recovering
from telemetry import summarize as telemetry_summary
from workflow_checkpoint import load_path as load_checkpoints


def _lease_summary(path: Path) -> dict:
    if not path.is_file():
        return {"claims": 0, "valid": True}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {"claims": None, "valid": False}
    if not isinstance(data, dict):
        return {"claims": None, "valid": False}
    claims = data.get("claims")
    if data.get("schema") != 1 or not isinstance(claims, dict):
        return {"claims": None, "valid": False}
    return {"claims": len(claims), "valid": True}


def inspect(project_out: Path | str) -> dict:
    project_out = Path(project_out)
    root = project_out / ".autonomy"

    paths = {
        "runtime_state": root / "runtime-state.json",
        "checkpoints": root / "workflow-checkpoints.json",
        "telemetry": root / "telemetry.jsonl",
        "leases": root / "task-leases.json",
        "quick_gate_cache": root / "quick-gate-cache.json",
        "full_gate_cache": root / "full-gate-cache.json",
        "artifact_cache": root / "artifact-cache.json",
        "artifact_cas": root / "artifact-cas",
    }

    errors = []
    runtime = {}
    if paths["runtime_state"].is_file():
        try:
            runtime = load_recovering(paths["runtime_state"])
        except Exception as exc:
            errors.append("runtime_state:" + type(exc).__name__)
    else:
        errors.append("runtime_state:missing")

    try:
        checkpoints = load_checkpoints(paths["checkpoints"])
    except Exception as exc:
        checkpoints = {}
        errors.append("checkpoints:" + type(exc).__name__)

    leases = _lease_summary(paths["leases"])
    if not leases["valid"]:
        errors.append("leases:invalid")

    telemetry = telemetry_summary(paths["telemetry"])
    if telemetry["events"] == 0:
        errors.append("telemetry:empty")

    status = "healthy" if not errors else "degraded"
    return {
        "status": status,
        "runtime_status": runtime.get("status"),
        "goal_id": runtime.get("goal_id"),
        "attempt": runtime.get("attempt"),
        "checkpoint_entries": len(checkpoints),
        "leases": leases,
        "telemetry": telemetry,
        "paths": {name: str(path) for name, path in paths.items()},
        "errors": errors,
    }
