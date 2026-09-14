import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import fleet_supervisor_apply as fsa


class FleetSupervisorApplyTests(unittest.TestCase):
    def _projects(self):
        return [
            {"id": "a", "file": "a.json"},
            {"id": "b", "file": "b.json"},
        ]

    def test_dry_run_never_executes_restart(self):
        decisions = {
            "actions": [
                {"id": "a", "action": "restart"},
                {"id": "b", "action": "quarantine"},
            ]
        }
        with patch("fleet_supervisor_apply.plan", return_value=decisions), patch(
            "fleet_supervisor_apply.matrix", return_value=self._projects()
        ), patch("fleet_supervisor_apply._run_project_for_queue") as run:
            report = fsa.execute("out", "requests", apply=False)

        run.assert_not_called()
        statuses = {row["id"]: row["status"] for row in report["results"]}
        self.assertEqual(statuses["a"], "dry_run")
        self.assertEqual(statuses["b"], "skipped_quarantine")
        self.assertEqual(report["restarts_executed"], 0)

    def test_apply_executes_only_restartable_projects_with_budget(self):
        decisions = {
            "actions": [
                {"id": "a", "action": "restart"},
                {"id": "b", "action": "restart"},
                {"id": "c", "action": "quarantine"},
            ]
        }

        def fake_run(project, project_out, work, runner, deadline, clock, baseline_sha):
            return {"status": "complete", "next_stage": None}

        with patch("fleet_supervisor_apply.plan", return_value=decisions), patch(
            "fleet_supervisor_apply.matrix", return_value=self._projects()
        ), patch(
            "fleet_supervisor_apply._run_project_for_queue", side_effect=fake_run
        ) as run:
            report = fsa.execute(
                "out",
                "requests",
                apply=True,
                max_restarts=1,
                clock=lambda: 100.0,
            )

        self.assertEqual(run.call_count, 1)
        statuses = {row["id"]: row["status"] for row in report["results"]}
        self.assertEqual(statuses["a"], "complete")
        self.assertEqual(statuses["b"], "restart_budget_exhausted")
        self.assertEqual(statuses["c"], "skipped_quarantine")
        self.assertEqual(report["restarts_executed"], 1)

    def test_missing_request_is_not_executed(self):
        decisions = {"actions": [{"id": "missing", "action": "restart"}]}
        with patch("fleet_supervisor_apply.plan", return_value=decisions), patch(
            "fleet_supervisor_apply.matrix", return_value=[]
        ), patch("fleet_supervisor_apply._run_project_for_queue") as run:
            report = fsa.execute("out", "requests", apply=True)

        run.assert_not_called()
        self.assertEqual(report["results"][0]["status"], "request_missing")


if __name__ == "__main__":
    unittest.main()
