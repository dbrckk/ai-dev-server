import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import artifact_cas
from core import StudioError


class ArtifactCasTests(unittest.TestCase):
    def test_put_get_and_deduplicate(self):
        with tempfile.TemporaryDirectory() as td:
            env = {
                "STUDIO_ARTIFACT_CAS_PATH": str(Path(td) / "cas"),
                "STUDIO_ARTIFACT_CAS_STATS_PATH": str(Path(td) / "stats.json"),
                "STUDIO_PROJECT_ID": "project-a",
            }
            with mock.patch.dict(os.environ, env, clear=False):
                first = artifact_cas.put(b"payload")
                second = artifact_cas.put(b"payload")
                self.assertEqual(first, second)
                self.assertEqual(
                    artifact_cas.get(first["sha256"], first["size"]),
                    b"payload",
                )
                blobs = [
                    p for p in (Path(td) / "cas").rglob("*")
                    if p.is_file() and not p.name.endswith(".tmp")
                ]
                self.assertEqual(len(blobs), 1)

    def test_corrupt_blob_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            env = {
                "STUDIO_ARTIFACT_CAS_PATH": str(Path(td) / "cas"),
                "STUDIO_ARTIFACT_CAS_STATS_PATH": str(Path(td) / "stats.json"),
                "STUDIO_PROJECT_ID": "project-a",
            }
            with mock.patch.dict(os.environ, env, clear=False):
                meta = artifact_cas.put(b"payload")
                artifact_cas.blob_path(meta["sha256"]).write_bytes(b"corrupt")
                with self.assertRaises(StudioError):
                    artifact_cas.get(meta["sha256"], meta["size"])

    def test_physical_quota_rejects_new_blob_atomically(self):
        with tempfile.TemporaryDirectory() as td:
            env = {
                "STUDIO_ARTIFACT_CAS_PATH": str(Path(td) / "cas"),
                "STUDIO_ARTIFACT_CAS_STATS_PATH": str(Path(td) / "stats.json"),
                "STUDIO_PROJECT_ID": "project-a",
            }
            with mock.patch.dict(os.environ, env, clear=False), mock.patch.object(
                artifact_cas, "MAX_CAS_BYTES", 10
            ):
                artifact_cas.put(b"12345")
                with self.assertRaises(StudioError):
                    artifact_cas.put(b"abcdefghij")
                self.assertEqual(artifact_cas.usage(), 5)

    def test_private_same_blob_is_physically_isolated_per_project(self):
        with tempfile.TemporaryDirectory() as td:
            base = {
                "STUDIO_ARTIFACT_CAS_PATH": str(Path(td) / "cas"),
                "STUDIO_ARTIFACT_CAS_STATS_PATH": str(Path(td) / "stats.json"),
            }
            with mock.patch.dict(os.environ, {**base, "STUDIO_PROJECT_ID": "project-a"}, clear=False):
                first = artifact_cas.put(b"same")
                first_path = artifact_cas.blob_path(first["sha256"])
            with mock.patch.dict(os.environ, {**base, "STUDIO_PROJECT_ID": "project-b"}, clear=False):
                second = artifact_cas.put(b"same")
                second_path = artifact_cas.blob_path(second["sha256"])

            self.assertEqual(first["sha256"], second["sha256"])
            self.assertNotEqual(first_path, second_path)
            self.assertTrue(first_path.is_file())
            self.assertTrue(second_path.is_file())

    def test_shareable_blob_uses_common_scope_only_when_explicit(self):
        with tempfile.TemporaryDirectory() as td:
            base = {
                "STUDIO_ARTIFACT_CAS_PATH": str(Path(td) / "cas"),
                "STUDIO_ARTIFACT_CAS_STATS_PATH": str(Path(td) / "stats.json"),
            }
            with mock.patch.dict(os.environ, {**base, "STUDIO_PROJECT_ID": "project-a"}, clear=False):
                first = artifact_cas.put(b"public", shareable=True)
                first_path = artifact_cas.blob_path(first["sha256"], shareable=True)
            with mock.patch.dict(os.environ, {**base, "STUDIO_PROJECT_ID": "project-b"}, clear=False):
                second = artifact_cas.put(b"public", shareable=True)
                second_path = artifact_cas.blob_path(second["sha256"], shareable=True)

            self.assertEqual(first_path, second_path)
            self.assertIn("/shared/", first_path.as_posix())

    def test_gc_keeps_only_referenced_digest(self):
        with tempfile.TemporaryDirectory() as td:
            env = {
                "STUDIO_ARTIFACT_CAS_PATH": str(Path(td) / "cas"),
                "STUDIO_ARTIFACT_CAS_STATS_PATH": str(Path(td) / "stats.json"),
                "STUDIO_PROJECT_ID": "project-a",
            }
            with mock.patch.dict(os.environ, env, clear=False):
                keep = artifact_cas.put(b"keep")
                drop = artifact_cas.put(b"drop")
                result = artifact_cas.gc({keep["sha256"]})
                self.assertEqual(result["removed"], 1)
                self.assertTrue(artifact_cas.blob_path(keep["sha256"]).is_file())
                self.assertFalse(artifact_cas.blob_path(drop["sha256"]).exists())


if __name__ == "__main__":
    unittest.main()
