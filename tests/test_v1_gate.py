import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import v1_gate


class V1GateTests(unittest.TestCase):
    def test_ready_host_without_project(self):
        readiness = {"ready": True, "checks": {"python": True}, "failed": []}
        with patch("v1_gate.readiness_check", return_value=readiness):
            report = v1_gate.evaluate(".")
        self.assertTrue(report["ready"])
        self.assertEqual(report["verdict"], "ready")
        self.assertIsNone(report["runtime"])

    def test_operational_project_requires_healthy_runtime(self):
        readiness = {"ready": True, "checks": {"python": True}, "failed": []}
        runtime = {"status": "healthy", "errors": [], "runtime_status": "running"}
        with patch("v1_gate.readiness_check", return_value=readiness), patch(
            "v1_gate.runtime_health", return_value=runtime
        ):
            report = v1_gate.evaluate(".", "out/project")
        self.assertTrue(report["ready"])
        self.assertEqual(report["verdict"], "operational")

    def test_degraded_runtime_blocks_gate(self):
        readiness = {"ready": True, "checks": {"python": True}, "failed": []}
        runtime = {
            "status": "degraded",
            "errors": ["leases:invalid"],
            "runtime_status": "running",
        }
        with patch("v1_gate.readiness_check", return_value=readiness), patch(
            "v1_gate.runtime_health", return_value=runtime
        ):
            report = v1_gate.evaluate(".", "out/project")
        self.assertFalse(report["ready"])
        self.assertEqual(report["verdict"], "blocked")
        self.assertIn("runtime:leases:invalid", report["failures"])

    def test_host_readiness_failure_blocks_gate(self):
        readiness = {
            "ready": False,
            "checks": {"docker_available": False},
            "failed": ["docker_available"],
        }
        with patch("v1_gate.readiness_check", return_value=readiness):
            report = v1_gate.evaluate(".")
        self.assertFalse(report["ready"])
        self.assertEqual(report["verdict"], "blocked")
        self.assertIn("readiness:docker_available", report["failures"])


if __name__ == "__main__":
    unittest.main()
