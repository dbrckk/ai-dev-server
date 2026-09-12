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

from provider_router import candidates_for, load_providers


class ProviderRouterTests(unittest.TestCase):
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
