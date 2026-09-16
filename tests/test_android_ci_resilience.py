import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from studio import multi_project_smoke


ROOT = Path(__file__).resolve().parents[1]


class AndroidCIResilienceTests(unittest.TestCase):
    def test_transient_android_archive_failures_are_recognized_conservatively(self):
        self.assertTrue(
            multi_project_smoke._is_transient_android_sdk_failure(
                "java.util.zip.ZipException: Archive is not a ZIP archive\n"
                "Install NDK (Side by side) failed"
            )
        )
        self.assertTrue(
            multi_project_smoke._is_transient_android_sdk_failure(
                "Warning: Android Emulator: Error on ZipFile unknown archive."
            )
        )
        self.assertFalse(
            multi_project_smoke._is_transient_android_sdk_failure(
                "Expected widget Settings but found none\nflutter test failed"
            )
        )

    def test_android_bootstrap_retries_sdkmanager_then_succeeds(self):
        script = ROOT / "scripts" / "bootstrap-android-ci.sh"
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            sdk = root / "cmdline-tools" / "latest" / "bin" / "sdkmanager"
            sdk.parent.mkdir(parents=True)
            counter = root / "install-attempts"
            sdk.write_text(
                "#!/usr/bin/env bash\n"
                "set -eu\n"
                "if [[ ${1:-} == --licenses ]]; then exit 0; fi\n"
                f"counter={counter!s}\n"
                "n=0; [[ -f \"$counter\" ]] && n=$(cat \"$counter\")\n"
                "n=$((n+1)); printf '%s' \"$n\" > \"$counter\"\n"
                "if [[ $n -eq 1 ]]; then echo 'ZipFile unknown archive' >&2; exit 1; fi\n"
                "exit 0\n",
                encoding="utf-8",
            )
            sdk.chmod(0o755)
            env = dict(os.environ)
            env["ANDROID_HOME"] = str(root)
            env["GITHUB_PATH"] = str(root / "github-path")
            result = subprocess.run(
                ["bash", str(script)],
                cwd=ROOT,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertEqual(counter.read_text(encoding="utf-8"), "2")

    def test_android_bootstrap_fails_after_three_install_attempts(self):
        script = ROOT / "scripts" / "bootstrap-android-ci.sh"
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            sdk = root / "cmdline-tools" / "latest" / "bin" / "sdkmanager"
            sdk.parent.mkdir(parents=True)
            counter = root / "install-attempts"
            sdk.write_text(
                "#!/usr/bin/env bash\n"
                "set -eu\n"
                "if [[ ${1:-} == --licenses ]]; then exit 0; fi\n"
                f"counter={counter!s}\n"
                "n=0; [[ -f \"$counter\" ]] && n=$(cat \"$counter\")\n"
                "n=$((n+1)); printf '%s' \"$n\" > \"$counter\"\n"
                "echo 'Archive is not a ZIP archive' >&2\n"
                "exit 1\n",
                encoding="utf-8",
            )
            sdk.chmod(0o755)
            env = dict(os.environ)
            env["ANDROID_HOME"] = str(root)
            env["GITHUB_PATH"] = str(root / "github-path")
            result = subprocess.run(
                ["bash", str(script)],
                cwd=ROOT,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(counter.read_text(encoding="utf-8"), "3")

    def test_all_android_workflows_use_shared_resilient_bootstrap(self):
        for rel in (
            ".github/workflows/studio-smoke.yml",
            ".github/workflows/multi-engine-benchmark.yml",
            ".github/workflows/mobile-studio.yml",
        ):
            text = (ROOT / rel).read_text(encoding="utf-8")
            self.assertIn("bash scripts/bootstrap-android-ci.sh", text, rel)


if __name__ == "__main__":
    unittest.main()
