"""Production-readiness gate for AI Dev Server runtime prerequisites."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import sys

from provider_router import load_providers
from queue import matrix


REQUIRED_STATE_ENV = (
    "STUDIO_QUICK_GATE_CACHE_PATH",
    "STUDIO_FULL_GATE_CACHE_PATH",
    "STUDIO_ARTIFACT_CACHE_PATH",
    "STUDIO_ARTIFACT_CAS_PATH",
    "STUDIO_CHECKPOINT_PATH",
)


def check(root: Path | str = ".") -> dict:
    root = Path(root).resolve()
    checks = {}

    checks["python_3_12_plus"] = sys.version_info >= (3, 12)
    checks["docker_available"] = shutil.which("docker") is not None
    checks["control_config_present"] = (root / "control/ci.json").is_file()
    checks["request_directory_present"] = (root / "control/mobile-requests").is_dir()

    try:
        ci_config = json.loads((root / "control/ci.json").read_text(encoding="utf-8"))
        checks["ci_provider_valid"] = (
            isinstance(ci_config, dict)
            and ci_config.get("provider") in {"github", "circleci"}
        )
    except (OSError, UnicodeError, json.JSONDecodeError):
        checks["ci_provider_valid"] = False

    try:
        matrix(root / "control/mobile-requests")
    except Exception:
        checks["request_queue_valid"] = False
    else:
        checks["request_queue_valid"] = True

    try:
        providers = load_providers(prefer_free=True)
    except ValueError:
        providers = ()
    checks["model_provider_configured"] = bool(providers)

    for name in REQUIRED_STATE_ENV:
        checks["env_" + name.lower()] = bool(os.environ.get(name, "").strip())

    required = list(checks)
    passed = all(checks[name] for name in required)
    return {
        "ready": passed,
        "checks": checks,
        "failed": [name for name in required if not checks[name]],
    }


if __name__ == "__main__":
    report = check()
    print(json.dumps(report, sort_keys=True))
    raise SystemExit(0 if report["ready"] else 1)
