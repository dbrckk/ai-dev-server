import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from predictive_budget import can_start_generation, estimate


class PredictiveBudgetTests(unittest.TestCase):
    def test_small_clean_repo_is_low_difficulty(self):
        result = estimate(
            file_count=12,
            source_bytes=80_000,
            previous_failures=0,
            verification_seconds=20,
            bootstrap_passed=True,
        )
        self.assertEqual(result.band, "low")
        self.assertEqual(result.recommended_work_passes, 1)

    def test_failure_history_and_slow_verification_raise_difficulty(self):
        result = estimate(
            file_count=200,
            source_bytes=1_000_000,
            previous_failures=6,
            verification_seconds=240,
            bootstrap_passed=False,
        )
        self.assertIn(result.band, {"high", "very_high"})
        self.assertGreaterEqual(result.verification_reserve_seconds, 240)
        self.assertEqual(result.recommended_agent_limit, 2)

    def test_generation_is_refused_when_it_would_consume_verification_reserve(self):
        self.assertFalse(can_start_generation(
            remaining_seconds=250,
            reserve_seconds=180,
            minimum_generation_seconds=90,
        ))
        self.assertTrue(can_start_generation(
            remaining_seconds=400,
            reserve_seconds=180,
            minimum_generation_seconds=90,
        ))


if __name__ == "__main__":
    unittest.main()
