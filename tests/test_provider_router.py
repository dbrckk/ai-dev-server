import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
STUDIO = ROOT / "studio"
if str(STUDIO) not in sys.path:
    sys.path.insert(0, str(STUDIO))

from provider_router import candidates_for, load_providers, budget_eligible, ProviderSpec


class ProviderRouterTests(unittest.TestCase):
    def test_discovered_local_capacity_becomes_provider_specs(self):
        discovered = [{
            "name": "ollama",
            "base": "http://127.0.0.1:11434/v1",
            "models": ["general", "qwen-coder"],
            "model": "general",
            "code_model": "qwen-coder",
            "vision_model": "",
            "unmetered": True,
            "monthly_token_quota": 0,
        }]
        with patch.dict(os.environ, {}, clear=True), patch(
            "provider_router.discover_local_capacity",
            return_value=discovered,
        ):
            providers = load_providers()
        self.assertEqual(
            {p.name for p in providers},
            {"ollama:general", "ollama:qwen-coder"},
        )
        coder = next(p for p in providers if p.model == "qwen-coder")
        self.assertTrue(coder.unmetered)
        self.assertEqual(coder.code_model, "qwen-coder")

    def test_autodiscovers_omniroute_only_when_no_explicit_provider_exists(self):
        auto = ProviderSpec(
            "omniroute",
            "http://127.0.0.1:20128/v1",
            "",
            "auto",
            code_model="auto",
            priority=98,
            monthly_token_quota=1_470_000_000,
        )
        with patch.dict(os.environ, {}, clear=True), patch(
            "provider_router._auto_omniroute",
            return_value=auto,
        ) as discover:
            providers = load_providers()
        discover.assert_called_once()
        self.assertEqual([p.name for p in providers], ["omniroute"])

    def test_explicit_primary_skips_omniroute_autodiscovery(self):
        env = {
            "STUDIO_API_KEY": "test-key",
            "STUDIO_API_BASE": "https://example.invalid/v1",
            "STUDIO_MODEL": "general",
        }
        with patch.dict(os.environ, env, clear=True), patch(
            "provider_router._auto_omniroute"
        ) as discover:
            providers = load_providers()
        discover.assert_not_called()
        self.assertEqual([p.name for p in providers], ["primary"])

    def test_primary_provider_is_loaded(self):
        env = {
            "STUDIO_API_KEY": "test-key",
            "STUDIO_API_BASE": "https://example.invalid/v1",
            "STUDIO_MODEL": "general",
            "STUDIO_CODE_MODEL": "coder",
            "STUDIO_VISION_MODEL": "vision",
        }
        with patch.dict(os.environ, env, clear=True):
            providers = load_providers()
        self.assertEqual(len(providers), 1)
        self.assertEqual(providers[0].model_for("implementation"), "coder")
        self.assertEqual(providers[0].model_for("visual", True), "vision")

    def test_missing_fallback_secret_skips_provider(self):
        config = [{
            "name": "fallback",
            "base": "https://fallback.invalid/v1",
            "key_env": "MISSING_KEY",
            "model": "free-model",
        }]
        with patch.dict(os.environ, {"STUDIO_PROVIDERS_JSON": json.dumps(config)}, clear=True):
            self.assertEqual(load_providers(), ())

    def test_free_fallback_can_rank_before_primary(self):
        config = [{
            "name": "free",
            "base": "https://free.invalid/v1",
            "key_env": "FREE_KEY",
            "model": "free-model",
            "priority": 10,
            "free_preferred": True,
        }]
        env = {
            "STUDIO_API_KEY": "paid-key",
            "STUDIO_PROVIDER_FREE": "false",
            "STUDIO_API_BASE": "https://paid.invalid/v1",
            "STUDIO_MODEL": "paid-model",
            "FREE_KEY": "free-key",
            "STUDIO_PROVIDERS_JSON": json.dumps(config),
        }
        with patch.dict(os.environ, env, clear=True):
            providers = load_providers(prefer_free=True)
        self.assertEqual([p.name for p in providers], ["free", "primary"])

    def test_local_endpoint_is_unmetered_by_default(self):
        env = {
            "STUDIO_API_KEY": "local-key",
            "STUDIO_API_BASE": "http://127.0.0.1:11434/v1",
            "STUDIO_MODEL": "local-model",
        }
        with patch.dict(os.environ, env, clear=True):
            providers = load_providers()
        self.assertTrue(providers[0].unmetered)

    def test_local_primary_can_be_keyless(self):
        env = {
            "STUDIO_API_BASE": "http://127.0.0.1:11434/v1",
            "STUDIO_MODEL": "qwen-local",
        }
        with patch.dict(os.environ, env, clear=True):
            providers = load_providers()
        self.assertEqual(len(providers), 1)
        self.assertEqual(providers[0].key, "")
        self.assertTrue(providers[0].unmetered)

    def test_local_json_provider_can_be_keyless(self):
        config = [{
            "name": "ollama",
            "base": "http://localhost:11434/v1",
            "model": "qwen-local",
        }]
        with patch.dict(
            os.environ,
            {"STUDIO_PROVIDERS_JSON": json.dumps(config)},
            clear=True,
        ):
            providers = load_providers()
        self.assertEqual([p.name for p in providers], ["ollama"])
        self.assertTrue(providers[0].unmetered)

    def test_remote_endpoint_is_metered_by_default(self):
        env = {
            "STUDIO_API_KEY": "remote-key",
            "STUDIO_API_BASE": "https://example.invalid/v1",
            "STUDIO_MODEL": "remote-model",
        }
        with patch.dict(os.environ, env, clear=True):
            providers = load_providers()
        self.assertFalse(providers[0].unmetered)

    def test_unmetered_can_be_explicit_for_remote_self_hosted_gateway(self):
        env = {
            "STUDIO_API_KEY": "gateway-key",
            "STUDIO_API_BASE": "https://gateway.example.invalid/v1",
            "STUDIO_MODEL": "self-hosted-model",
            "STUDIO_PROVIDER_UNMETERED": "true",
        }
        with patch.dict(os.environ, env, clear=True):
            providers = load_providers()
        self.assertTrue(providers[0].unmetered)

    def test_omniroute_endpoint_gets_current_recurring_quota_by_default(self):
        env = {
            "STUDIO_API_BASE": "http://127.0.0.1:20128/v1",
            "STUDIO_PROVIDER_NAME": "omniroute",
            "STUDIO_MODEL": "auto",
        }
        with patch.dict(os.environ, env, clear=True):
            providers = load_providers()
        self.assertEqual(providers[0].monthly_token_quota, 1_470_000_000)
        self.assertFalse(providers[0].unmetered)

    def test_paid_budget_exhaustion_keeps_pooled_free_quota_provider(self):
        providers = (
            ProviderSpec(
                "omniroute",
                "http://127.0.0.1:20128/v1",
                "",
                "auto",
                monthly_token_quota=1_470_000_000,
            ),
            ProviderSpec(
                "paid",
                "https://paid.invalid/v1",
                "k",
                "paid-model",
            ),
        )
        eligible = budget_eligible(
            providers,
            max_api_cost_usd=1.0,
            spent_api_cost_usd=1.2,
        )
        self.assertEqual([p.name for p in eligible], ["omniroute"])

    def test_paid_budget_exhaustion_keeps_only_unmetered(self):
        providers = (
            ProviderSpec(
                "local",
                "http://127.0.0.1:11434/v1",
                "k",
                "local-model",
                unmetered=True,
            ),
            ProviderSpec(
                "paid",
                "https://paid.invalid/v1",
                "k",
                "paid-model",
                unmetered=False,
            ),
        )
        eligible = budget_eligible(
            providers,
            max_api_cost_usd=1.0,
            spent_api_cost_usd=1.2,
        )
        self.assertEqual([p.name for p in eligible], ["local"])

    def test_paid_budget_not_exhausted_keeps_all(self):
        providers = (
            ProviderSpec("local", "http://127.0.0.1:11434/v1", "k", "local", unmetered=True),
            ProviderSpec("paid", "https://paid.invalid/v1", "k", "paid", unmetered=False),
        )
        eligible = budget_eligible(
            providers,
            max_api_cost_usd=1.0,
            spent_api_cost_usd=0.2,
        )
        self.assertEqual([p.name for p in eligible], ["local", "paid"])

    def test_vision_candidates_exclude_text_only_provider(self):
        config = [{
            "name": "vision",
            "base": "https://vision.invalid/v1",
            "key_env": "VISION_KEY",
            "model": "general",
            "vision_model": "vision-model",
        }]
        env = {
            "VISION_KEY": "v-key",
            "STUDIO_PROVIDERS_JSON": json.dumps(config),
        }
        with patch.dict(os.environ, env, clear=True):
            providers = load_providers()
            vision = candidates_for("visual", screenshots=True, providers=providers)
        self.assertEqual([p.name for p in vision], ["vision"])


if __name__ == "__main__":
    unittest.main()
