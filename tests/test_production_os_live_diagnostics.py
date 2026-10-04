import json
import unittest
from unittest.mock import patch

from core import APIError, StudioError
from production_os_live_diagnostics import diagnose
from production_os_provider_config import configure
from provider_router import ProviderSpec


class LiveDiagnosticsTests(unittest.TestCase):
    def test_provider_fallback_recovers_gone_model_and_output_excludes_secrets(self):
        calls = []
        providers = [ProviderSpec('gone', 'https://provider.example/v1', 'credential', 'old'),
                     ProviderSpec('ready', 'https://provider.example/v1', 'credential', 'new')]
        class FakeAPI:
            def __init__(self, base, key):
                pass
            def call(self, method, path, data=None, **kwargs):
                calls.append((method, path, data, kwargs))
                if data and data['model'] == 'old':
                    raise APIError(410)
                return {'choices': [{'message': {'content': '{"ready":true,"private":"credential remote text"}'}}]}
        result = diagnose(api_factory=FakeAPI, providers=providers, environ={})
        self.assertTrue(result['inference_ready'])
        self.assertEqual(result['providers'][0]['http_status'], 410)
        self.assertEqual(len(calls), 2)
        self.assertTrue(all(c[0:2] == ('POST', '/chat/completions') for c in calls))
        self.assertNotIn('credential', json.dumps(result))

    def test_invalid_or_empty_completions_and_failed_coding_model_are_not_ready(self):
        provider = ProviderSpec('p', 'https://provider.example/v1', 'key', 'product', code_model='code')
        class FakeAPI:
            def __init__(self, *args):
                pass
            def call(self, method, path, data, **kwargs):
                if data['model'] == 'code':
                    raise StudioError('sensitive exception')
                return {'choices': [{'message': {'content': '{"ready":true}'}}]}
        result = diagnose(api_factory=FakeAPI, providers=[provider], environ={})
        self.assertFalse(result['inference_ready'])
        self.assertNotIn('sensitive', json.dumps(result))
        for response in ({}, {'choices': []}, {'choices': [{'message': {'content': ''}}]}):
            with patch.object(FakeAPI, 'call', return_value=response):
                self.assertFalse(diagnose(api_factory=FakeAPI, providers=[provider], environ={})['inference_ready'])

    def test_operator_probe_is_read_only_and_no_token_is_reported(self):
        calls = []
        class FakeAPI:
            def __init__(self, base, key):
                self.key = key
            def call(self, *args, **kwargs):
                calls.append((args, kwargs))
                raise APIError(403)
        result = diagnose(api_factory=FakeAPI, providers=[], environ={
            'PRODUCTION_OS_URL': 'https://control.example', 'PRODUCTION_OS_OPERATOR_TOKEN': 'operator-secret'})
        self.assertEqual(result['operator_http_status'], 403)
        self.assertEqual(calls, [(('GET', '/v1/dashboard/device-sessions'), {'timeout_seconds': 10})])
        self.assertNotIn('operator-secret', json.dumps(result))

    def test_defaults_preserve_explicit_configuration_and_other_providers(self):
        env = {'STUDIO_API_BASE': 'https://integrate.api.nvidia.com/v1/'}
        self.assertTrue(configure(env))
        models = [p['model'] for p in json.loads(env['STUDIO_PROVIDERS_JSON'])]
        self.assertEqual(models, ['nvidia/nemotron-3.5-lightning-30b-a3b', 'poolside/laguna-xs-2.1'])
        for env in ({'STUDIO_API_BASE': 'https://another.example/v1'},
                    {'STUDIO_API_BASE': 'https://integrate.api.nvidia.com/v1', 'STUDIO_PROVIDERS_JSON': '[]'}):
            before = dict(env)
            self.assertFalse(configure(env))
            self.assertEqual(env, before)
