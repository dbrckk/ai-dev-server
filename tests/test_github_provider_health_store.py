"""The remote store must accept the health records written during real inference."""

import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from studio import github_provider_health_store as store
from studio.provider_health import record_failure, record_success


class ProviderHealthPersistenceTests(unittest.TestCase):
    def test_real_inference_record_can_be_persisted_without_losing_routing_history(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "provider-health.json"
            record_success(path, "nvidia/model", latency_ms=250.0)
            record_failure(path, "nvidia/model", latency_ms=350.0)
            with patch.object(store, "save", side_effect=lambda _github, data: data) as save:
                persisted = store.persist_local(object(), path)
            save.assert_called_once()
            row = persisted["nvidia/model"]
            self.assertEqual(row["successes"], 1)
            self.assertEqual(row["failures"], 1)
            self.assertEqual(row["recent_outcomes"], [1, 0])
            self.assertGreater(row["latency_ms_ema"], 250)
            self.assertGreater(row["last_observed_at"], 0)

    def test_legacy_remote_row_gains_safe_defaults(self):
        legacy = {"model": {"successes": 2, "failures": 1,
                            "consecutive_failures": 0, "opened_until": 0.0}}
        row = store._validate(legacy)["model"]
        self.assertIsNone(row["latency_ms_ema"])
        self.assertEqual(row["last_observed_at"], 0.0)
        self.assertEqual(row["recent_outcomes"], [])

    def test_unexpected_or_invalid_observations_are_rejected(self):
        row = {"successes": 1, "failures": 0, "consecutive_failures": 0,
               "opened_until": 0.0, "latency_ms_ema": 10.0,
               "last_observed_at": 100.0, "recent_outcomes": [1]}
        for changes in ({"credential": "private"}, {"latency_ms_ema": math.inf},
                        {"last_observed_at": -1}, {"recent_outcomes": [True]}):
            with self.subTest(changes=changes):
                with self.assertRaises(store.ProviderHealthStoreError):
                    store._validate({"model": {**row, **changes}})


if __name__ == "__main__":
    unittest.main()
