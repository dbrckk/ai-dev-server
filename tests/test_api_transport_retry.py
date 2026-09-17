import urllib.error
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))

from core import API


class APITransportRetryTests(unittest.TestCase):
    def test_call_retries_transient_url_error_then_succeeds(self):
        api = API('https://example.test', 'key')
        responses = [urllib.error.URLError('temporary network failure'), {'ok': True}]

        def fake_response(_req, timeout_seconds=300):
            value = responses.pop(0)
            if isinstance(value, Exception):
                raise value
            return value

        with patch.object(api, '_response', side_effect=fake_response) as response, \
                patch('core.time.sleep') as sleep:
            result = api.call('GET', '/resource', timeout_seconds=30)

        self.assertEqual(result, {'ok': True})
        self.assertEqual(response.call_count, 2)
        sleep.assert_called_once_with(1.0)


if __name__ == '__main__':
    unittest.main()
