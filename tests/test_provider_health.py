from pathlib import Path
import tempfile
import unittest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from provider_health import eligible, load, record_failure, record_success, reliability_bonus


class ProviderHealthTests(unittest.TestCase):
    def test_three_failures_open_circuit_and_success_resets_it(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "provider-health.json"
            for _ in range(2):
                record_failure(path, "p1", threshold=3, cooldown_seconds=60, now=100.0)
                self.assertTrue(eligible(path, "p1", now=100.0))
            record_failure(path, "p1", threshold=3, cooldown_seconds=60, now=100.0)
            self.assertFalse(eligible(path, "p1", now=120.0))
            self.assertTrue(eligible(path, "p1", now=161.0))
            record_success(path, "p1")
            row = load(path)["p1"]
            self.assertEqual(row["consecutive_failures"], 0)
            self.assertEqual(row["opened_until"], 0.0)

    def test_corrupt_state_fails_open_without_crashing(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "provider-health.json"
            path.write_text("{not-json")
            self.assertTrue(eligible(path, "p1", now=100.0))
            data = record_failure(path, "p1", threshold=1, cooldown_seconds=10, now=100.0)
            self.assertEqual(data["p1"]["failures"], 1)
            self.assertFalse(eligible(path, "p1", now=105.0))

    def test_backoff_grows_exponentially_after_threshold(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "provider-health.json"
            for _ in range(3):
                record_failure(path, "p1", threshold=3, cooldown_seconds=10, now=100.0)
            self.assertEqual(load(path)["p1"]["opened_until"], 110.0)
            record_failure(path, "p1", threshold=3, cooldown_seconds=10, now=100.0)
            self.assertEqual(load(path)["p1"]["opened_until"], 120.0)
            record_failure(path, "p1", threshold=3, cooldown_seconds=10, now=100.0)
            self.assertEqual(load(path)["p1"]["opened_until"], 140.0)

    def test_reliability_bonus_is_bounded_and_prefers_success(self):
        good = {"p": {"successes": 9, "failures": 1, "consecutive_failures": 0, "opened_until": 0.0}}
        bad = {"p": {"successes": 1, "failures": 9, "consecutive_failures": 2, "opened_until": 0.0}}
        self.assertGreater(reliability_bonus(good, "p"), 0)
        self.assertLess(reliability_bonus(bad, "p"), 0)
        self.assertLessEqual(reliability_bonus(good, "p"), 30.0)
        self.assertGreaterEqual(reliability_bonus(bad, "p"), -30.0)

    def test_provider_rows_never_persist_sensitive_details(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "provider-health.json"
            record_failure(path, "provider", threshold=1, cooldown_seconds=10, now=100.0)
            raw = path.read_text()
            self.assertNotIn("error", raw.lower())
            self.assertNotIn("token", raw.lower())
            self.assertEqual(
                set(load(path)["provider"]),
                {"successes", "failures", "consecutive_failures", "opened_until"},
            )


if __name__ == "__main__":
    unittest.main()
