import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from model_portfolio import choose


class ModelPortfolioTests(unittest.TestCase):
    def test_review_avoids_implementation_identity_when_possible(self):
        ranked = {
            "implementation": [
                {"provider": "ollama:qwen", "model": "qwen", "score": 20.0},
            ],
            "review": [
                {"provider": "ollama:qwen", "model": "qwen", "score": 30.0},
                {"provider": "omniroute", "model": "reviewer", "score": 25.0},
            ],
        }
        portfolio = choose(
            ranked,
            implementation_provider="ollama:qwen",
            implementation_model="qwen",
        )
        self.assertEqual(portfolio["roles"]["review"]["provider"], "omniroute")

    def test_review_falls_back_if_no_independent_candidate_exists(self):
        ranked = {
            "review": [
                {"provider": "ollama:qwen", "model": "qwen", "score": 30.0},
            ],
        }
        portfolio = choose(
            ranked,
            implementation_provider="ollama:qwen",
            implementation_model="qwen",
        )
        self.assertEqual(portfolio["roles"]["review"]["provider"], "ollama:qwen")

    def test_non_review_role_keeps_top_candidate(self):
        ranked = {
            "product": [
                {"provider": "a", "model": "planner-a", "score": 12.0},
                {"provider": "b", "model": "planner-b", "score": 11.0},
            ],
        }
        portfolio = choose(ranked)
        self.assertEqual(portfolio["roles"]["product"]["provider"], "a")

    def test_visual_also_prefers_independent_identity(self):
        ranked = {
            "visual": [
                {"provider": "impl", "model": "same", "score": 50.0},
                {"provider": "vision", "model": "vl", "score": 40.0},
            ],
        }
        portfolio = choose(
            ranked,
            implementation_provider="impl",
            implementation_model="same",
        )
        self.assertEqual(portfolio["roles"]["visual"]["provider"], "vision")


if __name__ == "__main__":
    unittest.main()
