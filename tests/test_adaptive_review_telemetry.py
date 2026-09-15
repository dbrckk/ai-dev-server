import importlib
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "studio"))
GENERIC_PROJECT = ROOT / "studio" / "generic_project.py"


class AdaptiveReviewTelemetryTests(unittest.TestCase):
    def test_review_policy_reports_stable_reason_for_each_decision(self):
        policy = importlib.import_module("adaptive_phase_policy")
        review_phase_decision = policy.review_phase_decision

        required = review_phase_decision(
            require_review=True,
            verification={"passed": True},
            review_remaining=120,
        )
        self.assertEqual(required["reason"], "adaptive review required")

        quota_exhausted = review_phase_decision(
            require_review=True,
            verification={"passed": True},
            review_remaining=20,
        )
        self.assertEqual(quota_exhausted["reason"], "required review quota exhausted")

        skipped = review_phase_decision(
            require_review=False,
            verification={"passed": True},
            review_remaining=120,
        )
        self.assertEqual(
            skipped["reason"],
            "adaptive policy skipped model review after trusted verification",
        )

        failed_verification = review_phase_decision(
            require_review=False,
            verification={"passed": False},
            review_remaining=120,
        )
        self.assertEqual(
            failed_verification["reason"],
            "adaptive model review was skipped, but trusted verification did not pass",
        )

    def test_round_state_persists_review_decision_telemetry(self):
        source = GENERIC_PROJECT.read_text(encoding="utf-8")

        self.assertIn("review_decision = {", source)
        self.assertIn('"model_launched": bool(review_policy["launch_model"])', source)
        self.assertIn('"adaptive_skipped": (', source)
        self.assertIn('"require_review": round_require_review', source)
        self.assertIn('"review_remaining": round(review_remaining, 4)', source)
        self.assertIn('"verification_passed": (', source)
        self.assertIn('"reason": review_policy["reason"]', source)
        self.assertIn('"review_decision": review_decision', source)


if __name__ == "__main__":
    unittest.main()
