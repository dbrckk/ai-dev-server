import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import generic_model
from provider_router import ProviderSpec
from core import APIError


class _FakeAPI:
    response = None
    error = None

    def __init__(self, base, key):
        self.base = base

    def call(self, method, path, params, timeout_seconds=None):
        if self.error is not None:
            raise self.error
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
        _FakeAPI.error = None
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
        with tempfile.TemporaryDirectory() as td, patch.dict(os.environ, {**self._env(), 'STUDIO_NATIVE_MODEL_USAGE_PATH':str(Path(td)/'usage.json')}, clear=True),              patch("generic_model.load_providers", return_value=(self._provider(),)),              patch("generic_model.load_project_envelope", return_value=50_000),              patch("generic_model.reserve_capacity", return_value=reservation) as reserve,              patch("generic_model.settle_capacity") as settle,              patch("generic_model.release_capacity") as release,              patch("generic_model.API", _FakeAPI):
            value, meta = generic_model.ask("system", "user", role="product")
            from native_model_usage import snapshot
            journal = snapshot()['usage']
            self.assertEqual((journal['runs'], journal['total_tokens'], journal['estimated_calls']), (1,150,0))
            _FakeAPI.response['usage'] = {'total_tokens': 75}
            generic_model.ask('system', 'user', role='product')
            self.assertEqual(snapshot()['usage']['total_tokens'], 225)
            self.assertEqual(snapshot()['usage']['estimated_calls'], 0)

        self.assertEqual(value, {"ok": True})
        self.assertEqual(meta["capacity"]["project_id"], "project-a")
        self.assertEqual(meta["capacity"]["project_envelope_tokens"], 50_000)
        self.assertEqual(reserve.call_count, 2)
        self.assertEqual(settle.call_count, 2)
        self.assertEqual(settle.call_args.kwargs["actual_tokens"], 75)
        release.assert_not_called()

    def test_protocol_failure_settles_consumed_tokens_without_double_release(self):
        _FakeAPI.error = None
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
        self.assertEqual(settle.call_args.kwargs["actual_tokens"], 150)
        release.assert_not_called()

    def test_transport_failure_releases_open_reservation(self):
        _FakeAPI.response = None
        _FakeAPI.error = APIError(503)
        reservation = {
            "admitted": True,
            "reservation_id": "r3",
            "reason": "reserved",
        }
        with patch.dict(os.environ, self._env(), clear=True), \
             patch("generic_model.load_providers", return_value=(self._provider(),)), \
             patch("generic_model.load_project_envelope", return_value=50_000), \
             patch("generic_model.reserve_capacity", return_value=reservation), \
             patch("generic_model.settle_capacity") as settle, \
             patch("generic_model.release_capacity") as release, \
             patch("generic_model.API", _FakeAPI):
            with self.assertRaisesRegex(Exception, "All generic-project providers failed"):
                generic_model.ask("system", "user", role="product")

        settle.assert_called_once()
        self.assertGreater(settle.call_args.kwargs['actual_tokens'], 0)
        release.assert_not_called()
        _FakeAPI.error = None

        # A 5xx keeps its conservative charge. The next provider must still
        # fit useful work into the remaining envelope instead of reusing
        # the first provider's stale 4096-token reservation.
        import json
        from capacity_ledger import load_active, consumed_tokens
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            plan = root / 'plan.json'
            ledger = root / 'ledger.json'
            plan.write_text(json.dumps({'projects': [{'id': 'small', 'token_envelope': 6000}]}))
            env = {'STUDIO_CAPACITY_PLAN_PATH': str(plan),
                   'STUDIO_CAPACITY_LEDGER_PATH': str(ledger),
                   'STUDIO_NATIVE_MODEL_USAGE_PATH': str(root / 'usage.json'),
                   'STUDIO_PROJECT_ID': 'small'}
            providers = (ProviderSpec('first', 'http://127.0.0.1:1/v1', '', 'first', priority=100, unmetered=True),
                         ProviderSpec('second', 'http://127.0.0.1:1/v1', '', 'second', priority=90, unmetered=True))
            response = {'choices': [{'finish_reason': 'stop', 'message': {'content': '{"ok":true}'}}],
                        'usage': {'prompt_tokens': 30, 'completion_tokens': 20, 'total_tokens': 50}}
            with (patch.dict(os.environ, env, clear=True),
                  patch('generic_model.load_providers', return_value=providers),
                  patch('generic_model.API', _FakeAPI),
                  patch.object(_FakeAPI, 'call', side_effect=[APIError(503), response]) as calls):
                value, meta = generic_model.ask('Return JSON.', 'Verify fallback.', code=True)
            self.assertEqual(value, {'ok': True})
            self.assertEqual(meta['provider'], 'second')
            self.assertEqual(calls.call_count, 2)
            limits = [c.args[2]['max_tokens'] for c in calls.call_args_list]
            self.assertEqual(limits[0], 4096)
            self.assertTrue(1024 <= limits[1] < limits[0])
            charged = consumed_tokens(load_active(ledger), project_id='small')
            self.assertTrue(limits[0] < charged <= 6000)

    def test_denied_reservation_skips_provider_call(self):
        _FakeAPI.response = None
        denied = {
            "admitted": False,
            "reason": "project_envelope_exhausted",
        }
        with patch.dict(os.environ, self._env(), clear=True),              patch("generic_model.load_providers", return_value=(self._provider(),)),              patch("generic_model.load_project_envelope", return_value=1),              patch("generic_model.reserve_capacity", return_value=denied),              patch("generic_model.API", _FakeAPI):
            with self.assertRaisesRegex(Exception, "project_envelope_exhausted"):
                generic_model.ask("system", "user", role="product")

        # Extend the same admission gate: an explicitly configured but missing,
        # corrupt, or unrelated project plan must never fall back to unlimited
        # capacity. No provider instance should be created in these cases.
        with tempfile.TemporaryDirectory() as td:
            plan_path = Path(td) / "capacity-plan.json"
            env = {
                **self._env(),
                "STUDIO_CAPACITY_PLAN_PATH": str(plan_path),
            }
            for content in (
                None,
                "not valid JSON",
                '{"projects":[{"id":"other-project","token_envelope":50000}]}',
            ):
                if content is None:
                    plan_path.unlink(missing_ok=True)
                else:
                    plan_path.write_text(content, encoding="utf-8")
                with patch.dict(os.environ, env, clear=True), \
                     patch("generic_model.load_providers", return_value=(self._provider(),)), \
                     patch("generic_model.API") as api:
                    with self.assertRaisesRegex(
                        Exception, "Configured project capacity plan missing or invalid"
                    ):
                        generic_model.ask("system", "user", role="product")
                    api.assert_not_called()

            # The plan exists but the project identity is missing: do not
            # silently treat the configured cap as a global unbounded mode.
            plan_path.write_text(
                '{"projects":[{"id":"project-a","token_envelope":50000}]}',
                encoding="utf-8",
            )
            with patch.dict(
                os.environ, {**env, "STUDIO_PROJECT_ID": ""}, clear=True
            ), patch(
                "generic_model.load_providers", return_value=(self._provider(),)
            ), patch("generic_model.API") as api:
                with self.assertRaisesRegex(
                    Exception, "Configured project capacity plan missing or invalid"
                ):
                    generic_model.ask("system", "user", role="product")
                api.assert_not_called()

        # No configured plan is a supported standalone/interactive mode.
        # The new fail-closed check must not require Production-OS limits
        # for unrelated local generic-model calls.
        _FakeAPI.error = None
        _FakeAPI.response = {
            "choices": [{"finish_reason": "stop", "message": {"content": '{"ok":true}'}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 4},
        }
        with patch.dict(os.environ, {}, clear=True), \
             patch("generic_model.load_providers", return_value=(self._provider(),)), \
             patch("generic_model.API", _FakeAPI):
            value, _ = generic_model.ask("system", "user", role="product")
        self.assertEqual(value, {"ok": True})


if __name__ == "__main__":
    unittest.main()
