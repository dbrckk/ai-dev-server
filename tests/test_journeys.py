import base64
import copy
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))
from journeys import validate_journeys, encoded_journeys

VALID = [{'id': 'settings', 'steps': [{'action': 'tap', 'key': 'settings_button'}, {'action': 'expect_text', 'value': 'Durée'}]}]

class JourneyTests(unittest.TestCase):
    def test_roundtrip_unicode_and_dart_injection_is_data(self):
        val = copy.deepcopy(VALID)
        val[0]['steps'][1]['value'] = "Durée $value '); evil(); ('"
        self.assertEqual(json.loads(base64.b64decode(encoded_journeys(val))), val)
    def test_rejects_no_interaction(self):
        val = copy.deepcopy(VALID)
        val[0]['steps'][0] = {'action': 'expect_key', 'key': 'settings_button'}
        with self.assertRaises(ValueError): validate_journeys(val)
    def test_rejects_no_assertion(self):
        val = copy.deepcopy(VALID)
        val[0]['steps'][1] = {'action': 'tap', 'key': 'back_button'}
        with self.assertRaises(ValueError): validate_journeys(val)
    def test_rejects_unknown_action(self):
        val = copy.deepcopy(VALID)
        val[0]['steps'][0] = {'action': 'shell', 'value': 'anything'}
        with self.assertRaises(ValueError): validate_journeys(val)
    def test_action_must_be_a_string(self):
        for action in ([], {}, None, True):
            val = copy.deepcopy(VALID)
            val[0]['steps'][0]['action'] = action
            with self.subTest(action=action), self.assertRaises(ValueError): validate_journeys(val)
    def test_rejects_duplicate_or_reserved_path(self):
        for val in [VALID * 2, [dict(VALID[0], id='initial')], [dict(VALID[0], id='../escape')]]:
            with self.subTest(val=val), self.assertRaises(ValueError): validate_journeys(val)
    def test_bounded_steps_and_journeys(self):
        for val in [[], VALID * 7, [dict(VALID[0], steps=VALID[0]['steps'] * 7)]]:
            with self.subTest(val=val), self.assertRaises(ValueError): validate_journeys(val)
    def test_invalid_scrolls(self):
        for dy in [True, float('nan'), float('inf'), 1001, 0, '3']:
            val = copy.deepcopy(VALID)
            val[0]['steps'][0] = {'action': 'scroll', 'key': 'list_view', 'dy': dy}
            with self.subTest(dy=dy), self.assertRaises(ValueError): validate_journeys(val)
    def test_typed_input_and_assertion(self):
        val = copy.deepcopy(VALID)
        val[0]['steps'][0] = {'action': 'enter_text', 'key': 'name_input', 'value': 'Alice'}
        self.assertEqual(validate_journeys(val), val)

class ProtocolRepairTests(unittest.TestCase):
    def test_underscore_slug_is_valid(self):
        val = copy.deepcopy(VALID)
        val[0]['id'] = 'timer_pause'
        self.assertEqual(validate_journeys(val), val)
    def test_one_repair_preserves_budget(self):
        from core import Model
        class InvalidThenValid(Model):
            def __init__(self):
                self.calls, self.limit = 0, 2
                self.contexts = []
            def _ask(self, role, context, screenshots=()):
                self.calls += 1
                self.contexts.append(context)
                return {'journeys': [] if self.calls == 1 else VALID}
        model = InvalidThenValid()
        self.assertEqual(model.ask('product', 'brief')['journeys'], VALID)
        self.assertEqual(model.calls, 2)
        self.assertIn('schema rule', model.contexts[1])
    def test_bad_schema_does_not_loop_forever(self):
        from core import Model, StudioError
        class AlwaysInvalid(Model):
            def __init__(self): self.calls, self.limit = 0, 9
            def _ask(self, *args):
                self.calls += 1
                return {'journeys': []}
        model = AlwaysInvalid()
        with self.assertRaises(StudioError): model.ask('product', 'brief')
        self.assertEqual(model.calls, 2)
    def test_no_protocol_retry_when_budget_exhausted(self):
        from core import Model, StudioError
        class Limited(Model):
            def __init__(self): self.calls, self.limit = 0, 1
            def _ask(self, *args):
                self.calls += 1
                return {'journeys': []}
        model = Limited()
        with self.assertRaises(StudioError): model.ask('product', 'brief')
        self.assertEqual(model.calls, 1)

class VisionDefaultsTests(unittest.TestCase):
    def test_nvidia_default(self):
        from unittest.mock import patch
        from core import Model
        with patch.dict('os.environ', {'STUDIO_API_KEY': 'test'}, clear=True):
            self.assertEqual(Model(2).vision, 'nvidia/nemotron-nano-12b-v2-vl')
    def test_other_provider_never_receives_nvidia_model_implicitly(self):
        from unittest.mock import patch
        from core import Model
        with patch.dict('os.environ', {'STUDIO_API_KEY': 'test', 'STUDIO_API_BASE': 'https://example.com/v1'}, clear=True):
            self.assertEqual(Model(2).vision, '')
    def test_explicit_disable(self):
        from unittest.mock import patch
        from core import Model
        with patch.dict('os.environ', {'STUDIO_API_KEY': 'test', 'STUDIO_VISION_MODEL': 'disabled'}, clear=True):
            self.assertEqual(Model(2).vision, '')

class TruncationTests(unittest.TestCase):
    def test_truncated_output_gets_one_budgeted_retry(self):
        from core import Model, ProtocolError
        class Truncated(Model):
            def __init__(self): self.calls, self.limit = 0, 2
            def _ask(self, *args):
                self.calls += 1
                if self.calls == 1: raise ProtocolError('Model response truncated')
                return {'journeys': VALID}
        model = Truncated()
        self.assertEqual(model.ask('product', 'brief')['journeys'], VALID)
        self.assertEqual(model.calls, 2)
    def test_auth_errors_are_not_protocol_retried(self):
        from core import Model, APIError
        class AuthError(Model):
            def __init__(self): self.calls, self.limit = 0, 10
            def _ask(self, *args):
                self.calls += 1
                raise APIError(401)
        model = AuthError()
        with self.assertRaises(APIError): model.ask('product', 'brief')
        self.assertEqual(model.calls, 1)
