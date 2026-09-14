import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from artifact_cas_namespace import project_namespace, scoped_digest
from core import StudioError


class ArtifactCasNamespaceTests(unittest.TestCase):
    def test_repository_id_becomes_safe_namespace(self):
        self.assertEqual(project_namespace("Owner/App"), "owner--app")

    def test_unsafe_project_id_is_hashed(self):
        value = project_namespace("Private App / customer α")
        self.assertTrue(value.startswith("project-"))
        self.assertEqual(len(value), 32)

    def test_same_blob_is_scoped_differently_per_project(self):
        digest = "a" * 64
        self.assertNotEqual(
            scoped_digest("owner/app-a", digest),
            scoped_digest("owner/app-b", digest),
        )

    def test_invalid_content_digest_is_rejected(self):
        with self.assertRaises(StudioError):
            scoped_digest("owner/app", "bad")


if __name__ == "__main__":
    unittest.main()
