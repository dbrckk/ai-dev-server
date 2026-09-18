import json
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from omniroute_capacity import OmniRouteCapacityError, fetch_summary, parse_summary


class _FakeResponse:
    def __init__(self, payload):
        self._payload = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self._payload


class OmniRouteCapacityTests(unittest.TestCase):
    def test_authenticated_summary_exposes_live_remaining_capacity(self):
        snapshot = parse_summary({
            "steadyRecurringTokens": 1_000_000,
            "usedThisMonth": 250_000,
            "remaining": 750_000,
            "catalogUpdatedAt": "2026-09-18",
            "catalogSource": "baseline",
        })

        self.assertEqual(snapshot.steady_recurring_tokens, 1_000_000)
        self.assertEqual(snapshot.used_this_month, 250_000)
        self.assertEqual(snapshot.remaining_tokens, 750_000)
        self.assertTrue(snapshot.authenticated_usage)
        self.assertEqual(snapshot.provider_row()["available_tokens"], 750_000)

    def test_unauthenticated_summary_fails_closed_for_scheduler_capacity(self):
        snapshot = parse_summary({
            "steadyRecurringTokens": 1_000_000,
            "usedThisMonth": None,
            "remaining": None,
            "catalogUpdatedAt": "2026-09-18",
            "catalogSource": "baseline",
        })

        self.assertFalse(snapshot.authenticated_usage)
        self.assertEqual(snapshot.provider_row()["available_tokens"], 0)
        self.assertEqual(snapshot.steady_recurring_tokens, 1_000_000)

    def test_invalid_summary_is_rejected(self):
        with self.assertRaises(OmniRouteCapacityError):
            parse_summary({"steadyRecurringTokens": -1, "usedThisMonth": 0, "remaining": 0})

    def test_fetch_summary_uses_bearer_token_and_canonical_endpoint(self):
        seen = {}

        def opener(request, timeout):
            seen["url"] = request.full_url
            seen["authorization"] = request.get_header("Authorization")
            seen["timeout"] = timeout
            return _FakeResponse({
                "steadyRecurringTokens": 100,
                "usedThisMonth": 40,
                "remaining": 60,
            })

        snapshot = fetch_summary(
            "http://127.0.0.1:20128",
            api_key="secret-token",
            timeout=3.5,
            opener=opener,
        )

        self.assertEqual(seen["url"], "http://127.0.0.1:20128/api/free-tier/summary")
        self.assertEqual(seen["authorization"], "Bearer secret-token")
        self.assertEqual(seen["timeout"], 3.5)
        self.assertEqual(snapshot.remaining_tokens, 60)


if __name__ == "__main__":
    unittest.main()
