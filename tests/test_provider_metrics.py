from pathlib import Path
import tempfile
import unittest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from provider_metrics import latency_bonus, load, record


class ProviderMetricsTests(unittest.TestCase):
    def test_latency_ema_is_role_scoped(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "metrics.json"
            record(path, "p", "product", 2.0)
            record(path, "p", "product", 6.0)
            record(path, "p", "implementation", 20.0)
            data = load(path)
            self.assertEqual(data["p:product"]["calls"], 2)
            self.assertAlmostEqual(data["p:product"]["ema_latency_seconds"], 3.0)
            self.assertEqual(data["p:implementation"]["calls"], 1)

    def test_latency_bonus_rewards_fast_and_penalizes_slow(self):
        fast = {"p:product": {"calls": 3, "ema_latency_seconds": 1.5}}
        slow = {"p:product": {"calls": 3, "ema_latency_seconds": 80.0}}
        self.assertGreater(latency_bonus(fast, "p", "product"), 0)
        self.assertLess(latency_bonus(slow, "p", "product"), 0)
        self.assertEqual(latency_bonus({}, "p", "product"), 0.0)


if __name__ == "__main__":
    unittest.main()
