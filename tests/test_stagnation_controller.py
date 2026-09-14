import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from stagnation_controller import decide, summarize


class StagnationControllerTests(unittest.TestCase):
    def test_sparse_evidence_is_neutral(self):
        decision = decide([{"samples": 2, "failure_streak": 2, "ema_success": 0.0}])
        self.assertEqual(decision.level, "normal")
        self.assertFalse(decision.force_diversify)

    def test_three_failures_trigger_diversification(self):
        decision = decide([{"samples": 3, "failure_streak": 3, "ema_success": 0.2}])
        self.assertEqual(decision.level, "diversify")
        self.assertTrue(decision.force_diversify)
        self.assertEqual(decision.capacity_multiplier, 0.90)

    def test_five_failures_throttle_capacity(self):
        decision = decide([{"samples": 6, "failure_streak": 5, "ema_success": 0.1}])
        self.assertEqual(decision.level, "throttle")
        self.assertEqual(decision.capacity_multiplier, 0.60)

    def test_eight_failures_pause_branch(self):
        decision = decide([{"samples": 8, "failure_streak": 8, "ema_success": 0.0}])
        self.assertEqual(decision.level, "pause")
        self.assertTrue(decision.pause)
        self.assertEqual(decision.capacity_multiplier, 0.0)

    def test_success_resets_stagnation(self):
        decision = decide([{"samples": 10, "failure_streak": 0, "ema_success": 0.4}])
        self.assertEqual(decision.level, "normal")

    def test_summary_counts_actions(self):
        result = summarize({"rows": [
            {"project_id": "a", "samples": 8, "failure_streak": 8, "ema_success": 0.0},
            {"project_id": "b", "samples": 5, "failure_streak": 3, "ema_success": 0.2},
        ]})
        self.assertEqual(result["paused_projects"], 1)
        self.assertEqual(result["diversifying_projects"], 2)


if __name__ == "__main__":
    unittest.main()
