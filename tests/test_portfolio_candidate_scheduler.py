import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from portfolio_candidate_scheduler import choose_schedule, MAX_CANDIDATES


class PortfolioCandidateSchedulerTests(unittest.TestCase):
    def test_single_candidate_when_route_is_confident(self):
        schedule = choose_schedule(
            capacity_status={"unmetered_available": True, "providers": []},
            route_confidence=0.9,
            verification_seconds=30,
            remaining_seconds=1000,
            available_agents=2,
            strategy="dual",
        )
        self.assertEqual(schedule.candidate_limit, 1)
        self.assertFalse(schedule.continue_after_verified)

    def test_two_candidates_when_uncertain_and_free_capacity_exists(self):
        schedule = choose_schedule(
            capacity_status={
                "unmetered_available": False,
                "providers": [{
                    "mode": "pooled-free",
                    "monthly_quota": {
                        "remaining_ratio": 0.7,
                        "exhausted": False,
                    },
                }],
            },
            route_confidence=0.5,
            verification_seconds=90,
            remaining_seconds=800,
            available_agents=1,
            strategy="dual",
        )
        self.assertEqual(schedule.candidate_limit, 2)
        self.assertTrue(schedule.continue_after_verified)

    def test_three_candidates_require_high_uncertainty_and_cheap_verification(self):
        schedule = choose_schedule(
            capacity_status={"unmetered_available": True, "providers": []},
            route_confidence=0.2,
            verification_seconds=60,
            remaining_seconds=1200,
            available_agents=2,
            strategy="dual",
        )
        self.assertEqual(schedule.candidate_limit, 3)
        self.assertEqual(schedule.agent_limit, 2)
        self.assertLessEqual(schedule.candidate_limit, MAX_CANDIDATES)

    def test_expensive_verification_prevents_wide_portfolio(self):
        schedule = choose_schedule(
            capacity_status={"unmetered_available": True, "providers": []},
            route_confidence=0.1,
            verification_seconds=500,
            remaining_seconds=5000,
            available_agents=2,
            strategy="dual",
        )
        self.assertEqual(schedule.candidate_limit, 1)

    def test_model_only_never_spawns_agents(self):
        schedule = choose_schedule(
            capacity_status={"unmetered_available": True, "providers": []},
            route_confidence=0.0,
            verification_seconds=30,
            remaining_seconds=1000,
            available_agents=3,
            strategy="model_only",
        )
        self.assertEqual(schedule.candidate_limit, 1)
        self.assertEqual(schedule.agent_limit, 0)
        self.assertTrue(schedule.include_model)

    def test_agent_only_does_not_require_model_candidate(self):
        schedule = choose_schedule(
            capacity_status={"unmetered_available": True, "providers": []},
            route_confidence=0.3,
            verification_seconds=60,
            remaining_seconds=1000,
            available_agents=2,
            strategy="agent_only",
        )
        self.assertFalse(schedule.include_model)
        self.assertGreaterEqual(schedule.agent_limit, 1)


if __name__ == "__main__":
    unittest.main()
