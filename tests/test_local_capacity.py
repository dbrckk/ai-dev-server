import json
import os
import unittest
from pathlib import Path
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import local_capacity


class LocalCapacityTests(unittest.TestCase):
    def _response(self, payload):
        response = MagicMock()
        response.status = 200
        response.read.return_value = json.dumps(payload).encode()
        response.__enter__.return_value = response
        response.__exit__.return_value = False
        return response

    def test_probe_selects_code_and_vision_models(self):
        payload = {
            "data": [
                {"id": "general-model"},
                {"id": "qwen-coder-32b"},
                {"id": "qwen3-vl"},
            ]
        }
        with patch("urllib.request.urlopen", return_value=self._response(payload)):
            result = local_capacity.probe_gateway(
                "ollama",
                "http://127.0.0.1:11434/v1",
                0,
            )
        self.assertEqual(result["code_model"], "qwen-coder-32b")
        self.assertEqual(result["vision_model"], "qwen3-vl")
        self.assertTrue(result["unmetered"])

    def test_omniroute_is_pooled_free_not_unmetered(self):
        payload = {"data": [{"id": "auto"}]}
        with patch("urllib.request.urlopen", return_value=self._response(payload)):
            result = local_capacity.probe_gateway(
                "omniroute",
                "http://127.0.0.1:20128/v1",
                1_470_000_000,
            )
        self.assertFalse(result["unmetered"])
        self.assertEqual(result["monthly_token_quota"], 1_470_000_000)

    def test_invalid_model_envelope_is_ignored(self):
        with patch(
            "urllib.request.urlopen",
            return_value=self._response({"models": []}),
        ):
            result = local_capacity.probe_gateway(
                "vllm",
                "http://127.0.0.1:8000/v1",
            )
        self.assertIsNone(result)

    def test_autodiscovery_can_be_disabled(self):
        with patch.dict(
            os.environ,
            {"STUDIO_AUTO_DISCOVER_LOCAL_CAPACITY": "false"},
            clear=True,
        ):
            self.assertEqual(local_capacity.discover(), [])


if __name__ == "__main__":
    unittest.main()
