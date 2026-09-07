"""Validate executable acceptance journeys; strings are data, never generated Dart code."""
import base64
import json
import re


def validate_journeys(value):
    if not isinstance(value, list) or not 1 <= len(value) <= 6:
        raise ValueError('Product must define 1..6 acceptance journeys')
    ids = set()
    for journey in value:
        if not isinstance(journey, dict) or set(journey) != {'id', 'steps'}:
            raise ValueError('Journey fields must be id and steps')
        name = journey['id']
        if not isinstance(name, str) or not re.fullmatch(r'[a-z][a-z0-9-]{0,39}', name) or name in ids or name == 'initial':
            raise ValueError('Invalid or duplicate journey id')
        ids.add(name)
        steps = journey['steps']
        if not isinstance(steps, list) or not 2 <= len(steps) <= 12:
            raise ValueError('Each journey needs 2..12 steps')
        assertions = interactions = 0
        for step in steps:
            if not isinstance(step, dict):
                raise ValueError('Invalid step')
            action = step.get('action')
            fields = {'tap': {'action', 'key'}, 'enter_text': {'action', 'key', 'value'},
                      'expect_text': {'action', 'value'}, 'expect_absent': {'action', 'value'},
                      'expect_key': {'action', 'key'}, 'scroll': {'action', 'key', 'dy'}}
            if action not in fields or set(step) != fields[action]:
                raise ValueError('Unsupported action or fields')
            if 'key' in step and (not isinstance(step['key'], str) or not re.fullmatch(r'[a-z][a-z0-9_-]{0,59}', step['key'])):
                raise ValueError('Keys must be stable lower-case ValueKey names')
            if 'value' in step and (not isinstance(step['value'], str) or not 1 <= len(step['value']) <= 160):
                raise ValueError('Invalid step text')
            if action == 'scroll' and (type(step['dy']) not in (float, int) or not -1000 <= step['dy'] <= 1000 or step['dy'] == 0):
                raise ValueError('Invalid scroll distance')
            assertions += action in ('expect_text', 'expect_absent', 'expect_key')
            interactions += action in ('tap', 'enter_text', 'scroll')
        if not assertions or not interactions:
            raise ValueError('Journey requires an interaction and an assertion')
    return value


def encoded_journeys(value):
    validate_journeys(value)
    return base64.b64encode(json.dumps(value, ensure_ascii=False).encode()).decode()

CONTRACT = '''The product JSON MUST include journeys: 1..6 objects with exactly id and steps.
Each journey is an important acceptance path, defined BEFORE implementation, with 2..12 steps,
at least one interaction and assertion. Supported steps ONLY:
{"action":"tap","key":"settings_button"}, {"action":"enter_text","key":"name_input","value":"Alice"},
{"action":"scroll","key":"settings_list","dy":-300}, {"action":"expect_text","value":"Settings"},
{"action":"expect_absent","value":"Error"}, {"action":"expect_key","key":"timer_running"}.
Use stable Flutter ValueKey<String> selectors. Every journey starts on the fresh home screen.
Cover all important screens and principal happy/error paths; no simulated backend claims.
Tests replay every journey in light/dark, compact/wide and large text layouts and capture its final screen.
The implementation MUST implement the exact keys/text required by these immutable acceptance journeys.
'''
