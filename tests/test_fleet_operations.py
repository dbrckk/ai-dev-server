import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import fleet_dashboard
import fleet_supervisor


class FleetOperationsTests(unittest.TestCase):
    def test_dashboard_aggregates_projects(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for name in ("a", "b"):
                (root / name / ".autonomy").mkdir(parents=True)

            reports = {
                "a": {
                    "status": "healthy",
                    "runtime_status": "complete",
                    "attempt": 2,
                    "checkpoint_entries": 3,
                    "leases": {"claims": 0},
                    "telemetry": {"events": 10},
                    "errors": [],
                },
                "b": {
                    "status": "degraded",
                    "runtime_status": "running",
                    "attempt": 1,
                    "checkpoint_entries": 1,
                    "leases": {"claims": 1},
                    "telemetry": {"events": 4},
                    "errors": ["telemetry:empty"],
                },
            }

            with patch("fleet_dashboard.inspect", side_effect=lambda p: reports[Path(p).name]):
                report = fleet_dashboard.collect(root)

            self.assertEqual(report["summary"]["total"], 2)
            self.assertEqual(report["summary"]["healthy"], 1)
            self.assertEqual(report["summary"]["degraded"], 1)
            self.assertEqual(report["summary"]["complete"], 1)
            self.assertEqual(report["summary"]["running"], 1)

    def test_supervisor_quarantines_state_integrity_failures(self):
        dashboard = {
            "projects": [
                {
                    "id": "bad",
                    "status": "degraded",
                    "runtime_status": "running",
                    "errors": ["leases:invalid"],
                },
                {
                    "id": "recoverable",
                    "status": "degraded",
                    "runtime_status": "deferred",
                    "errors": ["telemetry:empty"],
                },
                {
                    "id": "done",
                    "status": "healthy",
                    "runtime_status": "complete",
                    "errors": [],
                },
            ],
            "summary": {},
        }
        with patch("fleet_supervisor.collect", return_value=dashboard):
            report = fleet_supervisor.plan("ignored")

        actions = {row["id"]: row["action"] for row in report["actions"]}
        self.assertEqual(actions["bad"], "quarantine")
        self.assertEqual(actions["recoverable"], "restart")
        self.assertEqual(actions["done"], "none")


if __name__ == "__main__":
    unittest.main()
