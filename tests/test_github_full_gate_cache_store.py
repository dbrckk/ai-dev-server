import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from core import IMAGE
from github_full_gate_cache_store import (
    FullGateCacheStoreError,
    MAX_ENTRIES,
    _validate,
)


class GitHubFullGateCacheStoreTests(unittest.TestCase):
    def test_accepts_valid_success_only_cache(self):
        payload = {
            "schema": 1,
            "flutter_image": IMAGE,
            "entries": {
                "a" * 64: {"passed": True},
            },
        }
        self.assertEqual(_validate(payload), payload)

    def test_rejects_toolchain_mismatch(self):
        payload = {
            "schema": 1,
            "flutter_image": "other-image",
            "entries": {},
        }
        with self.assertRaises(FullGateCacheStoreError):
            _validate(payload)

    def test_rejects_failed_entry(self):
        payload = {
            "schema": 1,
            "flutter_image": IMAGE,
            "entries": {
                "a" * 64: {"passed": False},
            },
        }
        with self.assertRaises(FullGateCacheStoreError):
            _validate(payload)

    def test_rejects_oversized_cache(self):
        payload = {
            "schema": 1,
            "flutter_image": IMAGE,
            "entries": {
                f"{i:064x}": {"passed": True}
                for i in range(MAX_ENTRIES + 1)
            },
        }
        with self.assertRaises(FullGateCacheStoreError):
            _validate(payload)


if __name__ == "__main__":
    unittest.main()
