import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from github_artifact_cas_audit_store import (
    ArtifactCasAuditStoreError,
    MAX_RECORDS,
    _validate,
)


class GitHubArtifactCasAuditStoreTests(unittest.TestCase):
    def test_accepts_monotonic_rows(self):
        rows = [
            {
                "sequence": 1,
                "project_namespace": "owner--app",
                "artifact_class": "public-test-fixture",
                "sha256": "a" * 64,
                "size": 10,
            },
            {
                "sequence": 2,
                "project_namespace": "owner--app",
                "artifact_class": "toolchain-template",
                "sha256": "b" * 64,
                "size": 20,
            },
        ]
        self.assertEqual(_validate(rows), rows)

    def test_rejects_non_monotonic_sequence(self):
        rows = [
            {
                "sequence": 2,
                "project_namespace": "owner--app",
                "artifact_class": "public-test-fixture",
                "sha256": "a" * 64,
                "size": 1,
            },
            {
                "sequence": 2,
                "project_namespace": "owner--app",
                "artifact_class": "public-test-fixture",
                "sha256": "b" * 64,
                "size": 1,
            },
        ]
        with self.assertRaises(ArtifactCasAuditStoreError):
            _validate(rows)

    def test_rejects_oversized_audit(self):
        rows = [
            {
                "sequence": index + 1,
                "project_namespace": "owner--app",
                "artifact_class": "public-test-fixture",
                "sha256": f"{index:064x}",
                "size": index,
            }
            for index in range(MAX_RECORDS + 1)
        ]
        with self.assertRaises(ArtifactCasAuditStoreError):
            _validate(rows)


if __name__ == "__main__":
    unittest.main()
