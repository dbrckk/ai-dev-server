import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import readiness


class ReadinessTests(unittest.TestCase):
    def _root(self, td):
        root = Path(td)
        (root / "control/mobile-requests").mkdir(parents=True)
        (root / "control/ci.json").write_text('{"provider":"github"}', encoding="utf-8")
        return root

    def test_missing_runtime_state_paths_prevent_readiness(self):
        with tempfile.TemporaryDirectory() as td:
            root = self._root(td)
            with patch.dict(os.environ, {}, clear=True),                  patch("readiness.shutil.which", return_value="/usr/bin/docker"),                  patch("readiness.load_providers", return_value=(object(),)):
                result = readiness.check(root)

            self.assertFalse(result["ready"])
            self.assertIn(
                "env_studio_checkpoint_path",
                result["failed"],
            )

    def test_all_runtime_prerequisites_can_pass(self):
        with tempfile.TemporaryDirectory() as td:
            root = self._root(td)
            env = {
                "STUDIO_QUICK_GATE_CACHE_PATH": str(root / "quick.json"),
                "STUDIO_FULL_GATE_CACHE_PATH": str(root / "full.json"),
                "STUDIO_ARTIFACT_CACHE_PATH": str(root / "artifact.json"),
                "STUDIO_ARTIFACT_CAS_PATH": str(root / "cas"),
                "STUDIO_CHECKPOINT_PATH": str(root / "checkpoint.json"),
                "STUDIO_TASK_LEASE_PATH": str(root / "task-leases.json"),
                "STUDIO_TELEMETRY_PATH": str(root / "telemetry.jsonl"),
            }
            with patch.dict(os.environ, env, clear=True),                  patch("readiness.shutil.which", return_value="/usr/bin/docker"),                  patch("readiness.load_providers", return_value=(object(),)):
                result = readiness.check(root)

            self.assertTrue(result["ready"])
            self.assertEqual(result["failed"], [])


if __name__ == "__main__":
    unittest.main()
