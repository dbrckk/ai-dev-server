import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from adaptive_phase_policy import review_phase_decision


class AdaptivePhasePolicyTests(unittest.TestCase):
    def test_low_risk_round_skips_model_review_after_trusted_verification(self):
        decision = review_phase_decision(
            require_review=False,
            verification={"passed": True},
            review_remaining=120,
        )
        self.assertFalse(decision["launch_model"])
        self.assertTrue(decision["review"]["complete"])
        self.assertTrue(decision["review"]["adaptive_skipped"])

    def test_failed_verification_never_becomes_complete_when_review_is_skipped(self):
        decision = review_phase_decision(
            require_review=False,
            verification={"passed": False},
            review_remaining=120,
        )
        self.assertFalse(decision["launch_model"])
        self.assertFalse(decision["review"]["complete"])
        self.assertIn("verification", decision["review"]["reason"])

    def test_required_review_launches_model_when_budget_allows(self):
        decision = review_phase_decision(
            require_review=True,
            verification={"passed": True},
            review_remaining=120,
        )
        self.assertTrue(decision["launch_model"])
        self.assertIsNone(decision["review"])

    def test_quota_exhaustion_fails_closed_even_when_review_is_required(self):
        decision = review_phase_decision(
            require_review=True,
            verification={"passed": True},
            review_remaining=20,
        )
        self.assertFalse(decision["launch_model"])
        self.assertFalse(decision["review"]["complete"])
        self.assertIn("quota", decision["review"]["reason"])


if __name__ == "__main__":
    unittest.main()
