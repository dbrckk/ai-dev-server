"""Sequential smoke runs proving project isolation across repeated executions."""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


_TRANSIENT_ANDROID_SDK_SIGNATURES = (
    "Archive is not a ZIP archive",
    "ZipFile unknown archive",
)


def _is_transient_android_sdk_failure(output: object) -> bool:
    text = str(output or "")
    return any(signature in text for signature in _TRANSIENT_ANDROID_SDK_SIGNATURES)


def _clear_transient_android_download_cache(env: dict[str, str]) -> None:
    android_home = env.get("ANDROID_HOME")
    if android_home:
        root = Path(android_home)
        shutil.rmtree(root / ".temp", ignore_errors=True)
        shutil.rmtree(root / ".cache", ignore_errors=True)
    android_user_home = env.get("ANDROID_USER_HOME")
    if android_user_home:
        shutil.rmtree(Path(android_user_home) / "cache", ignore_errors=True)
    elif env.get("HOME"):
        shutil.rmtree(Path(env["HOME"]) / ".android" / "cache", ignore_errors=True)


def main() -> int:
    base_env = dict(os.environ)
    failures = []
    with tempfile.TemporaryDirectory(prefix="studio-multi-smoke-") as td:
        root = Path(td)
        for index in range(2):
            project_root = root / f"project-{index + 1}"
            env = dict(base_env)
            env["STUDIO_SMOKE_ROOT"] = str(project_root)

            passed = False
            for attempt in range(2):
                if attempt:
                    shutil.rmtree(project_root, ignore_errors=True)
                result = subprocess.run(
                    [sys.executable, "studio/smoke.py"],
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    timeout=25 * 60,
                )
                print(f"project-{index + 1}: exit={result.returncode} attempt={attempt + 1}")
                print(result.stdout[-12000:])
                if result.returncode == 0:
                    passed = True
                    break
                if attempt == 0 and _is_transient_android_sdk_failure(result.stdout):
                    print(f"project-{index + 1}: retrying after transient Android SDK archive corruption")
                    _clear_transient_android_download_cache(env)
                    continue
                break

            if not passed:
                failures.append(index + 1)
            shutil.rmtree(project_root, ignore_errors=True)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
