import json
from pathlib import Path
import unittest
import os
import tempfile
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))

from core import StudioError
from godot_model import GodotModel
from provider_router import ProviderSpec


class FakeAPI:
    base = 'https://example.test/v1'
    def __init__(self, responses): self.responses = list(responses); self.calls = []
    def call(self, method, path, data=None):
        self.calls.append((method, path, data))
        value = self.responses.pop(0)
        if isinstance(value, Exception): raise value
        return value


def completion(value):
    return {'choices':[{'finish_reason':'stop','message':{'content':json.dumps(value)}}]}


def model(responses, limit=4):
    obj = GodotModel.__new__(GodotModel)
    obj.api = FakeAPI(responses)
    obj.model = 'general'
    obj.code_model = 'code'
    obj.providers = (
        ProviderSpec('primary', 'https://example.test/v1', 'primary-key', 'general', code_model='code', priority=100),
        ProviderSpec('fallback', 'https://fallback.test/v1', 'fallback-key', 'fallback-general', code_model='fallback-code', priority=90),
    )
    obj.models_used = {}
    obj.providers_used = {}
    obj.routing_portfolio = {}
    obj.avoid_providers = set()
    obj.vision = ''
    obj.limit = limit
    obj.calls = 0
    return obj


def product_value():
    return {'acceptance_criteria':['game starts'], 'journeys':[{'id':'play','steps':[
        {'action':'tap','key':'play_button'}, {'action':'expect_text','value':'Score'}]}]}


class GodotModelTests(unittest.TestCase):
    def test_nvidia_source_generation_requests_json_mode(self):
        subject = model([
            completion({'files': [{'path': 'scripts/main.gd', 'content': 'extends Node\\n'}]}),
            completion(product_value()),
            completion({'direction': 'minimal'}),
        ])
        subject.api.base = 'https://integrate.api.nvidia.com/v1'
        subject.providers = (
            ProviderSpec(
                'primary', 'https://integrate.api.nvidia.com/v1',
                'primary-key', 'nvidia/nemotron-3-super-120b-a12b',
                code_model='nvidia/nemotron-3-super-120b-a12b', priority=100,
            ),
        )
        subject.ask('implementation', 'improve game')
        self.assertEqual(subject.api.calls[0][2]['response_format'], {'type': 'json_object'})
        self.assertEqual(subject.api.calls[0][2]['max_tokens'], 16000)
        self.assertEqual(subject.api.calls[0][2]['reasoning_budget'], 2048)
        subject.ask('product', 'plan game')
        subject.ask('design', 'art direction')
        self.assertEqual([call[2]['max_tokens'] for call in subject.api.calls], [16000, 3072, 1536])
        self.assertEqual([call[2]['reasoning_budget'] for call in subject.api.calls], [2048, 512, 512])
        self.assertIn('target no more than 900 output tokens', subject.api.calls[2][2]['messages'][0]['content'])
        self.assertTrue(all(
            call[2]['response_format'] == {'type': 'json_object'}
            for call in subject.api.calls
        ))

    def test_product_uses_godot_planning_contract_not_flutter_execution_claims(self):
        subject = model([completion(product_value())])
        result = subject.ask('product', 'plan game')
        self.assertEqual(result['journeys'][0]['id'], 'play')
        system = subject.api.calls[0][2]['messages'][0]['content']
        self.assertIn('Godot mobile game product lead', system)
        self.assertIn('specifications only', system)
        self.assertNotIn('Flutter ValueKey', system)
        self.assertIn('Keep the deliverable compact', system)
        self.assertEqual(subject.models_used['product'], 'general')
        self.assertEqual(subject.api.calls[0][2]['max_tokens'], 3072)

    def test_product_prompt_requires_literal_json_step_objects(self):
        # Canary 35 spent two calls rejecting an otherwise well-formed plan:
        # the Godot prompt omitted the validator's 40-character id limit.
        rejected = product_value()
        rejected['journeys'][0]['id'] = 'jumpy-settings-open-tap-empty-prevents-start'
        accepted = product_value()
        accepted['journeys'][0]['id'] = 'j' * 40
        subject = model([completion(rejected), completion(accepted)])
        result = subject.ask('product', 'plan game')
        self.assertEqual(result, accepted)
        self.assertEqual(subject.calls, 2)
        system = subject.api.calls[0][2]['messages'][0]['content']
        self.assertIn('Every step MUST be a JSON object', system)
        self.assertIn('{"action":"tap","key":"play_button"}', system)
        self.assertIn('{"action":"expect_text","value":"Score"}', system)
        self.assertNotIn('tap(key)', system)
        self.assertIn('max 40 characters', system)
        self.assertIn('initial is reserved', system)
        self.assertIn('max 60 characters', system)
        self.assertIn('1..160 characters', system)
        self.assertIn('nonzero number between -1000 and 1000', system)
        retry = subject.api.calls[1][2]['messages']
        self.assertEqual(retry[0]['content'], system)
        self.assertIn(rejected['journeys'][0]['id'], retry[1]['content'])
        # Keep strict rejection and the existing two-call ceiling.
        subject = model([completion(rejected), completion(rejected)])
        with self.assertRaisesRegex(StudioError, 'Structured response rejected'):
            subject.ask('product', 'plan game')
        self.assertEqual(subject.calls, 2)

    def test_implementation_uses_godot_prompt_and_scope(self):
        subject = model([completion({'files':[{'path':'scripts/main.gd','content':'extends Node\n'}]})])
        result = subject.ask('implementation', 'improve game')
        self.assertEqual(result['files'][0]['path'], 'scripts/main.gd')
        params = subject.api.calls[0][2]
        system = params['messages'][0]['content']
        self.assertIn('Godot 4.7', system)
        self.assertNotIn('Senior Flutter engineering team', system)
        self.assertEqual(subject.calls, 1)

    def test_test_role_rejects_non_test_path_then_repairs_once(self):
        subject = model([
            completion({'files':[{'path':'scripts/main.gd','content':'extends Node\n'}]}),
            completion({'files':[{'path':'tests/main_test.gd','content':'extends Node\n'}]}),
        ])
        result = subject.ask('tests', 'write regression')
        self.assertEqual(result['files'][0]['path'], 'tests/main_test.gd')
        self.assertEqual(subject.calls, 2)

    def test_truncated_patch_retry_requests_a_smaller_complete_change(self):
        truncated = {'choices':[{'finish_reason':'length','message':{'content':'{"files":['}}]}
        subject = model([
            truncated,
            completion({'files':[{'path':'scripts/main.gd','content':'extends Node\n'}]}),
        ])
        result = subject.ask('implementation', 'improve game')
        self.assertEqual(result['files'][0]['path'], 'scripts/main.gd')
        self.assertEqual(subject.calls, 2)
        retry = subject.api.calls[1][2]['messages'][1]['content']
        self.assertIn('at most two files', retry)
        self.assertIn('20,000 characters', retry)
        self.assertIn('complete JSON', retry)

    def test_structured_godot_call_falls_back_to_secondary_provider(self):
        subject = model([StudioError('API unavailable or timed out')])
        fallback_api = FakeAPI([completion(product_value())])
        fallback_api.base = 'https://fallback.test/v1'
        with patch('core.API', return_value=fallback_api) as api_factory:
            result = subject.ask('product', 'plan game')
        self.assertEqual(result['journeys'][0]['id'], 'play')
        self.assertEqual(subject.providers_used['product'], 'fallback')
        self.assertEqual(fallback_api.calls[0][2]['model'], 'fallback-general')
        self.assertIn('Godot mobile game product lead', fallback_api.calls[0][2]['messages'][0]['content'])
        api_factory.assert_called_once_with('https://fallback.test/v1', 'fallback-key')

        # A successful HTTP call with malformed JSON is not successful
        # inference. The bounded repair tries an alternate provider instead
        # of requesting the same malformed completion twice.
        malformed = {'choices': [{'finish_reason': 'stop',
                                  'message': {'content': '{not json'}}]}
        subject = model([malformed])
        fallback_api = FakeAPI([completion(product_value())])
        fallback_api.base = 'https://fallback.test/v1'
        with patch('core.API', return_value=fallback_api):
            result = subject.ask('product', 'plan game')
        self.assertEqual(result['journeys'][0]['id'], 'play')
        self.assertEqual(subject.providers_used['product'], 'fallback')
        self.assertEqual(subject.calls, 2)
        self.assertEqual(len(subject.api.calls), 1)
        self.assertEqual(len(fallback_api.calls), 1)

        # An installation with no alternate provider still retains its
        # original same-provider repair attempt, with no new provider calls.
        subject = model([malformed, completion(product_value())])
        subject.providers = (subject.providers[0],)
        result = subject.ask('product', 'plan game')
        self.assertEqual(result['journeys'][0]['id'], 'play')
        self.assertEqual(subject.providers_used['product'], 'primary')
        self.assertEqual(len(subject.api.calls), 2)
        self.assertEqual(subject.calls, 2)

    def test_ranked_fallback_uses_its_own_api_client_when_it_beats_primary(self):
        subject = model([completion(product_value())])
        primary, fallback = subject.providers
        fallback_api = FakeAPI([completion(product_value())])
        fallback_api.base = fallback.base
        with patch('godot_model.candidates_for', return_value=(fallback, primary)), \
                patch('core.API', return_value=fallback_api) as api_factory:
            result = subject.ask('product', 'plan game')
        self.assertEqual(result['journeys'][0]['id'], 'play')
        self.assertEqual(subject.providers_used['product'], 'fallback')
        self.assertEqual(subject.api.calls, [])
        self.assertEqual(fallback_api.calls[0][2]['model'], 'fallback-general')
        api_factory.assert_called_once_with(fallback.base, fallback.key)

    def test_budget_is_shared_and_fail_closed(self):
        subject = model([], limit=0)
        with self.assertRaisesRegex(StudioError, 'budget exhausted'):
            subject.ask('implementation', 'x')
        from native_model_usage import snapshot
        from capacity_ledger import consumed_tokens, load
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); journal=root/'usage.json'; ledger=root/'ledger.json'; plan=root/'plan.json'
            plan.write_text(json.dumps({'projects':[{'id':'demo','token_envelope':20000}]}))
            with patch.dict(os.environ, {'STUDIO_NATIVE_MODEL_USAGE_PATH':str(journal),
                    'STUDIO_CAPACITY_PLAN_PATH':str(plan),'STUDIO_CAPACITY_LEDGER_PATH':str(ledger),
                    'STUDIO_PROJECT_ID':'demo'}):
                reply=completion(product_value())
                reply['usage']={'prompt_tokens':31,'completion_tokens':19,'total_tokens':50,
                                'prompt_tokens_details':{'cached_tokens':7},
                                'completion_tokens_details':{'reasoning_tokens':5}}
                subject=model([reply]); subject.ask('product','plan game')
                usage=snapshot()['usage']
                self.assertEqual((usage['runs'],usage['total_tokens'],usage['cached_input_tokens'],usage['reasoning_tokens']), (1,50,7,5))
                self.assertEqual(usage['estimated_calls'],0)
                self.assertEqual(consumed_tokens(load(ledger),project_id='demo'),50)
                plan.write_text(json.dumps({'projects':[{'id':'demo','token_envelope':50}]}))
                subject=model([])
                with self.assertRaisesRegex(StudioError,'project_envelope_exhausted'):
                    subject.ask('product','plan game')
                self.assertEqual(subject.api.calls,[])
                self.assertTrue(snapshot()['capacity_exhausted'])
                self.assertEqual(snapshot()['usage']['runs'],1)
                plan.write_text(json.dumps({'projects':[{'id':'demo','token_envelope':20000}]}))
                ledger.write_text(json.dumps({'schema':1,'consumed':{'demo::native:primary':-100},'reservations':{}}))
                with self.assertRaisesRegex(StudioError,'capacity ledger invalid'):
                    subject.ask('product','plan game')
                self.assertEqual(subject.api.calls,[])
                plan.unlink()
                with self.assertRaisesRegex(StudioError,'capacity plan missing or invalid'):
                    subject.ask('product','plan game')
                self.assertEqual(subject.api.calls,[])

            # Regression from real Jumpy canary #34: under a finite envelope,
            # conservative unknown-usage reservations for planning must still
            # leave the full implementation output allowance available.
            planning_journal = root/'planning-usage.json'
            planning_ledger = root/'planning-ledger.json'
            planning_plan = root/'planning-plan.json'
            planning_plan.write_text(json.dumps({
                'projects': [{'id': 'jumpy', 'token_envelope': 24000}]
            }))
            with patch.dict(os.environ, {
                'STUDIO_NATIVE_MODEL_USAGE_PATH': str(planning_journal),
                'STUDIO_CAPACITY_PLAN_PATH': str(planning_plan),
                'STUDIO_CAPACITY_LEDGER_PATH': str(planning_ledger),
                'STUDIO_PROJECT_ID': 'jumpy',
            }):
                subject = model([
                    completion(product_value()),
                    completion({'direction': 'focused'}),
                    completion({'files': [{'path': 'scripts/main.gd',
                                          'content': 'extends Node\\n'}]}),
                ])
                subject.providers = (subject.providers[0],)
                subject.ask('product', 'fix one input bug')
                subject.ask('design', 'minimal settings overlay')
                source_patch = subject.ask('implementation', 'implement the guarded input')
                self.assertEqual(source_patch['files'][0]['path'], 'scripts/main.gd')
                self.assertEqual(
                    [row[2]['max_tokens'] for row in subject.api.calls],
                    [3072, 1536, 16000],
                )
                self.assertLessEqual(
                    consumed_tokens(load(planning_ledger), project_id='jumpy'),
                    24000,
                )
                self.assertFalse(snapshot()['capacity_exhausted'])


if __name__ == '__main__': unittest.main()
