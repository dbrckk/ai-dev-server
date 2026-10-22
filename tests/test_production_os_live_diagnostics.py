import json
import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from core import APIError, StudioError
from production_os_live_diagnostics import diagnose, main, _safe_increment_source
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
                if (data and data['model'] == 'nvidia/nemotron-3.5-lightning-30b-a3b'
                        and data.get('chat_template_kwargs') != {'enable_thinking': False}):
                    return {'choices': [{'finish_reason': 'length', 'message': {'content': ''}}]}
                if (data and data['model'] == 'poolside/laguna-xs-2.1'
                        and 'Write only Python code' in data['messages'][0]['content']):
                    raise APIError(503)
                if data and 'Write only Python code' in data['messages'][0]['content']:
                    return {'choices': [{'message': {'content': 'def increment(value):\n    return value + 1\n'}}]}
                return {'choices': [{'message': {'content': '{"ready":true,"private":"credential remote text"}'}}]}
        result = diagnose(api_factory=FakeAPI, providers=providers, environ={})
        self.assertTrue(result['inference_ready'])
        self.assertEqual(result['providers'][0]['http_status'], 410)
        self.assertEqual(len(calls), 2)
        self.assertTrue(all(c[0:2] == ('POST', '/chat/completions') for c in calls))
        self.assertNotIn('credential', json.dumps(result))
        self.assertEqual(result['providers'][0]['provider_family'], 'other')
        smoke = diagnose(api_factory=FakeAPI, providers=providers,
                         environ={'PRODUCTION_OS_DIAGNOSE_CODE_SMOKE': '1'})
        self.assertEqual(smoke['coding_smoke']['status'], 'ready')
        self.assertEqual(smoke['coding_smoke']['provider_index'], 1)
        self.assertNotIn('credential', json.dumps(smoke))

        # A healthy readiness response does not guarantee the code endpoint.
        # Match native fallback within the ORIGINAL 384-token output ceiling.
        nim_base = 'https://integrate.api.nvidia.com/v1'
        nim = [ProviderSpec('laguna', nim_base, 'credential', 'poolside/laguna-xs-2.1'),
               ProviderSpec('lightning', nim_base, 'credential', 'nvidia/nemotron-3.5-lightning-30b-a3b')]
        calls.clear()
        recovered = diagnose(api_factory=FakeAPI, providers=nim,
                             environ={'PRODUCTION_OS_DIAGNOSE_CODE_SMOKE': '1'})
        self.assertTrue(recovered['inference_ready'])
        self.assertEqual([p['status'] for p in recovered['providers']], ['ready', 'ready'])
        self.assertEqual(recovered['coding_smoke']['status'], 'ready')
        self.assertEqual(recovered['coding_smoke']['provider_index'], 1)
        self.assertEqual(recovered['coding_smoke']['attempts'][0]['http_status'], 503)
        code_calls = [c for c in calls if 'Write only Python code' in c[2]['messages'][0]['content']]
        self.assertEqual(len(code_calls), 2)
        self.assertLessEqual(sum(c[2]['max_tokens'] for c in code_calls), 384)
        self.assertTrue(all(c[3]['max_attempts'] == 1 for c in code_calls))
        self.assertNotIn('credential', json.dumps(recovered))

        # Each candidate is tried once, sharing a deadline, not 40s each.
        calls.clear()
        with patch('production_os_live_diagnostics.time.monotonic', side_effect=[0, 0, 40]):
            exhausted = diagnose(api_factory=FakeAPI, providers=nim,
                                 environ={'PRODUCTION_OS_DIAGNOSE_CODE_SMOKE': '1'})
        self.assertEqual(exhausted['coding_smoke']['status'], 'unavailable')
        self.assertEqual(len(exhausted['coding_smoke']['attempts']), 1)
        self.assertEqual(exhausted['coding_smoke']['attempts'][0]['http_status'], 503)
        self.assertEqual(len([c for c in calls if 'Write only Python code' in c[2]['messages'][0]['content']]), 1)
        self.assertNotIn('credential', json.dumps(exhausted))

        # The real public gateway reports costs inside usage, including
        # separate upstream fields. None may be ignored in a free-code proof.
        import tempfile
        from pathlib import Path
        import public_free_code_smoke as public_smoke
        catalog = {"data": [{"id": public_smoke.MODEL, "isFree": True,
                             "pricing": {"prompt": "0", "completion": "0"}}]}
        cases = (
            ({"usage": {"market_cost": 0}}, True),
            ({"usage": {"cost": "0", "cost_details": {"upstream_inference_cost": 0}}}, True),
            ({"usage": {"market_cost": 0.01}}, False),
            ({"market_cost": 0, "usage": {"cost": 0.01}}, False),
            ({"usage": {"cost": 0, "cost_details": {"upstream_inference_completions_cost": 0.01}}}, False),
            ({"usage": {"cost": False}}, False),
            ({"usage": {"cost": "NaN"}}, False),
            ({"usage": {"cost": None}}, False),
        )
        for cost_fields, passed in cases:
            with self.subTest(cost_fields=cost_fields), tempfile.TemporaryDirectory() as tmp:
                output = Path(tmp) / "report.json"
                response = {"choices": [{"message": {"content": 'def increment(value):\n    return value + 1'}}], **cost_fields}
                with patch.object(public_smoke, "OUTPUT", output), patch.object(public_smoke, "API") as api, redirect_stdout(io.StringIO()):
                    api.return_value.call.side_effect = [catalog, response]
                    self.assertEqual(public_smoke.run(), 0 if passed else 1)
                    self.assertEqual(api.return_value.call.call_count, 2)
                    live_call = api.return_value.call.call_args_list[1]
                    self.assertEqual(live_call.args[:2], ('POST', '/chat/completions'))
                    self.assertEqual(live_call.args[2]['max_tokens'], 1024)
                    self.assertEqual(live_call.kwargs['max_attempts'], 1)
                report = json.loads(output.read_text())
                self.assertEqual(report["code_verified"], passed)
                self.assertTrue(report["cost_reported"])
                self.assertEqual(report.get("reported_zero_cost", False), passed)
        catalog["data"][0]["pricing"]["prompt"] = False
        self.assertFalse(public_smoke._catalog_confirms_zero_cost(catalog))

    def test_invalid_or_empty_completions_and_failed_coding_model_are_not_ready(self):
        self.assertTrue(_safe_increment_source('def increment(value):\n    return value + 1'))
        for unsafe in ('__import__("os").system("id")',
                       'def increment(value: forbidden_call()):\n    return value + 1',
                       'def increment(value: int):\n    return value + 1',
                       'def increment(value):\n    return eval("value+1")',
                       'def increment(value):\n    return 11',
                       'def increment(value):\n    return value + 2',
                       'def increment(value):\n    import os\n    return value + 1'):
            self.assertFalse(_safe_increment_source(unsafe))
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
        # A healthy model must not hide missing or rejected operator access.
        with patch.dict('os.environ', {}, clear=True):
            for access in ('not_configured', 'unavailable', 'ready'):
                report = {'inference_ready': True, 'operator_access': access}
                with self.subTest(operator_access=access), patch(
                    'production_os_live_diagnostics.diagnose', return_value=report
                ), redirect_stdout(io.StringIO()) as output:
                    self.assertEqual(main(), 0 if access == 'ready' else 1)
                    self.assertEqual(report['diagnostic_ready'], access == 'ready')
                    self.assertNotIn('operator-secret', output.getvalue())
        with patch.dict('os.environ', {'PRODUCTION_OS_DIAGNOSE_WAKE': '1'}, clear=True):
            for wake in (None, {}, {'mode': 'unknown'}, {'mode': 'unavailable'},
                         {'mode': 'immediate'}, {'mode': 'scheduled_fallback'}):
                report = {'inference_ready': True, 'operator_access': 'ready', 'worker_wake': wake}
                expected = isinstance(wake, dict) and wake.get('mode') in {'immediate', 'scheduled_fallback'}
                with self.subTest(worker_wake=wake), patch(
                    'production_os_live_diagnostics.diagnose', return_value=report
                ), redirect_stdout(io.StringIO()):
                    self.assertEqual(main(), 0 if expected else 1)
                    self.assertEqual(report['diagnostic_ready'], expected)
            with (patch('production_os_live_diagnostics.diagnose', side_effect=StudioError('operator-secret')),
                  redirect_stdout(io.StringIO()) as output):
                self.assertEqual(main(), 1)
                self.assertNotIn('operator-secret', output.getvalue())

    def test_defaults_preserve_explicit_configuration_and_other_providers(self):
        env = {'STUDIO_API_BASE': 'https://integrate.api.nvidia.com/v1/'}
        self.assertTrue(configure(env))
        models = [p['model'] for p in json.loads(env['STUDIO_PROVIDERS_JSON'])]
        self.assertEqual(models, ['nvidia/nemotron-3.5-lightning-30b-a3b', 'poolside/laguna-xs-2.1'])
        # Fresh hosted code proof qualifies Lightning; keep an unavailable
        # Poolside fallback from preceding it in the actual default registry.
        from provider_router import load_providers
        with patch.dict('os.environ', {**env, 'STUDIO_API_KEY': 'fixture'}, clear=True):
            ordered = load_providers()
        self.assertEqual([p.model_for('implementation') for p in ordered], [
            'nvidia/nemotron-3-super-120b-a12b',
            'nvidia/nemotron-3.5-lightning-30b-a3b',
            'poolside/laguna-xs-2.1',
        ])
        cloudflare_env = {
            'STUDIO_API_BASE': 'https://integrate.api.nvidia.com/v1',
            'STUDIO_CLOUDFLARE_FREE_TIER_ONLY': '1',
            'CLOUDFLARE_ACCOUNT_ID': 'a' * 32,
            'CLOUDFLARE_API_TOKEN': 'sensitive-cloudflare-key',
        }
        self.assertTrue(configure(cloudflare_env))
        self.assertNotIn('sensitive-cloudflare-key', cloudflare_env['STUDIO_PROVIDERS_JSON'])
        configured = json.loads(cloudflare_env['STUDIO_PROVIDERS_JSON'])
        self.assertEqual(len(configured), 3)
        self.assertEqual(configured[2]['model'], '@cf/zai-org/glm-4.7-flash')
        self.assertEqual(configured[2]['key_env'], 'CLOUDFLARE_API_TOKEN')
        self.assertEqual(
            configured[2]['base'],
            'https://api.cloudflare.com/client/v4/accounts/' + 'a' * 32 + '/ai/v1',
        )
        for excluded in (
            {'STUDIO_CLOUDFLARE_FREE_TIER_ONLY': '0'},
            {'CLOUDFLARE_ACCOUNT_ID': 'invalid'},
            {'CLOUDFLARE_API_TOKEN': ''},
        ):
            disabled = {
                'STUDIO_API_BASE': 'https://integrate.api.nvidia.com/v1',
                'STUDIO_CLOUDFLARE_FREE_TIER_ONLY': '1',
                'CLOUDFLARE_ACCOUNT_ID': 'a' * 32,
                'CLOUDFLARE_API_TOKEN': 'sensitive-cloudflare-key',
            }
            disabled.update(excluded)
            self.assertTrue(configure(disabled))
            self.assertEqual(len(json.loads(disabled['STUDIO_PROVIDERS_JSON'])), 2)
        for env in ({'STUDIO_API_BASE': 'https://another.example/v1'},
                    {'STUDIO_API_BASE': 'https://integrate.api.nvidia.com/v1', 'STUDIO_PROVIDERS_JSON': '[]'}):
            before = dict(env)
            self.assertFalse(configure(env))
            self.assertEqual(env, before)
