import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import architecture_feedback as af


class ArchitectureFeedbackTests(unittest.TestCase):
    def test_insufficient_history_does_not_bias(self):
        recs = {"matches": [{"repo": "a/core", "score": 90.0, "quality_score": 9.0}]}
        learning = {"rankings": [{"repo": "a/core", "samples": 4, "success_rate": 1.0}]}

        result = af.apply(recs, learning)

        self.assertFalse(result["feedback_applied"])
        self.assertEqual(result["matches"][0]["feedback_score"], 90.0)
        self.assertNotIn("historical_evidence", result["matches"][0])

    def test_success_history_applies_bounded_bonus(self):
        recs = {
            "matches": [
                {"repo": "a/core", "score": 90.0, "quality_score": 9.0},
                {"repo": "b/other", "score": 91.0, "quality_score": 8.0},
            ]
        }
        learning = {
            "rankings": [
                {
                    "repo": "a/core",
                    "samples": 8,
                    "success_rate": 1.0,
                    "mean_model_calls": 2.0,
                    "mean_cycles": 1.0,
                    "mean_blockers": 0.0,
                }
            ]
        }

        result = af.apply(recs, learning)

        self.assertTrue(result["feedback_applied"])
        self.assertEqual(result["matches"][0]["repo"], "a/core")
        self.assertEqual(result["matches"][0]["feedback_score"], 93.0)
        self.assertLessEqual(
            abs(result["matches"][0]["historical_evidence"]["advisory_bonus"]),
            af.MAX_SCORE_BONUS,
        )
        self.assertFalse(result["feedback_policy"]["can_add_dependency"])

    def test_poor_history_can_only_apply_small_penalty(self):
        recs = {"matches": [{"repo": "a/core", "score": 90.0}]}
        learning = {"rankings": [{"repo": "a/core", "samples": 10, "success_rate": 0.0}]}

        result = af.apply(recs, learning)

        self.assertEqual(result["matches"][0]["feedback_score"], 87.0)


if __name__ == "__main__":
    unittest.main()
