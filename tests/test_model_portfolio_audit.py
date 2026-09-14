import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from model_portfolio_audit import audit


class ModelPortfolioAuditTests(unittest.TestCase):
    def test_independent_review_is_detected(self):
        result = audit({
            "implementation": {"provider": "a", "model": "impl"},
            "review": {"provider": "b", "model": "review"},
            "product": {"provider": "c", "model": "plan"},
        })
        self.assertTrue(result["review_independent"])
        self.assertEqual(result["unique_providers"], 3)
        self.assertEqual(result["diversity_ratio"], 1.0)

    def test_same_review_identity_is_detected(self):
        result = audit({
            "implementation": {"provider": "a", "model": "same"},
            "review": {"provider": "a", "model": "same"},
        })
        self.assertFalse(result["review_independent"])
        self.assertEqual(result["diversity_ratio"], 0.5)

    def test_empty_portfolio_is_safe(self):
        result = audit({})
        self.assertEqual(result["roles_observed"], 0)
        self.assertIsNone(result["review_independent"])


if __name__ == "__main__":
    unittest.main()
