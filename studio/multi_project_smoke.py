"""Sequential smoke runs proving project isolation across repeated executions."""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def main() -> int:
    base_env = dict(os.environ)
    failures = []
    with tempfile.TemporaryDirectory(prefix="studio-multi-smoke-") as td:
        root = Path(td)
        for index in range(2):
            project_root = root / f"project-{index + 1}"
            env = dict(base_env)
            env["STUDIO_SMOKE_ROOT"] = str(project_root)
            result = subprocess.run(
                [sys.executable, "studio/smoke.py"],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=25 * 60,
            )
            print(f"project-{index + 1}: exit={result.returncode}")
            print(result.stdout[-12000:])
            if result.returncode != 0:
                failures.append(index + 1)
            shutil.rmtree(project_root, ignore_errors=True)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
