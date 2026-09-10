import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch
import urllib.error
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))
from core import API, APIError, StudioError, Model

BASE = 'https://integrate.api.nvidia.com/v1'
RID = '12345678-1234-1234-1234-123456789abc'

def response(status, body=None, rid=RID):
    obj = io.BytesIO(json.dumps(body or {}).encode())
    obj.status, obj.headers = status, {'NVCF-REQID': rid}
    return obj

class TransportTests(unittest.TestCase):
    def call_with(self, replies, base=BASE):
        opener = Mock()
        opener.open.side_effect = replies
        with patch('core.urllib.request.build_opener', return_value=opener), patch('core.time.sleep'):
            result = API(base, 'test-token').call('POST', '/chat/completions', {})
        return result, opener

    def test_pending_polls_same_origin_without_resubmitting(self):
        result, opener = self.call_with([response(202), response(202), response(200, {'ok': True})])
        self.assertEqual(result, {'ok': True})
        requests = [call.args[0] for call in opener.open.call_args_list]
        self.assertEqual([r.get_method() for r in requests], ['POST', 'GET', 'GET'])
        self.assertEqual(requests[1].full_url, BASE + '/status/' + RID)

    def test_rejects_untrusted_pending_ids_and_providers(self):
        for base, rid in [(BASE, '../../evil'), (BASE, 'https://evil.test'), ('https://example.com/v1', RID)]:
            with self.subTest(base=base, rid=rid), self.assertRaises(StudioError):
                self.call_with([response(202, rid=rid)], base)

    def test_polling_has_a_hard_limit(self):
        with self.assertRaisesRegex(StudioError, 'polling limit'):
            self.call_with([response(202) for _ in range(61)])

    def test_poll_error_never_resubmits_post(self):
        with self.assertRaises(APIError):
            self.call_with([response(202), urllib.error.HTTPError(BASE, 503, 'error', {}, None)])

    def test_non_json_response_is_clear(self):
        r = response(200)
        r.seek(0); r.write(b'not json'); r.seek(0)
        with self.assertRaisesRegex(StudioError, 'non-JSON'):
            self.call_with([r])

    def test_completion_explicitly_disables_streaming(self):
        with patch.dict('os.environ', {'STUDIO_API_KEY': 'test'}, clear=True):
            m = Model(1)
        m.api.call = Mock(return_value={'choices': [{'message': {'content': '{"tokens":{}}'}}]})
        m.ask('design', 'brief')
        self.assertIs(m.api.call.call_args.args[2]['stream'], False)

class MalformedEnvelopeTests(unittest.TestCase):
    def test_non_finite_numbers_use_bounded_repair(self):
        for number in ('NaN', 'Infinity', '-Infinity', '1e999'):
            with self.subTest(number=number), patch.dict('os.environ', {'STUDIO_API_KEY': 'test'}, clear=True):
                envelope = lambda raw: {'choices': [{'message': {'content': raw}}]}
                invalid = envelope('{"nested":[{"value":' + number + '}]}')
                model = Model(2)
                model.api.call = Mock(side_effect=[invalid, envelope('{"value":1.5}')])
                self.assertEqual(model.ask('design', 'brief'), {'value': 1.5})
                self.assertEqual(model.calls, 2)
                model = Model(1)
                model.api.call = Mock(return_value=invalid)
                with self.assertRaisesRegex(StudioError, 'Structured response rejected'):
                    model.ask('design', 'brief')
                self.assertEqual(model.calls, 1)

    def test_excessive_json_nesting_uses_bounded_repair(self):
        depth = sys.getrecursionlimit() * 2
        raw = '{"nested":' + '[' * depth + '0' + ']' * depth + '}'
        envelope = lambda text: {'choices': [{'message': {'content': text}}]}
        with patch.dict('os.environ', {'STUDIO_API_KEY': 'test'}, clear=True):
            model = Model(2)
            model.api.call = Mock(side_effect=[envelope(raw), envelope('{"design":"valid"}')])
            self.assertEqual(model.ask('design', 'brief'), {'design': 'valid'})
            self.assertEqual(model.calls, 2)
            model = Model(1)
            model.api.call = Mock(return_value=envelope(raw))
            with self.assertRaisesRegex(StudioError, 'Structured response rejected'):
                model.ask('design', 'brief')
            self.assertEqual(model.calls, 1)

    def test_bad_choices_trigger_bounded_repair_without_attribute_crash(self):
        invalid = [None, [], {}, {'choices': []}, {'choices': [None]},
                   {'choices': ['invalid']}, {'choices': [{'message': None}]}]
        for envelope in invalid:
            with self.subTest(envelope=envelope), patch.dict('os.environ', {'STUDIO_API_KEY': 'test'}, clear=True):
                model = Model(2)
                model.api.call = Mock(return_value=envelope)
                with self.assertRaisesRegex(StudioError, 'Structured response rejected'):
                    model.ask('design', 'brief')
                self.assertEqual(model.calls, 2)

    def test_invalid_unicode_is_repaired_within_call_budget(self):
        for invalid in [{'nested': ['\ud800']}, {'\udfff': 'value'}]:
            with self.subTest(invalid=ascii(invalid)), patch.dict('os.environ', {'STUDIO_API_KEY': 'test'}, clear=True):
                model = Model(2)
                envelope = lambda value: {'choices': [{'message': {'content': json.dumps(value)}}]}
                model.api.call = Mock(side_effect=[envelope(invalid), envelope({'design': 'valid'})])
                self.assertEqual(model.ask('design', 'brief'), {'design': 'valid'})
                self.assertEqual(model.calls, 2)
                model = Model(1)
                model.api.call = Mock(return_value=envelope(invalid))
                with self.assertRaisesRegex(StudioError, 'Structured response rejected'):
                    model.ask('design', 'brief')
                self.assertEqual(model.calls, 1)
