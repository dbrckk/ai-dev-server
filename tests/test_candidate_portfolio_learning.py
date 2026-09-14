import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import candidate_portfolio_learning as learning
from portfolio_candidate_scheduler import choose_schedule


class CandidatePortfolioLearningTests(unittest.TestCase):
    def test_recommendation_requires_minimum_samples(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "candidate-width.json"
            for _ in range(learning.MIN_SAMPLES - 1):
                learning.record(path, width=2, success=True, cost_seconds=90)
            result = learning.recommendation(learning.load(path))
            self.assertIsNone(result["recommended_width"])

    def test_verified_success_dominates_cost(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "candidate-width.json"
            for _ in range(6):
                learning.record(path, width=2, success=True, cost_seconds=120)
                learning.record(path, width=1, success=False, cost_seconds=20)
            result = learning.recommendation(learning.load(path))
            self.assertEqual(result["recommended_width"], 2)

    def test_cost_breaks_close_success_outcomes(self):
        data = {
            "width:2": {
                "samples": 8,
                "successes": 7,
                "ema_success": 0.9,
                "ema_cost_seconds": 60.0,
            },
            "width:3": {
                "samples": 8,
                "successes": 7,
                "ema_success": 0.9,
                "ema_cost_seconds": 360.0,
            },
        }
        result = learning.recommendation(data)
        self.assertEqual(result["recommended_width"], 2)

    def test_history_can_reduce_but_not_expand_safe_width(self):
        reduced = choose_schedule(
            capacity_status={"unmetered_available": True, "providers": []},
            route_confidence=0.1,
            verification_seconds=40,
            remaining_seconds=1200,
            available_agents=2,
            available_models=3,
            strategy="dual",
            recommended_width=2,
        )
        self.assertEqual(reduced.candidate_limit, 2)

        not_expanded = choose_schedule(
            capacity_status={"unmetered_available": True, "providers": []},
            route_confidence=0.95,
            verification_seconds=40,
            remaining_seconds=1200,
            available_agents=2,
            available_models=3,
            strategy="dual",
            recommended_width=3,
        )
        self.assertEqual(not_expanded.candidate_limit, 1)


if __name__ == "__main__":
    unittest.main()
