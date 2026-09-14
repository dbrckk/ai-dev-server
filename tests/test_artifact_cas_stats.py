import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import artifact_cas_stats as stats
import immutable_artifact_cache as cache


class ArtifactCasStatsTests(unittest.TestCase):
    def test_hits_and_rebuild_cost_raise_retention_score(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "stats.json"
            env = {"STUDIO_ARTIFACT_CAS_STATS_PATH": str(path)}
            with mock.patch.dict(os.environ, env, clear=False):
                cold = "a" * 64
                hot = "b" * 64
                stats.record(cold, size=1024, hit=False, rebuild_cost_seconds=1)
                stats.record(hot, size=1024, hit=False, rebuild_cost_seconds=30)
                stats.record(hot, size=1024, hit=True)
                stats.record(hot, size=1024, hit=True)

                self.assertGreater(
                    stats.retention_score(hot),
                    stats.retention_score(cold),
                )

    def test_value_trim_keeps_more_valuable_blob_under_quota(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "stats.json"
            env = {"STUDIO_ARTIFACT_CAS_STATS_PATH": str(path)}
            with mock.patch.dict(os.environ, env, clear=False):
                low = "1" * 64
                high = "2" * 64
                stats.record(low, size=1024, hit=False, rebuild_cost_seconds=1)
                stats.record(high, size=1024, hit=True, rebuild_cost_seconds=40)
                entries = {
                    "a" * 64: {
                        "validation_key": "a" * 64,
                        "files": {
                            cache.APK_REL: {"sha256": low, "size": 1024},
                        },
                    },
                    "b" * 64: {
                        "validation_key": "b" * 64,
                        "files": {
                            cache.APK_REL: {"sha256": high, "size": 1024},
                        },
                    },
                }
                with mock.patch.object(cache, "MAX_TOTAL_BYTES", 1024):
                    trimmed = cache._trim_by_value(entries)

                self.assertEqual(list(trimmed), ["b" * 64])

    def test_recency_is_deterministic_logical_clock(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "stats.json"
            env = {"STUDIO_ARTIFACT_CAS_STATS_PATH": str(path)}
            with mock.patch.dict(os.environ, env, clear=False):
                older = "c" * 64
                newer = "d" * 64
                stats.record(older, size=1024, hit=False)
                stats.record(newer, size=1024, hit=False)

                self.assertGreater(
                    stats.retention_score(newer),
                    stats.retention_score(older),
                )

    def test_summary_reports_hits_bytes_and_protected_cost(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "stats.json"
            env = {"STUDIO_ARTIFACT_CAS_STATS_PATH": str(path)}
            with mock.patch.dict(os.environ, env, clear=False):
                digest = "e" * 64
                stats.record(digest, size=2048, hit=False, rebuild_cost_seconds=15)
                stats.record(digest, size=2048, hit=True)
                result = stats.summary()

            self.assertEqual(result["blob_count"], 1)
            self.assertEqual(result["tracked_bytes"], 2048)
            self.assertEqual(result["hits"], 1)
            self.assertEqual(result["protected_rebuild_seconds"], 15.0)
            self.assertGreater(result["mean_retention_score"], 0.0)


if __name__ == "__main__":
    unittest.main()
