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
             patch("fleet_daemon.capacity_ledger_snapshot", return_value={"active_reservations": 0, "reserved_tokens": 0, "consumed_tokens": 0, "reaped": 0}), \
             patch("fleet_daemon.apply_preemption", return_value={"apply": False, "preemptions_executed": 0, "results": []}), \
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
             patch("fleet_daemon.capacity_ledger_snapshot", return_value={"active_reservations": 0, "reserved_tokens": 0, "consumed_tokens": 0, "reaped": 0}), \
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
             patch("fleet_daemon.persist_capacity_plan", return_value={"summary": {"active_projects": 1, "allocated_tokens": 32000}, "rebalance": {"pressured_projects": 1}}) as capacity, \
             patch("fleet_daemon.capacity_ledger_snapshot", return_value={"active_reservations": 2, "reserved_tokens": 2000, "consumed_tokens": 4000, "reaped": 1}), \
             patch("fleet_daemon.apply_preemption", return_value={"apply": False, "preemptions_executed": 0, "results": []}), \
             patch("fleet_daemon.apply_supervisor", return_value={"apply": False, "restarts_executed": 0, "results": []}):
            report = fleet_daemon.tick("out", "requests")

        capacity.assert_called_once()
        self.assertEqual(report["capacity"]["allocated_tokens"], 32000)
        self.assertEqual(report["capacity"]["ledger"]["active_reservations"], 2)
        self.assertEqual(report["capacity"]["rebalance"]["pressured_projects"], 1)


    def test_tick_applies_preemption_then_replans_capacity(self):
        plans = [
            {"summary": {"active_projects": 2, "allocated_tokens": 32000}},
            {"summary": {"active_projects": 2, "allocated_tokens": 48000}},
        ]
        with patch("fleet_daemon.collect", return_value={"summary": {"total": 2}}), \
             patch("fleet_daemon.snapshot", return_value={"ts": 1, "healthy": 2}), \
             patch("fleet_daemon.append_metrics", return_value={"snapshots": 1, "latest": {"ts": 1}}), \
             patch("fleet_daemon.evaluate_regression", return_value={"regressed": False, "regressions": []}), \
             patch("fleet_daemon.maintain", return_value={"summary": {"projects": 2}}), \
             patch("fleet_daemon.classify_worker_liveness", return_value={"summary": {"expired": 0, "crashed": 0, "stalled": 0, "orphaned": 0, "recoverable_tokens": 0}}), \
             patch("fleet_daemon.persist_capacity_plan", side_effect=plans) as capacity, \
             patch("fleet_daemon.apply_preemption", return_value={"apply": True, "preemptions_executed": 1, "results": [{"status": "preempted"}]}) as preempt, \
             patch("fleet_daemon.capacity_ledger_snapshot", return_value={"active_reservations": 0, "reserved_tokens": 0, "consumed_tokens": 0, "reaped": 0}), \
             patch("fleet_daemon.apply_supervisor", return_value={"apply": False, "restarts_executed": 0, "results": []}):
            report = fleet_daemon.tick("out", "requests", apply_preemptions=True)

        self.assertEqual(capacity.call_count, 2)
        self.assertTrue(preempt.call_args.kwargs["apply"])
        self.assertEqual(report["capacity"]["allocated_tokens"], 48000)
        self.assertEqual(report["preemption"]["preemptions_executed"], 1)


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
