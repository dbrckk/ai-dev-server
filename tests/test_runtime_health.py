import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import durable_state
import runtime_health
import telemetry
import workflow_checkpoint


class RuntimeHealthTests(unittest.TestCase):
    def test_healthy_project_reports_runtime_signals(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "project"
            autonomy = out / ".autonomy"
            autonomy.mkdir(parents=True)

            durable_state.save(
                autonomy / "runtime-state.json",
                {
                    "goal_id": "demo",
                    "status": "complete",
                    "attempt": 2,
                },
            )

            env = {
                "STUDIO_CHECKPOINT_PATH": str(autonomy / "workflow-checkpoints.json"),
                "STUDIO_TELEMETRY_PATH": str(autonomy / "telemetry.jsonl"),
            }
            with patch.dict(os.environ, env, clear=False):
                key = workflow_checkpoint.operation_key("demo", {"x": 1})
                workflow_checkpoint.put(key, {"ok": True}, kind="demo")
                telemetry.emit("goal_run_finished", goal_id="demo", status="complete")

            (autonomy / "task-leases.json").write_text(
                json.dumps({"schema": 1, "claims": {}}),
                encoding="utf-8",
            )

            report = runtime_health.inspect(out)

            self.assertEqual(report["status"], "healthy")
            self.assertEqual(report["runtime_status"], "complete")
            self.assertEqual(report["checkpoint_entries"], 1)
            self.assertEqual(report["leases"]["claims"], 0)
            self.assertEqual(report["telemetry"]["events"], 1)
            self.assertEqual(report["errors"], [])

    def test_corrupt_runtime_and_lease_state_is_degraded(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "project"
            autonomy = out / ".autonomy"
            autonomy.mkdir(parents=True)
            (autonomy / "runtime-state.json").write_text("{broken", encoding="utf-8")
            (autonomy / "task-leases.json").write_text("{broken", encoding="utf-8")

            report = runtime_health.inspect(out)

            self.assertEqual(report["status"], "degraded")
            self.assertFalse(report["leases"]["valid"])
            self.assertTrue(any(item.startswith("runtime_state:") for item in report["errors"]))
            self.assertIn("leases:invalid", report["errors"])


if __name__ == "__main__":
    unittest.main()
