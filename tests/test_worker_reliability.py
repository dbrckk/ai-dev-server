import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from worker_reliability import summarize, project_multiplier


class WorkerReliabilityTests(unittest.TestCase):
    def test_failures_reduce_reliability_with_bounded_penalty(self):
        workers = [
            {"project_id": "bad", "classification": "crashed"},
            {"project_id": "bad", "classification": "stalled"},
            {"project_id": "bad", "classification": "orphaned"},
            {"project_id": "bad", "classification": "crashed"},
            {"project_id": "bad", "classification": "stalled"},
            {"project_id": "bad", "classification": "crashed"},
            {"project_id": "bad", "classification": "stalled"},
            {"project_id": "bad", "classification": "crashed"},
        ]
        report = summarize({"workers": workers})
        row = report["projects"]["bad"]
        self.assertLess(row["reliability_score"], 0.5)
        self.assertLess(row["capacity_multiplier"], 1.0)
        self.assertGreaterEqual(project_multiplier(report, "bad"), 0.75)

    def test_completed_workers_improve_reliability(self):
        report = summarize({"workers": [
            {"project_id": "good", "classification": "completed"}
            for _ in range(8)
        ]})
        self.assertGreater(report["projects"]["good"]["reliability_score"], 0.5)
        self.assertGreater(report["projects"]["good"]["capacity_multiplier"], 1.0)

    def test_sparse_history_stays_close_to_neutral(self):
        report = summarize({"workers": [
            {"project_id": "new", "classification": "crashed"},
        ]})
        self.assertGreater(report["projects"]["new"]["capacity_multiplier"], 0.9)

    def test_unknown_project_is_neutral(self):
        self.assertEqual(project_multiplier({"projects": {}}, "new"), 1.0)


if __name__ == "__main__":
    unittest.main()
