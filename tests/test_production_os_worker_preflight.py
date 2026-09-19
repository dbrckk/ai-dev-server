from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import importlib.util

SPEC = importlib.util.spec_from_file_location(
    "production_os_preflight",
    SCRIPTS / "preflight-production-os-worker.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class ProductionOSWorkerPreflightTests(unittest.TestCase):
    def base_env(self, output_root):
        return {
            "PRODUCTION_OS_URL": "https://production.example",
            "PRODUCTION_OS_WORKER_TOKEN": "worker-secret",
            "PRODUCTION_OS_OPERATOR_TOKEN": "operator-secret",
            "PRODUCTION_OS_OUTPUT_ROOT": str(output_root),
            "PRODUCTION_OS_POLL_INTERVAL": "10",
        }

    def test_ready_configuration_passes(self):
        with tempfile.TemporaryDirectory() as td, patch.object(
            MODULE,
            "_codex_version",
            return_value=(True, "codex-cli 1.2.3"),
        ):
            code, lines = MODULE.run_preflight(self.base_env(Path(td) / "out"))

        self.assertEqual(code, 0)
        self.assertIn(
            "READY: Production-OS worker preflight passed",
            lines,
        )

    def test_visual_assets_are_non_blocking_when_pollinations_is_unavailable(self):
        with tempfile.TemporaryDirectory() as td, patch.object(
            MODULE,
            "_codex_version",
            return_value=(True, "codex-cli 1.2.3"),
        ), patch.object(
            MODULE,
            "_pollinations_status",
            return_value=(False, "polli CLI not installed"),
        ):
            code, lines = MODULE.run_preflight(self.base_env(Path(td) / "out"))

        self.assertEqual(code, 0)
        self.assertTrue(any("INFO visual assets: disabled" in line for line in lines))

    def test_visual_assets_are_reported_ready_when_pollinations_is_ready(self):
        with tempfile.TemporaryDirectory() as td, patch.object(
            MODULE,
            "_codex_version",
            return_value=(True, "codex-cli 1.2.3"),
        ), patch.object(
            MODULE,
            "_pollinations_status",
            return_value=(True, "polli installed and authenticated"),
        ):
            code, lines = MODULE.run_preflight(self.base_env(Path(td) / "out"))

        self.assertEqual(code, 0)
        self.assertTrue(any("OK visual assets:" in line for line in lines))

    def test_visual_probe_uses_asset_forge_operational_status(self):
        class Result:
            returncode = 0
            stdout = (
                '{"ready":{"anyGeneratedAsset":true},'
                '"capabilities":{"rasterPng":true,"rasterWebp":false,'
                '"vectorSvg":true,"threeDGlb":false,"godotImport":false},'
                '"blockers":[]}'
            )
            stderr = ""

        with patch.object(MODULE.shutil, "which", return_value="/usr/bin/asset-forge"), \
             patch.object(MODULE.subprocess, "run", return_value=Result()) as run:
            ready, detail = MODULE._pollinations_status(
                {"PATH": "/usr/bin", "POLLINATIONS_API_KEY": "secret"}
            )

        self.assertTrue(ready)
        self.assertIn("rasterPng", detail)
        self.assertIn("vectorSvg", detail)
        self.assertNotIn("secret", detail)
        self.assertEqual(
            run.call_args.args[0],
            ["/usr/bin/asset-forge", "operational-status"],
        )

    def test_missing_required_secret_fails_without_echoing_secret_values(self):
        with tempfile.TemporaryDirectory() as td, patch.object(
            MODULE,
            "_codex_version",
            return_value=(True, "codex-cli 1.2.3"),
        ):
            env = self.base_env(Path(td) / "out")
            env.pop("PRODUCTION_OS_WORKER_TOKEN")
            code, lines = MODULE.run_preflight(env)

        rendered = "\n".join(lines)
        self.assertEqual(code, 2)
        self.assertIn("PRODUCTION_OS_WORKER_TOKEN", rendered)
        self.assertNotIn("operator-secret", rendered)

    def test_remote_http_control_plane_is_rejected(self):
        with tempfile.TemporaryDirectory() as td, patch.object(
            MODULE,
            "_codex_version",
            return_value=(True, "codex-cli 1.2.3"),
        ):
            env = self.base_env(Path(td) / "out")
            env["PRODUCTION_OS_URL"] = "http://production.example"
            code, lines = MODULE.run_preflight(env)

        self.assertEqual(code, 2)
        self.assertTrue(
            any("HTTPS required" in line for line in lines)
        )

    def test_loopback_http_is_allowed(self):
        with tempfile.TemporaryDirectory() as td, patch.object(
            MODULE,
            "_codex_version",
            return_value=(True, "codex-cli 1.2.3"),
        ):
            env = self.base_env(Path(td) / "out")
            env["PRODUCTION_OS_URL"] = "http://127.0.0.1:8787"
            code, _ = MODULE.run_preflight(env)

        self.assertEqual(code, 0)

    def test_partial_omniroute_configuration_fails(self):
        with tempfile.TemporaryDirectory() as td, patch.object(
            MODULE,
            "_codex_version",
            return_value=(True, "codex-cli 1.2.3"),
        ):
            env = self.base_env(Path(td) / "out")
            env["OMNIROUTE_URL"] = "https://omniroute.example"
            code, lines = MODULE.run_preflight(env)

        self.assertEqual(code, 2)
        self.assertTrue(
            any("must be set together" in line for line in lines)
        )

    def test_non_positive_poll_interval_fails(self):
        with tempfile.TemporaryDirectory() as td, patch.object(
            MODULE,
            "_codex_version",
            return_value=(True, "codex-cli 1.2.3"),
        ):
            env = self.base_env(Path(td) / "out")
            env["PRODUCTION_OS_POLL_INTERVAL"] = "0"
            code, lines = MODULE.run_preflight(env)

        self.assertEqual(code, 2)
        self.assertTrue(
            any("positive number" in line for line in lines)
        )


if __name__ == "__main__":
    unittest.main()
