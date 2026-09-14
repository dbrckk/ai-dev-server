import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import fleet_metrics
import fleet_regression


class FleetMetricsTests(unittest.TestCase):
    def test_snapshot_aggregates_operational_totals(self):
        dashboard = {
            "summary": {
                "total": 2,
                "healthy": 2,
                "degraded": 0,
                "running": 1,
                "complete": 1,
                "blocked": 0,
            },
            "projects": [
                {
                    "active_leases": 1,
                    "checkpoint_entries": 4,
                    "telemetry_events": 10,
                },
                {
                    "active_leases": 0,
                    "checkpoint_entries": 2,
                    "telemetry_events": 6,
                },
            ],
        }
        with patch("fleet_metrics.collect", return_value=dashboard):
            row = fleet_metrics.snapshot("ignored", ts=100.0)

        self.assertEqual(row["active_leases"], 1)
        self.assertEqual(row["checkpoint_entries"], 6)
        self.assertEqual(row["telemetry_events"], 16)
        self.assertEqual(row["ts"], 100.0)

    def test_history_is_bounded(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "metrics.json"
            with patch.object(fleet_metrics, "MAX_SNAPSHOTS", 3):
                for index in range(5):
                    fleet_metrics.append(path, {"ts": index, "healthy": index})
            rows = fleet_metrics.load(path)
            self.assertEqual(len(rows), 3)
            self.assertEqual([row["ts"] for row in rows], [2, 3, 4])

    def test_regression_detects_health_drop_and_lease_spike(self):
        result = fleet_regression.compare(
            {
                "healthy": 4,
                "degraded": 0,
                "blocked": 0,
                "active_leases": 1,
            },
            {
                "healthy": 3,
                "degraded": 1,
                "blocked": 1,
                "active_leases": 5,
            },
        )
        self.assertTrue(result["regressed"])
        self.assertIn("healthy_projects_decreased", result["regressions"])
        self.assertIn("degraded_projects_increased", result["regressions"])
        self.assertIn("blocked_projects_increased", result["regressions"])
        self.assertIn("active_leases_spike", result["regressions"])

    def test_insufficient_history_is_not_a_regression(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "metrics.json"
            fleet_metrics.append(path, {"ts": 1, "healthy": 1})
            result = fleet_regression.evaluate(path)
            self.assertFalse(result["regressed"])
            self.assertTrue(result["insufficient_history"])


if __name__ == "__main__":
    unittest.main()
