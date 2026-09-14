import os
import unittest
from pathlib import Path
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import generic_model
from provider_router import ProviderSpec


class _FakeAPI:
    response = None

    def __init__(self, base, key):
        self.base = base

    def call(self, method, path, params, timeout_seconds=None):
        return self.response


class GenericModelCapacityTests(unittest.TestCase):
    def _provider(self):
        return ProviderSpec(
            "omniroute",
            "http://127.0.0.1:20128/v1",
            "",
            "auto",
            code_model="auto",
            monthly_token_quota=1_000_000,
        )

    def _env(self):
        return {
            "STUDIO_CAPACITY_LEDGER_PATH": "/tmp/capacity-ledger-test.json",
            "STUDIO_CAPACITY_PLAN_PATH": "/tmp/capacity-plan-test.json",
            "STUDIO_PROJECT_ID": "project-a",
        }

    def test_success_settles_transactional_reservation_with_actual_usage(self):
        _FakeAPI.response = {
            "choices": [{
                "finish_reason": "stop",
                "message": {"content": '{"ok": true}'},
            }],
            "usage": {"prompt_tokens": 100, "completion_tokens": 50},
        }
        reservation = {
            "admitted": True,
            "reservation_id": "r1",
            "reason": "reserved",
        }
        with patch.dict(os.environ, self._env(), clear=True),              patch("generic_model.load_providers", return_value=(self._provider(),)),              patch("generic_model.load_project_envelope", return_value=50_000),              patch("generic_model.reserve_capacity", return_value=reservation) as reserve,              patch("generic_model.settle_capacity") as settle,              patch("generic_model.release_capacity") as release,              patch("generic_model.API", _FakeAPI):
            value, meta = generic_model.ask("system", "user", role="product")

        self.assertEqual(value, {"ok": True})
        self.assertEqual(meta["capacity"]["project_id"], "project-a")
        self.assertEqual(meta["capacity"]["project_envelope_tokens"], 50_000)
        reserve.assert_called_once()
        settle.assert_called_once()
        self.assertEqual(settle.call_args.kwargs["actual_tokens"], 150)
        release.assert_not_called()

    def test_protocol_failure_releases_transactional_reservation(self):
        _FakeAPI.response = {
            "choices": [{
                "finish_reason": "stop",
                "message": {"content": "not-json"},
            }],
            "usage": {"prompt_tokens": 100, "completion_tokens": 50},
        }
        reservation = {
            "admitted": True,
            "reservation_id": "r2",
            "reason": "reserved",
        }
        with patch.dict(os.environ, self._env(), clear=True),              patch("generic_model.load_providers", return_value=(self._provider(),)),              patch("generic_model.load_project_envelope", return_value=50_000),              patch("generic_model.reserve_capacity", return_value=reservation),              patch("generic_model.settle_capacity") as settle,              patch("generic_model.release_capacity") as release,              patch("generic_model.API", _FakeAPI):
            with self.assertRaisesRegex(Exception, "All generic-project providers failed"):
                generic_model.ask("system", "user", role="product")

        settle.assert_called_once()
        release.assert_called_once_with(
            Path("/tmp/capacity-ledger-test.json"),
            "r2",
        )

    def test_denied_reservation_skips_provider_call(self):
        _FakeAPI.response = None
        denied = {
            "admitted": False,
            "reason": "project_envelope_exhausted",
        }
        with patch.dict(os.environ, self._env(), clear=True),              patch("generic_model.load_providers", return_value=(self._provider(),)),              patch("generic_model.load_project_envelope", return_value=1),              patch("generic_model.reserve_capacity", return_value=denied),              patch("generic_model.API", _FakeAPI):
            with self.assertRaisesRegex(Exception, "project_envelope_exhausted"):
                generic_model.ask("system", "user", role="product")


if __name__ == "__main__":
    unittest.main()
