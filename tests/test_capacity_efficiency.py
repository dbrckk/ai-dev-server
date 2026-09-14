import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import capacity_efficiency as efficiency


class CapacityEfficiencyTests(unittest.TestCase):
    def test_verified_progress_per_token_rewards_efficient_model(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "efficiency.json"
            for _ in range(4):
                efficiency.record(
                    path,
                    project_id="a",
                    provider="fast",
                    model="m1",
                    tokens=1000,
                    verified_success=True,
                )
                efficiency.record(
                    path,
                    project_id="b",
                    provider="slow",
                    model="m2",
                    tokens=4000,
                    verified_success=True,
                )
            summary = efficiency.summarize(path)
            self.assertGreater(
                summary["projects"]["a"]["risk_adjusted_score"],
                summary["projects"]["b"]["risk_adjusted_score"],
            )
            self.assertGreater(
                efficiency.project_multiplier(summary, "a"),
                efficiency.project_multiplier(summary, "b"),
            )

    def test_failures_reduce_efficiency(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "efficiency.json"
            for success in (True, False, False, False):
                efficiency.record(
                    path,
                    project_id="a",
                    provider="p",
                    model="m",
                    tokens=1000,
                    verified_success=success,
                )
            row = efficiency.summarize(path)["rows"][0]
            self.assertLess(row["success_rate"], 0.5)

    def test_sparse_projects_remain_neutral(self):
        summary = {
            "projects": {
                "a": {"samples": 1, "risk_adjusted_score": 100.0},
                "b": {"samples": 10, "risk_adjusted_score": 10.0},
            }
        }
        self.assertEqual(efficiency.project_multiplier(summary, "a"), 1.0)


if __name__ == "__main__":
    unittest.main()
