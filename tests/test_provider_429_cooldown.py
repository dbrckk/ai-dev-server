"""A 429 should open the transient provider circuit after HTTP transport retries."""
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import generic_model
from core import APIError, Model
from provider_health import eligible, load as load_health
from provider_router import ProviderSpec


class _ProviderAPI:
    calls = []
    bad_status = 429

    def __init__(self, base, key):
        self.base = base

    def call(self, method, path, params, timeout_seconds=None):
        self.calls.append(self.base)
        if self.base.endswith("/bad"):
            raise APIError(self.bad_status)
        return {
            "choices": [{
                "finish_reason": "stop",
                "message": {"content": '{"ok":true}'},
            }],
            "usage": {"prompt_tokens": 30, "completion_tokens": 12},
        }


def _providers():
    return (
        ProviderSpec(
            name="rate-limited", base="https://model.invalid/bad", key="fake",
            model="model-a", priority=100, free_preferred=True,
        ),
        ProviderSpec(
            name="fallback", base="https://model.invalid/good", key="fake",
            model="model-b", priority=1, free_preferred=True,
        ),
    )


class Provider429CooldownTests(unittest.TestCase):
    def setUp(self):
        _ProviderAPI.calls = []
        _ProviderAPI.bad_status = 429

    def test_generic_model_uses_fallback_and_skips_429_provider_next_call(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "health.json"
            with (
                patch.dict(os.environ, {"STUDIO_PROVIDER_HEALTH_PATH": str(path)}, clear=True),
                patch("generic_model.load_providers", return_value=_providers()),
                patch("generic_model.API", _ProviderAPI),
            ):
                result, metadata = generic_model.ask("system", "user", role="product")
                self.assertEqual(result, {"ok": True})
                self.assertEqual(metadata["provider"], "fallback")
                self.assertEqual(_ProviderAPI.calls, [
                    "https://model.invalid/bad", "https://model.invalid/good",
                ])
                self.assertFalse(eligible(path, "rate-limited"))
                self.assertTrue(eligible(path, "fallback"))
                self.assertEqual(load_health(path)["rate-limited"]["consecutive_failures"], 1)

                again, metadata = generic_model.ask("system", "user", role="product")
                self.assertEqual(again, {"ok": True})
                self.assertEqual(metadata["provider"], "fallback")
                self.assertEqual(_ProviderAPI.calls[-1], "https://model.invalid/good")
                self.assertEqual(_ProviderAPI.calls.count("https://model.invalid/bad"), 1)

    def test_generic_server_error_preserves_standard_three_failure_threshold(self):
        _ProviderAPI.bad_status = 503
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "health.json"
            with (
                patch.dict(os.environ, {"STUDIO_PROVIDER_HEALTH_PATH": str(path)}, clear=True),
                patch("generic_model.load_providers", return_value=_providers()),
                patch("generic_model.API", _ProviderAPI),
            ):
                result, _ = generic_model.ask("system", "user", role="product")
            self.assertEqual(result, {"ok": True})
            self.assertTrue(eligible(path, "rate-limited"))
            self.assertEqual(load_health(path)["rate-limited"]["consecutive_failures"], 1)

    def test_flutter_model_provider_cooldown_and_independent_fallback(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "health.json"
            with (
                patch.dict(os.environ, {"STUDIO_PROVIDER_HEALTH_PATH": str(path)}, clear=True),
                patch("provider_router.load_providers", return_value=_providers()),
                patch("core.API", _ProviderAPI),
            ):
                model = Model(limit=4)
                result = model._ask("product", "Return JSON", ())
                self.assertEqual(result, {"ok": True})
                self.assertFalse(eligible(path, "rate-limited"))
                self.assertIn("https://model.invalid/good", _ProviderAPI.calls)
                before = _ProviderAPI.calls.count("https://model.invalid/bad")
                self.assertEqual(model._ask("product", "Return JSON", ()), {"ok": True})
                self.assertEqual(_ProviderAPI.calls.count("https://model.invalid/bad"), before)


if __name__ == "__main__":
    unittest.main()
