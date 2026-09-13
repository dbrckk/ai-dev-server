from pathlib import Path
import tempfile
import unittest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from provider_health import eligible, load, record_failure, record_success


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
