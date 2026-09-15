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


    def test_preemption_lease_is_claimed_before_worker_and_released_after(self):
        projects = [{"id": "high", "file": "high.json"}]
        capacity_plan = {
            "projects": [{
                "id": "high",
                "admission": {
                    "admitted": True,
                    "action": "admit_preemption_lease",
                    "reason": "transactional_preemption_lease",
                },
            }]
        }
        events = []

        def claim(*args, **kwargs):
            events.append("claim")
            return {"claimed": True, "reservation_id": "lease-1"}

        def run(*args, **kwargs):
            events.append("worker")
            return {"status": "complete", "next_stage": None}

        def release(*args, **kwargs):
            events.append("release")
            return {"released": True}

        with tempfile.TemporaryDirectory() as td, patch(
            "ci_runner.matrix", return_value=projects
        ), patch(
            "ci_runner.persist_capacity_plan", return_value=capacity_plan
        ), patch(
            "ci_runner.claim_preemption_lease", side_effect=claim
        ), patch(
            "ci_runner._run_project_for_queue", side_effect=run
        ), patch(
            "ci_runner.release_capacity_reservation", side_effect=release
        ):
            ci_runner.run_queue("requests", Path(td), clock=lambda: 100.0)
            report = __import__("json").loads(
                (Path(td) / "queue.json").read_text(encoding="utf-8")
            )

        self.assertEqual(events, ["claim", "worker", "release"])
        self.assertTrue(report["projects"][0]["admission_lease_claimed"])
        self.assertTrue(report["projects"][0]["admission_lease_released"])

    def test_failed_preemption_lease_claim_blocks_worker(self):
        projects = [{"id": "high", "file": "high.json"}]
        capacity_plan = {
            "projects": [{
                "id": "high",
                "admission": {
                    "admitted": True,
                    "action": "admit_preemption_lease",
                },
            }]
        }
        with tempfile.TemporaryDirectory() as td, patch(
            "ci_runner.matrix", return_value=projects
        ), patch(
            "ci_runner.persist_capacity_plan", return_value=capacity_plan
        ), patch(
            "ci_runner.claim_preemption_lease",
            return_value={"claimed": False, "reason": "preemption_lease_missing"},
        ), patch("ci_runner._run_project_for_queue") as run:
            ci_runner.run_queue("requests", Path(td), clock=lambda: 100.0)
            report = __import__("json").loads(
                (Path(td) / "queue.json").read_text(encoding="utf-8")
            )

        run.assert_not_called()
        self.assertEqual(report["projects"][0]["status"], "deferred_by_admission")
        self.assertEqual(
            report["projects"][0]["admission_reason"],
            "preemption_lease_claim_failed",
        )



if __name__ == "__main__":
    unittest.main()
