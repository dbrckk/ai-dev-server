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


    def test_routing_bonus_prefers_verified_efficient_model(self):
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
                    project_id="a",
                    provider="slow",
                    model="m2",
                    tokens=4000,
                    verified_success=True,
                )
            summary = efficiency.summarize(path)
            fast = efficiency.routing_bonus(
                summary,
                project_id="a",
                provider="fast",
                model="m1",
            )
            slow = efficiency.routing_bonus(
                summary,
                project_id="a",
                provider="slow",
                model="m2",
            )
            self.assertGreater(fast, slow)
            self.assertLessEqual(abs(fast), 8.0)
            self.assertLessEqual(abs(slow), 8.0)

    def test_routing_bonus_requires_mature_comparison(self):
        summary = {
            "rows": [
                {
                    "project_id": "a",
                    "provider": "p",
                    "model": "m",
                    "samples": 2,
                    "risk_adjusted_score": 100.0,
                }
            ]
        }
        self.assertEqual(
            efficiency.routing_bonus(
                summary,
                project_id="a",
                provider="p",
                model="m",
            ),
            0.0,
        )



    def test_failure_streak_resets_after_verified_success(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "efficiency.json"
            for _ in range(3):
                row = efficiency.record(
                    path,
                    project_id="a",
                    provider="p",
                    model="m",
                    tokens=1000,
                    verified_success=False,
                )
            self.assertEqual(row["failure_streak"], 3)
            row = efficiency.record(
                path,
                project_id="a",
                provider="p",
                model="m",
                tokens=1000,
                verified_success=True,
            )
            self.assertEqual(row["failure_streak"], 0)
            self.assertEqual(row["success_streak"], 1)



    def test_stagnation_routing_penalty_escalates_with_failure_streak(self):
        summary = {
            "rows": [
                {
                    "project_id": "a",
                    "provider": "p",
                    "model": "m",
                    "samples": 8,
                    "failure_streak": 8,
                    "risk_adjusted_score": 0.0,
                }
            ]
        }
        self.assertEqual(
            efficiency.stagnation_routing_penalty(
                summary,
                project_id="a",
                provider="p",
                model="m",
            ),
            -24.0,
        )

    def test_stagnation_routing_penalty_is_neutral_without_streak(self):
        summary = {
            "rows": [
                {
                    "project_id": "a",
                    "provider": "p",
                    "model": "m",
                    "samples": 8,
                    "failure_streak": 0,
                    "risk_adjusted_score": 10.0,
                }
            ]
        }
        self.assertEqual(
            efficiency.stagnation_routing_penalty(
                summary,
                project_id="a",
                provider="p",
                model="m",
            ),
            0.0,
        )


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
