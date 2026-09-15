import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import provider_health


class ProviderScopedHealthTests(unittest.TestCase):
    def test_scoped_result_updates_global_and_specialized_health(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "health.json"
            provider_health.record_scoped_verified_result(
                path,
                "p",
                model="m",
                role="implementation",
                verified_success=True,
                latency_ms=100,
            )
            data = provider_health.load(path)
            self.assertEqual(data["p"]["successes"], 1)
            self.assertEqual(data["p|model=m|role=implementation"]["successes"], 1)

    def test_scoped_reliability_prefers_specialization(self):
        data = {
            "p": {"successes": 9, "failures": 1},
            "p|model=m|role=implementation": {"successes": 1, "failures": 3},
        }
        self.assertAlmostEqual(
            provider_health.scoped_reliability(
                data, "p", model="m", role="implementation"
            ),
            2 / 6,
        )

    def test_scoped_evidence_decays_after_one_half_life(self):
        data = {
            "p|model=m|role=implementation": {
                "successes": 90,
                "failures": 10,
                "last_observed_at": 1000.0,
            }
        }
        fresh = provider_health.scoped_evidence(
            data, "p", model="m", role="implementation",
            now=1000.0, half_life_seconds=100.0,
        )
        stale = provider_health.scoped_evidence(
            data, "p", model="m", role="implementation",
            now=1100.0, half_life_seconds=100.0,
        )
        self.assertEqual(fresh["freshness"], 1.0)
        self.assertAlmostEqual(stale["freshness"], 0.5)
        self.assertAlmostEqual(stale["confidence"], fresh["confidence"] * 0.5)

    def test_legacy_health_without_timestamp_keeps_full_freshness(self):
        evidence = provider_health.scoped_evidence(
            {"p": {"successes": 5, "failures": 1}},
            "p",
            now=999999.0,
        )
        self.assertEqual(evidence["freshness"], 1.0)

    def test_scoped_reliability_falls_back_to_provider(self):
        data = {"p": {"successes": 3, "failures": 1}}
        self.assertAlmostEqual(
            provider_health.scoped_reliability(
                data, "p", model="unknown", role="review"
            ),
            4 / 6,
        )


if __name__ == "__main__":
    unittest.main()
