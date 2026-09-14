import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import provider_monthly_quota as quota


class ProviderMonthlyQuotaTests(unittest.TestCase):
    def test_records_tokens_in_current_month(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "quota.json"
            now = datetime(2026, 9, 14, tzinfo=timezone.utc)
            quota.record(path, "omniroute", prompt_tokens=100, completion_tokens=50, now=now)
            quota.record(path, "omniroute", prompt_tokens=25, completion_tokens=25, now=now)
            status = quota.quota_status(path, "omniroute", 1000, now=now)
            self.assertEqual(status["used_tokens"], 200)
            self.assertEqual(status["remaining_tokens"], 800)
            self.assertFalse(status["exhausted"])

    def test_month_rollover_resets_usage_view(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "quota.json"
            september = datetime(2026, 9, 30, tzinfo=timezone.utc)
            october = datetime(2026, 10, 1, tzinfo=timezone.utc)
            quota.record(path, "omniroute", prompt_tokens=900, completion_tokens=100, now=september)
            self.assertEqual(
                quota.quota_status(path, "omniroute", 1000, now=september)["used_tokens"],
                1000,
            )
            self.assertEqual(
                quota.quota_status(path, "omniroute", 1000, now=october)["used_tokens"],
                0,
            )

    def test_exhaustion_is_enforced(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "quota.json"
            now = datetime(2026, 9, 14, tzinfo=timezone.utc)
            quota.record(path, "omniroute", prompt_tokens=800, completion_tokens=250, now=now)
            status = quota.quota_status(path, "omniroute", 1000, now=now)
            self.assertTrue(status["exhausted"])
            self.assertEqual(status["remaining_tokens"], 0)


if __name__ == "__main__":
    unittest.main()
