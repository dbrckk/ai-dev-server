import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import ci_runner


class CiRunnerAdmissionTests(unittest.TestCase):
    def test_denied_project_never_creates_worker(self):
        projects = [
            {"id": "a", "file": "a.json"},
            {"id": "b", "file": "b.json"},
        ]
        capacity_plan = {
            "projects": [
                {
                    "id": "a",
                    "admission": {
                        "admitted": False,
                        "reason": "fleet_admission_slots_saturated",
                    },
                },
                {
                    "id": "b",
                    "admission": {
                        "admitted": True,
                        "reason": "ranked_within_admission_slots",
                    },
                },
            ]
        }

        def fake_run(*args, **kwargs):
            return {"status": "complete", "next_stage": None}

        with tempfile.TemporaryDirectory() as td, patch(
            "ci_runner.matrix", return_value=projects
        ), patch(
            "ci_runner.persist_capacity_plan", return_value=capacity_plan
        ), patch(
            "ci_runner._run_project_for_queue", side_effect=fake_run
        ) as run:
            code = ci_runner.run_queue(
                "requests",
                Path(td),
                clock=lambda: 100.0,
            )
            report = __import__("json").loads(
                (Path(td) / "queue.json").read_text(encoding="utf-8")
            )

        self.assertEqual(run.call_count, 1)
        by_id = {row["id"]: row for row in report["projects"]}
        self.assertEqual(by_id["a"]["status"], "deferred_by_admission")
        self.assertEqual(by_id["b"]["status"], "complete")
        self.assertEqual(code, 1)

    def test_missing_admission_decision_fails_open(self):
        projects = [{"id": "a", "file": "a.json"}]
        with tempfile.TemporaryDirectory() as td, patch(
            "ci_runner.matrix", return_value=projects
        ), patch(
            "ci_runner.persist_capacity_plan", return_value={"projects": []}
        ), patch(
            "ci_runner._run_project_for_queue",
            return_value={"status": "complete", "next_stage": None},
        ) as run:
            ci_runner.run_queue("requests", Path(td), clock=lambda: 100.0)

        run.assert_called_once()


if __name__ == "__main__":
    unittest.main()
