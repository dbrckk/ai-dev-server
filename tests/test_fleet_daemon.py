import unittest
from unittest.mock import patch
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import fleet_daemon


class FleetDaemonTests(unittest.TestCase):
    def test_tick_suppresses_restarts_when_regression_detected(self):
        with patch("fleet_daemon.collect", return_value={"summary": {"total": 1}}), \
             patch("fleet_daemon.snapshot", return_value={"ts": 1, "healthy": 1}), \
             patch("fleet_daemon.append_metrics", return_value={"snapshots": 2, "latest": {"ts": 1}}), \
             patch("fleet_daemon.evaluate_regression", return_value={"regressed": True, "regressions": ["healthy_projects_decreased"]}), \
             patch("fleet_daemon.maintain", return_value={"summary": {"projects": 1}}), \
             patch("fleet_daemon.persist_capacity_plan", return_value={"summary": {"active_projects": 1, "allocated_tokens": 100}}), \
             patch("fleet_daemon.apply_supervisor", return_value={"apply": False, "restarts_executed": 0, "results": []}) as supervisor:
            report = fleet_daemon.tick("out", "requests", apply_restarts=True, max_restarts=2)

        self.assertTrue(report["regression"]["regressed"])
        supervisor.assert_called_once()
        self.assertFalse(supervisor.call_args.kwargs["apply"])

    def test_tick_allows_bounded_restarts_without_regression(self):
        with patch("fleet_daemon.collect", return_value={"summary": {"total": 1}}), \
             patch("fleet_daemon.snapshot", return_value={"ts": 1, "healthy": 1}), \
             patch("fleet_daemon.append_metrics", return_value={"snapshots": 2, "latest": {"ts": 1}}), \
             patch("fleet_daemon.evaluate_regression", return_value={"regressed": False, "regressions": []}), \
             patch("fleet_daemon.maintain", return_value={"summary": {"projects": 1}}), \
             patch("fleet_daemon.persist_capacity_plan", return_value={"summary": {"active_projects": 1, "allocated_tokens": 100}}), \
             patch("fleet_daemon.apply_supervisor", return_value={"apply": True, "restarts_executed": 1, "results": []}) as supervisor:
            report = fleet_daemon.tick("out", "requests", apply_restarts=True, max_restarts=1)

        self.assertEqual(report["supervisor"]["restarts_executed"], 1)
        self.assertTrue(supervisor.call_args.kwargs["apply"])
        self.assertEqual(supervisor.call_args.kwargs["max_restarts"], 1)


    def test_tick_persists_capacity_plan(self):
        with patch("fleet_daemon.collect", return_value={"summary": {"total": 1}}), \
             patch("fleet_daemon.snapshot", return_value={"ts": 1, "healthy": 1}), \
             patch("fleet_daemon.append_metrics", return_value={"snapshots": 1, "latest": {"ts": 1}}), \
             patch("fleet_daemon.evaluate_regression", return_value={"regressed": False, "regressions": []}), \
             patch("fleet_daemon.maintain", return_value={"summary": {"projects": 1}}), \
             patch("fleet_daemon.persist_capacity_plan", return_value={"summary": {"active_projects": 1, "allocated_tokens": 32000}}) as capacity, \
             patch("fleet_daemon.apply_supervisor", return_value={"apply": False, "restarts_executed": 0, "results": []}):
            report = fleet_daemon.tick("out", "requests")

        capacity.assert_called_once()
        self.assertEqual(report["capacity"]["allocated_tokens"], 32000)


    def test_run_loop_enforces_minimum_interval(self):
        sleeps = []
        with patch("fleet_daemon.tick", return_value={"ok": True}):
            rows = fleet_daemon.run_loop(
                "out",
                "requests",
                interval_seconds=1,
                iterations=2,
                sleep=lambda seconds: sleeps.append(seconds),
            )

        self.assertEqual(len(rows), 2)
        self.assertEqual(sleeps, [fleet_daemon.MIN_INTERVAL_SECONDS])


if __name__ == "__main__":
    unittest.main()
