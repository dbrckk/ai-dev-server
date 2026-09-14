import os
import tempfile
import unittest
from unittest import mock
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from core import StudioError
from immutable_artifact_cache import APK_REL, capture, restore, verify_entry, save, touch


class ImmutableArtifactCacheTests(unittest.TestCase):

    def _cas_env(self, root):
        return {
            "STUDIO_ARTIFACT_CAS_PATH": str(root / "cas"),
            "STUDIO_ARTIFACT_CACHE_PATH": str(root / "artifact-cache.json"),
            "STUDIO_ARTIFACT_CAS_STATS_PATH": str(root / "artifact-cas-stats.json"),
        }
    def _root(self, td):
        root = Path(td)
        apk = root / APK_REL
        apk.parent.mkdir(parents=True)
        apk.write_bytes(b"A" * 2048)
        goldens = root / "test/goldens"
        goldens.mkdir(parents=True)
        (goldens / "one.png").write_bytes(b"PNG-one")
        (goldens / "two.png").write_bytes(b"PNG-two")
        return root

    def test_capture_and_verified_restore(self):
        with tempfile.TemporaryDirectory() as td:
            root = self._root(td)
            key = "a" * 64
            with mock.patch.dict(os.environ, self._cas_env(root), clear=False):
                entry = capture(root, key)

                (root / APK_REL).unlink()
                for path in (root / "test/goldens").glob("*.png"):
                    path.unlink()

                result = restore(root, entry, key)

            self.assertIn(APK_REL, result["restored"])
            self.assertEqual((root / APK_REL).read_bytes(), b"A" * 2048)
            self.assertEqual((root / "test/goldens/one.png").read_bytes(), b"PNG-one")

    def test_corrupted_payload_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = self._root(td)
            key = "b" * 64
            with unittest.mock.patch.dict(os.environ, self._cas_env(root), clear=False):
                entry = capture(root, key)
                apk_meta = entry["files"][APK_REL]
                blob = root / "cas" / apk_meta["sha256"][:2] / apk_meta["sha256"][2:]
                payload = bytearray(blob.read_bytes())
                payload[0] ^= 0x01
                blob.write_bytes(bytes(payload))

                with self.assertRaises(StudioError):
                    verify_entry(entry, key)

    def test_validation_key_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = self._root(td)
            with unittest.mock.patch.dict(os.environ, self._cas_env(root), clear=False):
                entry = capture(root, "c" * 64)
                with self.assertRaises(StudioError):
                    restore(root, entry, "d" * 64)

    def test_identical_blobs_are_deduplicated(self):
        with tempfile.TemporaryDirectory() as td:
            root = self._root(td)
            with unittest.mock.patch.dict(os.environ, self._cas_env(root), clear=False):
                first = capture(root, "e" * 64)
                second = capture(root, "f" * 64)
                first_apk = first["files"][APK_REL]["sha256"]
                second_apk = second["files"][APK_REL]["sha256"]
                self.assertEqual(first_apk, second_apk)
                blobs = [p for p in (root / "cas").rglob("*") if p.is_file()]
                unique_digests = {
                    meta["sha256"]
                    for entry in (first, second)
                    for meta in entry["files"].values()
                }
                self.assertEqual(len(blobs), len(unique_digests))

    def test_gc_removes_unreferenced_blobs(self):
        with tempfile.TemporaryDirectory() as td:
            root = self._root(td)
            with unittest.mock.patch.dict(os.environ, self._cas_env(root), clear=False):
                first = capture(root, "1" * 64)
                (root / APK_REL).write_bytes(b"B" * 2048)
                second = capture(root, "2" * 64)
                stale = first["files"][APK_REL]["sha256"]
                stale_path = root / "cas" / stale[:2] / stale[2:]
                self.assertTrue(stale_path.exists())
                save({"2" * 64: second})
                self.assertFalse(stale_path.exists())

    def test_high_value_artifact_can_evict_low_value_entry_before_admission(self):
        with tempfile.TemporaryDirectory() as td:
            root = self._root(td)
            entries = {}
            with mock.patch.dict(os.environ, self._cas_env(root), clear=False):
                with mock.patch("immutable_artifact_cache.MAX_TOTAL_BYTES", 3000), mock.patch("immutable_artifact_cache.MAX_CAS_BYTES", 3000):
                    first_key = "7" * 64
                    first = capture(
                        root,
                        first_key,
                        rebuild_cost_seconds=1,
                        entries=entries,
                    )
                    entries[first_key] = first
                    old_apk_digest = first["files"][APK_REL]["sha256"]

                    (root / APK_REL).write_bytes(b"B" * 2048)
                    second_key = "8" * 64
                    second = capture(
                        root,
                        second_key,
                        rebuild_cost_seconds=100,
                        entries=entries,
                    )
                    entries[second_key] = second

                self.assertNotIn(first_key, entries)
                self.assertIn(second_key, entries)
                old_blob = root / "cas" / old_apk_digest[:2] / old_apk_digest[2:]
                self.assertFalse(old_blob.exists())


    def test_touch_moves_entry_to_most_recent_position(self):
        entries = {
            "a" * 64: {"validation_key": "a" * 64, "files": {}},
            "b" * 64: {"validation_key": "b" * 64, "files": {}},
        }
        touch(entries, "a" * 64)
        self.assertEqual(list(entries)[-1], "a" * 64)


if __name__ == "__main__":
    unittest.main()
