"""Adaptive generic model token quotas must be enforced on the actual API request."""
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import generic_model
from provider_monthly_quota import month_key
from provider_router import ProviderSpec


class CaptureAPI:
    requests = []

    def __init__(self, base, key):
        self.base = base

    def call(self, method, path, params, timeout_seconds=None):
        self.requests.append(params)
        return {
            "choices": [{
                "finish_reason": "stop",
                "message": {"content": '{"ok":true}'},
            }],
            "usage": {"prompt_tokens": 120, "completion_tokens": 65},
        }


class AdaptiveQuotaBudgetTests(unittest.TestCase):
    def setUp(self):
        CaptureAPI.requests = []

    def _quota(self, used):
        return {
            "schema": 1,
            "months": {month_key(): {
                "pooled": {"total_tokens": used},
            }},
        }

    def _run(self, *, used=0, quota=10000, code=False, role="product", project_cap=None, reserve=False):
        with tempfile.TemporaryDirectory() as td:
            env = {"STUDIO_PROVIDER_MONTHLY_QUOTA_PATH": str(Path(td) / "quota.json")}
            if project_cap is not None:
                env.update({
                    "STUDIO_CAPACITY_LEDGER_PATH": str(Path(td) / "ledger.json"),
                    "STUDIO_CAPACITY_PLAN_PATH": str(Path(td) / "plan.json"),
                    "STUDIO_PROJECT_ID": "p1",
                })
            provider = ProviderSpec(
                "pooled", "http://127.0.0.1:20128/v1",
                "", "auto", code_model="auto",
                monthly_token_quota=quota,
                free_preferred=True,
            )
            from contextlib import ExitStack
            with ExitStack() as stack:
                stack.enter_context(patch.dict(os.environ, env, clear=True))
                stack.enter_context(patch("generic_model.load_providers", return_value=(provider,)))
                stack.enter_context(patch("generic_model.load_provider_monthly_quota", return_value=self._quota(used)))
                stack.enter_context(patch("generic_model.load_project_envelope", return_value=project_cap))
                stack.enter_context(patch("generic_model.load_capacity_ledger", return_value={"schema":1, "consumed":{}, "reservations":{}}))
                reserve_fn = stack.enter_context(patch(
                    "generic_model.reserve_capacity",
                    return_value={"admitted": True, "reservation_id":"r1"},
                ))
                stack.enter_context(patch("generic_model.settle_capacity"))
                stack.enter_context(patch("generic_model.API", CaptureAPI))
                try:
                    result = generic_model.ask(
                        "Make valid short JSON", "Return an object with ok=true",
                        role=role, code=code,
                    )
                    error = None
                except Exception as exc:
                    result = None
                    error = exc
                return result, error, list(CaptureAPI.requests), reserve_fn.call_args

    def test_partially_used_free_quota_uses_smaller_real_max_tokens(self):
        result, error, calls, _reservation = self._run(used=6000)
        self.assertIsNone(error)
        self.assertEqual(result[0], {"ok": True})
        self.assertEqual(len(calls), 1)
        self.assertGreaterEqual(calls[0]["max_tokens"], 1024)
        self.assertLess(calls[0]["max_tokens"], 8192)
        # 4,000 remaining, 300 reserved for critical work, prompt margin.
        self.assertLess(calls[0]["max_tokens"], 3700)

    def test_small_project_envelope_reduces_requested_tokens_and_reservation(self):
        result, error, calls, reservation = self._run(used=0, project_cap=3000)
        self.assertIsNone(error)
        self.assertEqual(result[0], {"ok": True})
        self.assertLess(calls[0]["max_tokens"], 3000)
        self.assertLessEqual(reservation.kwargs["estimated_tokens"], 3000)
        prompt_estimate = max(1, (
            len("Make valid short JSON") + len("Return an object with ok=true") + 3
        ) // 4)
        prompt_margin = max(128, (prompt_estimate + 4) // 5)
        self.assertEqual(
            reservation.kwargs["estimated_tokens"],
            calls[0]["max_tokens"] + prompt_estimate + prompt_margin,
        )

    def test_true_exhaustion_never_invokes_the_provider(self):
        result, error, calls, _ = self._run(used=10000)
        self.assertIsNone(result)
        self.assertIn("No provider remains", str(error))
        self.assertEqual(calls, [])

    def test_noncritical_reserve_is_preserved_but_review_may_use_it(self):
        # Quota 10,000: remaining 1,400; 300 protected tokens.
        # Normal product output cannot meet the 1,024 minimum; review can.
        _, denied, calls, _ = self._run(used=8600, role="product")
        self.assertIsNotNone(denied)
        self.assertEqual(calls, [])
        result, error, calls, _ = self._run(used=8600, role="review")
        self.assertIsNone(error)
        self.assertEqual(result[0], {"ok": True})
        self.assertGreaterEqual(calls[0]["max_tokens"], 1024)

    def test_code_requires_bounded_minimum_and_does_not_fake_completion(self):
        result, error, calls, _ = self._run(used=7600, code=True, role="implementation")
        self.assertIsNotNone(error)
        self.assertIsNone(result)
        self.assertEqual(calls, [])


if __name__ == "__main__":
    unittest.main()
