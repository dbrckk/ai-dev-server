import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import model_portfolio_learning as learning


class ModelPortfolioLearningTests(unittest.TestCase):
    def test_learning_requires_minimum_samples(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "portfolio.json"
            audit = {"review_independent": True, "diversity_ratio": 1.0}
            for _ in range(learning.MIN_SAMPLES - 1):
                learning.record(path, audit=audit, success=True)
            result = learning.recommendation(learning.load(path))
            self.assertIsNone(result["recommended_class"])

    def test_best_verified_portfolio_class_is_recommended(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "portfolio.json"
            independent = {"review_independent": True, "diversity_ratio": 0.8}
            same = {"review_independent": False, "diversity_ratio": 0.2}
            for _ in range(6):
                learning.record(path, audit=independent, success=True)
                learning.record(path, audit=same, success=False)
            result = learning.recommendation(learning.load(path))
            self.assertEqual(result["recommended_class"], "independent|high")

    def test_classes_are_separate(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "portfolio.json"
            learning.record(
                path,
                audit={"review_independent": True, "diversity_ratio": 0.8},
                success=True,
            )
            learning.record(
                path,
                audit={"review_independent": True, "diversity_ratio": 0.5},
                success=True,
            )
            data = learning.load(path)
            self.assertIn("independent|high", data)
            self.assertIn("independent|medium", data)


    def test_diversity_bias_is_zero_without_enough_evidence(self):
        data = {
            "independent|high": {
                "samples": learning.MIN_SAMPLES - 1,
                "successes": learning.MIN_SAMPLES - 1,
                "ema_success": 1.0,
            }
        }
        self.assertEqual(learning.diversity_bias(data), 0.0)

    def test_diversity_bias_is_bounded_by_portfolio_class(self):
        high = {
            "independent|high": {
                "samples": learning.MIN_SAMPLES,
                "successes": learning.MIN_SAMPLES,
                "ema_success": 1.0,
            }
        }
        medium = {
            "independent|medium": {
                "samples": learning.MIN_SAMPLES,
                "successes": learning.MIN_SAMPLES,
                "ema_success": 1.0,
            }
        }
        self.assertEqual(learning.diversity_bias(high), 4.0)
        self.assertEqual(learning.diversity_bias(medium), 2.0)
        self.assertLess(learning.diversity_bias(high), 10.0)


if __name__ == "__main__":
    unittest.main()
