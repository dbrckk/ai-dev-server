import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import provider_health


class ProviderVerifiedFeedbackTests(unittest.TestCase):
    def test_verified_success_updates_reliability_and_latency(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "health.json"
            provider_health.record_verified_result(
                path, "p", verified_success=True, latency_ms=120,
            )
            snapshot = provider_health.health_snapshot(path, now=0)
            self.assertEqual(snapshot["p"]["observations"], 1)
            self.assertAlmostEqual(snapshot["p"]["reliability"], 2 / 3, places=6)
            self.assertEqual(snapshot["p"]["latency_ms_ema"], 120.0)
            self.assertFalse(snapshot["p"]["circuit_open"])

    def test_verified_failures_open_circuit(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "health.json"
            for _ in range(3):
                provider_health.record_verified_result(
                    path,
                    "p",
                    verified_success=False,
                    latency_ms=500,
                    threshold=3,
                    cooldown_seconds=60,
                    now=100,
                )
            snapshot = provider_health.health_snapshot(path, now=100)
            self.assertEqual(snapshot["p"]["failures"], 3)
            self.assertTrue(snapshot["p"]["circuit_open"])
            self.assertEqual(snapshot["p"]["opened_until"], 160.0)

    def test_unverified_non_boolean_outcome_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "health.json"
            with self.assertRaises(ValueError):
                provider_health.record_verified_result(
                    path, "p", verified_success=1,
                )


if __name__ == "__main__":
    unittest.main()
