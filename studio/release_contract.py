"""Validate VERSION, release manifest and required workflow contracts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

WORKFLOW_NAMES = {
    "CI": ".github/workflows/ci.yml",
    "Validate AI Dev Server": ".github/workflows/validate.yml",
    "Fault Injection Gate": ".github/workflows/fault-injection.yml",
    "Resilience Soak": ".github/workflows/resilience-soak.yml",
    "Mobile Studio Real Build": ".github/workflows/mobile-real-build.yml",
    "Multi-Engine E2E Benchmark": ".github/workflows/multi-engine-benchmark.yml",
}


def validate(root: Path | str = ".") -> dict:
    root = Path(root)
    failures = []

    version_path = root / "VERSION"
    manifest_path = root / "control/release.json"

    try:
        version = version_path.read_text(encoding="utf-8").strip()
    except OSError:
        version = ""
        failures.append("version_missing")

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        manifest = {}
        failures.append("release_manifest_invalid")

    if not isinstance(manifest, dict):
        manifest = {}
        failures.append("release_manifest_not_object")

    if version and manifest.get("version") != version:
        failures.append("version_mismatch")

    gates = manifest.get("required_gates")
    if not isinstance(gates, list):
        gates = []
        failures.append("required_gates_invalid")

    missing_expected = sorted(set(WORKFLOW_NAMES) - set(gates))
    if missing_expected:
        failures.append("required_gates_missing:" + ",".join(missing_expected))

    unknown = sorted(set(gates) - set(WORKFLOW_NAMES))
    if unknown:
        failures.append("required_gates_unknown:" + ",".join(unknown))

    workflow_files = {}
    for gate, rel in WORKFLOW_NAMES.items():
        path = root / rel
        exists = path.is_file()
        workflow_files[gate] = {"path": rel, "exists": exists}
        if gate in gates and not exists:
            failures.append("workflow_missing:" + gate)

    commands = manifest.get("operational_commands")
    if not isinstance(commands, list) or not commands:
        failures.append("operational_commands_missing")

    safety = manifest.get("safety")
    if version.startswith("1.2") and not isinstance(safety, dict):
        failures.append("v1_2_safety_contract_missing")

    return {
        "valid": not failures,
        "version": version or None,
        "channel": manifest.get("channel"),
        "required_gates": gates,
        "workflows": workflow_files,
        "failures": failures,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Validate AI Dev Server release contract")
    parser.add_argument("--root", default=".")
    args = parser.parse_args(argv)
    report = validate(args.root)
    print(json.dumps(report, sort_keys=True))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
