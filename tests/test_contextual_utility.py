import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from contextual_utility import utility_score, MAX_UTILITY_BONUS, MAX_UTILITY_PENALTY


class ContextualUtilityTests(unittest.TestCase):
    def test_high_success_fast_free_is_positive(self):
        result = utility_score(
            expected_success=0.9,
            execution_seconds=5,
            verification_seconds=20,
            architecture_hold=False,
            free_preferred=True,
        )
        self.assertGreater(result["score"], 0)
        self.assertLessEqual(result["score"], MAX_UTILITY_BONUS)

    def test_slow_low_success_is_penalized(self):
        result = utility_score(
            expected_success=0.2,
            execution_seconds=90,
            verification_seconds=240,
            architecture_hold=False,
            free_preferred=True,
        )
        self.assertLess(result["score"], 0)
        self.assertGreaterEqual(result["score"], -MAX_UTILITY_PENALTY)

    def test_architecture_hold_reduces_utility(self):
        normal = utility_score(
            expected_success=0.8,
            execution_seconds=20,
            verification_seconds=90,
            architecture_hold=False,
        )
        hold = utility_score(
            expected_success=0.8,
            execution_seconds=20,
            verification_seconds=90,
            architecture_hold=True,
        )
        self.assertLess(hold["score"], normal["score"])

    def test_paid_provider_has_small_extra_cost(self):
        free = utility_score(
            expected_success=0.8,
            execution_seconds=10,
            verification_seconds=30,
            architecture_hold=False,
            free_preferred=True,
        )
        paid = utility_score(
            expected_success=0.8,
            execution_seconds=10,
            verification_seconds=30,
            architecture_hold=False,
            free_preferred=False,
        )
        self.assertLess(paid["score"], free["score"])


if __name__ == "__main__":
    unittest.main()
