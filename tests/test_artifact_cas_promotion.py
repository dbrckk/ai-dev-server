import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import artifact_cas
from artifact_cas_promotion import ATTESTATION, promote_private
from core import StudioError


class ArtifactCasPromotionTests(unittest.TestCase):
    def _env(self, td):
        return {
            "STUDIO_ARTIFACT_CAS_PATH": str(Path(td) / "cas"),
            "STUDIO_ARTIFACT_CAS_STATS_PATH": str(Path(td) / "stats.json"),
            "STUDIO_PROJECT_ID": "project-a",
        }

    def test_promotes_explicit_safe_text_fixture(self):
        with tempfile.TemporaryDirectory() as td:
            with mock.patch.dict(os.environ, self._env(td), clear=False):
                private = artifact_cas.put(b'{"fixture":"public"}')
                result = promote_private(
                    private["sha256"],
                    private["size"],
                    artifact_class="public-test-fixture",
                    attestation=ATTESTATION,
                )
                shared = artifact_cas.get(
                    private["sha256"],
                    private["size"],
                    shareable=True,
                    artifact_class="public-test-fixture",
                )

            self.assertEqual(result["status"], "promoted")
            self.assertEqual(shared, b'{"fixture":"public"}')

    def test_requires_exact_public_attestation(self):
        with tempfile.TemporaryDirectory() as td:
            with mock.patch.dict(os.environ, self._env(td), clear=False):
                private = artifact_cas.put(b"public text")
                with self.assertRaises(StudioError):
                    promote_private(
                        private["sha256"],
                        private["size"],
                        artifact_class="public-test-fixture",
                        attestation="yes",
                    )

    def test_rejects_binary_payload(self):
        with tempfile.TemporaryDirectory() as td:
            with mock.patch.dict(os.environ, self._env(td), clear=False):
                private = artifact_cas.put(b"\x00\xff\x00\xff")
                with self.assertRaises(StudioError):
                    promote_private(
                        private["sha256"],
                        private["size"],
                        artifact_class="public-test-fixture",
                        attestation=ATTESTATION,
                    )

    def test_rejects_secret_marker(self):
        with tempfile.TemporaryDirectory() as td:
            with mock.patch.dict(os.environ, self._env(td), clear=False):
                private = artifact_cas.put(b"token=ghp_example_secret")
                with self.assertRaises(StudioError):
                    promote_private(
                        private["sha256"],
                        private["size"],
                        artifact_class="public-test-fixture",
                        attestation=ATTESTATION,
                    )


if __name__ == "__main__":
    unittest.main()
