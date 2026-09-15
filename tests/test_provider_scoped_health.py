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
