import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import provider_cost
from contextual_utility import utility_score


class ProviderCostTests(unittest.TestCase):
    def test_estimate_call_cost(self):
        cost = provider_cost.estimate_call_cost(
            prompt_tokens=1_000_000,
            completion_tokens=500_000,
            input_cost_per_million=2.0,
            output_cost_per_million=4.0,
        )
        self.assertAlmostEqual(cost, 4.0)

    def test_record_maintains_ema_and_total(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "cost.json"
            provider_cost.record(path, "p", "implementation", 0.02)
            provider_cost.record(path, "p", "implementation", 0.06)
            row = provider_cost.load(path)["p:implementation"]
            self.assertEqual(row["calls"], 2)
            self.assertAlmostEqual(row["total_cost_usd"], 0.08)
            self.assertGreater(row["ema_cost_usd"], 0.02)
            self.assertLess(row["ema_cost_usd"], 0.06)

    def test_verified_value_per_unit_cost_drops_with_money_and_retry(self):
        cheap = utility_score(
            expected_success=0.8,
            execution_seconds=10,
            verification_seconds=30,
            architecture_hold=False,
            monetary_cost_usd=0.0,
            retry_probability=0.1,
        )
        expensive = utility_score(
            expected_success=0.8,
            execution_seconds=10,
            verification_seconds=30,
            architecture_hold=False,
            monetary_cost_usd=0.10,
            retry_probability=0.6,
        )
        self.assertGreater(
            cheap["verified_value_per_unit_cost"],
            expensive["verified_value_per_unit_cost"],
        )
        self.assertGreater(cheap["score"], expensive["score"])


if __name__ == "__main__":
    unittest.main()
