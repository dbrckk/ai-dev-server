import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from github_artifact_cas_stats_store import (
    ArtifactCasStatsStoreError,
    MAX_BLOBS,
    _validate,
)


class GitHubArtifactCasStatsStoreTests(unittest.TestCase):
    def test_accepts_valid_stats(self):
        payload = {
            "schema": 1,
            "clock": 3,
            "blobs": {
                "a" * 64: {
                    "hits": 2,
                    "last_used": 3,
                    "size": 2048,
                    "rebuild_cost_seconds": 12.5,
                }
            },
        }
        self.assertEqual(_validate(payload), payload)

    def test_rejects_invalid_digest(self):
        payload = {
            "schema": 1,
            "clock": 1,
            "blobs": {
                "bad": {
                    "hits": 0,
                    "last_used": 1,
                    "size": 1,
                    "rebuild_cost_seconds": 0.0,
                }
            },
        }
        with self.assertRaises(ArtifactCasStatsStoreError):
            _validate(payload)

    def test_rejects_negative_hits(self):
        payload = {
            "schema": 1,
            "clock": 1,
            "blobs": {
                "b" * 64: {
                    "hits": -1,
                    "last_used": 1,
                    "size": 1,
                    "rebuild_cost_seconds": 0.0,
                }
            },
        }
        with self.assertRaises(ArtifactCasStatsStoreError):
            _validate(payload)

    def test_rejects_oversized_stats(self):
        payload = {
            "schema": 1,
            "clock": 1,
            "blobs": {
                f"{i:064x}": {
                    "hits": 0,
                    "last_used": 1,
                    "size": 1,
                    "rebuild_cost_seconds": 0.0,
                }
                for i in range(MAX_BLOBS + 1)
            },
        }
        with self.assertRaises(ArtifactCasStatsStoreError):
            _validate(payload)


if __name__ == "__main__":
    unittest.main()
