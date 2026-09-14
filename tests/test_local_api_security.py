import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from core import API, StudioError


class LocalAPISecurityTests(unittest.TestCase):
    def test_loopback_http_is_allowed(self):
        api = API("http://127.0.0.1:11434/v1", "")
        self.assertEqual(api.base, "http://127.0.0.1:11434/v1")

    def test_localhost_http_is_allowed(self):
        api = API("http://localhost:8000/v1", "")
        self.assertEqual(api.base, "http://localhost:8000/v1")

    def test_remote_http_is_rejected(self):
        with self.assertRaises(StudioError):
            API("http://example.invalid/v1", "secret")

    def test_https_remote_remains_allowed(self):
        api = API("https://example.invalid/v1", "secret")
        self.assertEqual(api.base, "https://example.invalid/v1")


if __name__ == "__main__":
    unittest.main()
