"""Machine-readable V1 release-candidate assessment for one project output."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from durable_state import load_recovering
from telemetry import summarize


def assess(project_out: Path) -> dict:
    project_out = Path(project_out)
    failures = []
    evidence = {}

    report_path = project_out / "report.json"
    if not report_path.is_file():
        failures.append("report_missing")
        report = {}
    else:
        try:
            report = json.loads(report_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            report = {}
            failures.append("report_invalid")

    completion = report.get("completion") if isinstance(report, dict) else None
    evidence["completion_finished"] = (
        isinstance(completion, dict) and completion.get("finished") is True
    )
    if not evidence["completion_finished"]:
        failures.append("completion_not_finished")

    evidence["store_ready"] = report.get("release_status") == "store_ready"
    if not evidence["store_ready"]:
        failures.append("release_not_store_ready")

    autonomy = project_out / ".autonomy"
    runtime_path = autonomy / "runtime-state.json"
    try:
        runtime = load_recovering(runtime_path)
    except Exception:
        runtime = {}
        failures.append("runtime_state_unavailable")
    evidence["runtime_status"] = runtime.get("status")

    telemetry_summary = summarize(autonomy / "telemetry.jsonl")
    evidence["telemetry"] = telemetry_summary

    checkpoint = autonomy / "workflow-checkpoints.json"
    evidence["workflow_checkpoint_present"] = checkpoint.is_file()
    if not evidence["workflow_checkpoint_present"]:
        failures.append("workflow_checkpoint_missing")

    artifact_cas = autonomy / "artifact-cas"
    evidence["artifact_cas_present"] = artifact_cas.exists()

    return {
        "ready": not failures,
        "failures": sorted(set(failures)),
        "evidence": evidence,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project_out")
    args = parser.parse_args()
    result = assess(Path(args.project_out))
    print(json.dumps(result, sort_keys=True))
    return 0 if result["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
