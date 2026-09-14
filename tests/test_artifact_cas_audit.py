import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import artifact_cas_audit as audit


class ArtifactCasAuditTests(unittest.TestCase):
    def test_records_monotonic_sequence(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "audit.json"
            with mock.patch.dict(
                os.environ,
                {"STUDIO_ARTIFACT_CAS_AUDIT_PATH": str(path)},
                clear=False,
            ):
                first = audit.record(
                    project_id="Owner/App",
                    artifact_class="public-test-fixture",
                    digest="a" * 64,
                    size=10,
                )
                second = audit.record(
                    project_id="Owner/App",
                    artifact_class="toolchain-template",
                    digest="b" * 64,
                    size=20,
                )
                rows = audit.load()

        self.assertEqual(first["sequence"], 1)
        self.assertEqual(second["sequence"], 2)
        self.assertEqual(rows[-1]["sequence"], 2)
        self.assertEqual(rows[0]["project_namespace"], "owner--app")

    def test_audit_is_bounded(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "audit.json"
            with mock.patch.dict(
                os.environ,
                {"STUDIO_ARTIFACT_CAS_AUDIT_PATH": str(path)},
                clear=False,
            ), mock.patch.object(audit, "MAX_RECORDS", 3):
                for index in range(5):
                    audit.record(
                        project_id="owner/app",
                        artifact_class="public-test-fixture",
                        digest=f"{index:064x}",
                        size=index,
                    )
                rows = audit.load()

        self.assertEqual(len(rows), 3)
        self.assertEqual([row["sequence"] for row in rows], [3, 4, 5])


if __name__ == "__main__":
    unittest.main()
