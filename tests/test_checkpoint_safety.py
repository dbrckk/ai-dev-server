import http.client
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))
from core import API, Model, StudioError
from run import GitHub


class CheckpointSafetyTests(unittest.TestCase):
    def test_valid_checkpoint_preserves_nested_unicode_metadata(self):
        state = {'status': 'blocked', 'design': {'title': 'Écran', 'ratio': 1.5}}
        with tempfile.TemporaryDirectory() as d:
            gh = GitHub.__new__(GitHub)
            gh.repo = '/repos/owner/app'
            gh.get = Mock(return_value=[])
            gh.call = Mock(side_effect=[{'sha': 'tree'}, {'sha': 'commit'}, {}])
            self.assertEqual(gh.publish('studio/demo', None, Path(d), state), 'commit')
            entry = gh.call.call_args_list[0].args[2]['tree'][0]
            self.assertEqual(json.loads(entry['content']), state)

    def test_incomplete_response_body_does_not_resubmit(self):
        response = Mock()
        response.status = 200
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        response.read.side_effect = http.client.IncompleteRead(b'ghp_partialSecret')
        opener = Mock()
        opener.open.return_value = response
        with patch('core.urllib.request.build_opener', return_value=opener):
            with self.assertRaises(StudioError) as caught:
                API('https://example.com', 'key').call('POST', '/completion', {})
        self.assertNotIn('ghp_partialSecret', str(caught.exception))
        self.assertEqual(opener.open.call_count, 1)

    def test_filtered_or_interrupted_completion_is_not_a_review_pass(self):
        for reason in ('content_filter', 'tool_calls', 'function_call'):
            with self.subTest(reason=reason), patch.dict('os.environ', {'STUDIO_API_KEY': 'test'}, clear=True):
                model = Model(1)
                model.api.call = Mock(return_value={'choices': [{'finish_reason': reason,
                    'message': {'content': '{"passed":true,"blockers":[]}'}}]})
                with self.assertRaises(StudioError):
                    model.ask('review', 'brief')
                self.assertEqual(model.calls, 1)

    def test_checkpoint_metadata_rejected_before_any_remote_call(self):
        for value in ('ghp_fixtureSecret', float('nan'), '\ud800'):
            with self.subTest(value=ascii(value)), tempfile.TemporaryDirectory() as d:
                gh = GitHub.__new__(GitHub)
                gh.repo = '/repos/owner/app'
                gh.get = Mock(side_effect=AssertionError('remote read before validation'))
                gh.call = Mock(side_effect=AssertionError('remote write before validation'))
                with self.assertRaises(StudioError):
                    gh.publish('studio/demo', 'parent', Path(d),
                               {'status': 'blocked', 'product': {'detail': value}})
                gh.get.assert_not_called()
                gh.call.assert_not_called()

    def test_metadata_secret_is_repaired_without_echoing_it(self):
        secret = 'ghp_fixtureSecret'
        with patch.dict('os.environ', {'STUDIO_API_KEY': 'test'}, clear=True):
            model = Model(2)
            envelope = lambda value: {'choices': [{'message': {'content': json.dumps(value)}}]}
            model.api.call = Mock(side_effect=[envelope({'design': {'token': secret}}),
                                               envelope({'design': 'safe'})])
            self.assertEqual(model.ask('design', 'brief'), {'design': 'safe'})
            self.assertEqual(model.calls, 2)
            self.assertNotIn(secret, json.dumps(model.api.call.call_args.args[2]))

    def test_transport_disconnect_does_not_resubmit_or_expose_partial_body(self):
        failures = [http.client.IncompleteRead(b'ghp_partialSecret'),
                    http.client.RemoteDisconnected('ghp_partialSecret'),
                    ConnectionResetError('ghp_partialSecret')]
        for failure in failures:
            with self.subTest(failure=type(failure).__name__):
                opener = Mock()
                opener.open.side_effect = failure
                with patch('core.urllib.request.build_opener', return_value=opener):
                    with self.assertRaises(StudioError) as caught:
                        API('https://example.com', 'key').call('POST', '/completion', {})
                self.assertNotIn('ghp_partialSecret', str(caught.exception))
                self.assertEqual(opener.open.call_count, 1)
