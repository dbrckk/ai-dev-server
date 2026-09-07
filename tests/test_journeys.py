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
