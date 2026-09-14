import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from github_quick_gate_cache_store import (
    MAX_ENTRIES,
    QuickGateCacheStoreError,
    _validate,
)


class GitHubQuickGateCacheStoreTests(unittest.TestCase):
    def test_accepts_valid_cache_payload(self):
        payload = {
            "schema": 1,
            "toolchain_fingerprint": "a" * 64,
            "entries": {
                "b" * 64: {
                    "passed": True,
                    "logs": [
                        {
                            "command": ["flutter", "analyze"],
                            "exit_code": 0,
                            "output": "",
                        }
                    ],
                }
            },
        }
        result = _validate(payload)
        self.assertEqual(result, payload)

    def test_rejects_invalid_cache_key(self):
        payload = {
            "schema": 1,
            "toolchain_fingerprint": "a" * 64,
            "entries": {
                "short": {
                    "passed": True,
                    "logs": [],
                }
            },
        }
        with self.assertRaises(QuickGateCacheStoreError):
            _validate(payload)

    def test_rejects_oversized_cache(self):
        payload = {
            "schema": 1,
            "toolchain_fingerprint": "a" * 64,
            "entries": {
                f"{i:064x}": {
                    "passed": True,
                    "logs": [],
                }
                for i in range(MAX_ENTRIES + 1)
            },
        }
        with self.assertRaises(QuickGateCacheStoreError):
            _validate(payload)

    def test_rejects_unbounded_log_output(self):
        payload = {
            "schema": 1,
            "toolchain_fingerprint": "a" * 64,
            "entries": {
                "b" * 64: {
                    "passed": False,
                    "logs": [
                        {
                            "command": ["flutter", "test"],
                            "exit_code": 1,
                            "output": "x" * 20001,
                        }
                    ],
                }
            },
        }
        with self.assertRaises(QuickGateCacheStoreError):
            _validate(payload)


if __name__ == "__main__":
    unittest.main()
