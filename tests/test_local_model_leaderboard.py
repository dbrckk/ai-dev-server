import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from local_model_leaderboard import leaderboards


class LocalModelLeaderboardTests(unittest.TestCase):
    def test_best_specialist_ranks_first(self):
        data = {
            "ollama|python-good|implementation|stack:python": {
                "samples": 8,
                "successes": 8,
                "ema_verified_success": 0.95,
            },
            "ollama|python-mid|implementation|stack:python": {
                "samples": 8,
                "successes": 5,
                "ema_verified_success": 0.65,
            },
        }
        result = leaderboards(data)
        rows = result["contexts"]["stack:python"]
        self.assertEqual(rows[0]["model"], "python-good")
        self.assertGreater(rows[0]["specialist_score"], rows[1]["specialist_score"])

    def test_low_sample_rows_are_hidden(self):
        data = {
            "ollama|new-model|implementation|stack:flutter": {
                "samples": 1,
                "successes": 1,
                "ema_verified_success": 1.0,
            }
        }
        result = leaderboards(data, min_samples=3)
        self.assertEqual(result["context_count"], 0)

    def test_contexts_are_independent(self):
        data = {
            "ollama|a|implementation|stack:python": {
                "samples": 6,
                "successes": 6,
                "ema_verified_success": 0.9,
            },
            "ollama|b|implementation|stack:flutter": {
                "samples": 6,
                "successes": 6,
                "ema_verified_success": 0.9,
            },
        }
        result = leaderboards(data)
        self.assertIn("stack:python", result["contexts"])
        self.assertIn("stack:flutter", result["contexts"])


if __name__ == "__main__":
    unittest.main()
