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
                try:
                    result = subprocess.run(
                        [sys.executable, "studio/smoke.py"],
                        env=env,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        timeout=29 * 60,
                    )
                    output = result.stdout or ""
                    code = result.returncode
                except subprocess.TimeoutExpired as exc:
                    # Preserve a structured failure rather than aborting the
                    # whole smoke with a traceback and uncleaned Docker files.
                    output = exc.stdout or b""
                    if isinstance(output, bytes):
                        output = output.decode(errors="replace")
                    code = 124
                    output += "\nSmoke project exceeded the 29-minute process deadline"
                print(f"project-{index + 1}: exit={code} attempt={attempt + 1}")
                print(output[-12000:])
                if code == 0:
                    passed = True
                    break
                if attempt == 0 and _is_transient_android_sdk_failure(output):
                    print(f"project-{index + 1}: retrying after transient Android SDK archive corruption")
                    _clear_transient_android_download_cache(env)
                    continue
                break

            if not passed:
                failures.append(index + 1)
            # A build killed on its deadline may leave root-owned Gradle
            # files because Docker never reached the chmod exit trap.
            try:
                shutil.rmtree(project_root)
            except OSError:
                from core import Sandbox
                sandbox = Sandbox(project_root)
                permissions_env = {
                    key: base_env[key] for key in ("PATH", "HOME")
                    if key in base_env
                }
                if not sandbox._restore_host_permissions(permissions_env):
                    raise RuntimeError(
                        f"project-{index + 1}: Docker-owned workspace cleanup failed"
                    ) from None
                shutil.rmtree(project_root)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
