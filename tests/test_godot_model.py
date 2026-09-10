import json
from pathlib import Path
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))

from core import StudioError
from godot_model import GodotModel


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
    obj.models_used = {}
    obj.vision = ''
    obj.limit = limit
    obj.calls = 0
    return obj


class GodotModelTests(unittest.TestCase):
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

    def test_budget_is_shared_and_fail_closed(self):
        subject = model([], limit=0)
        with self.assertRaisesRegex(StudioError, 'budget exhausted'):
            subject.ask('implementation', 'x')


if __name__ == '__main__': unittest.main()
