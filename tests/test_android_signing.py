import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import zipfile
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from core import StudioError
from android_signing import (
    sign_aab,
    signing_credentials,
    strip_existing_signatures,
    valid_aab,
)


def make_aab(path: Path, *, signed=False):
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("BundleConfig.pb", b"cfg")
        z.writestr("base/manifest/AndroidManifest.xml", b"manifest")
        z.writestr("base/dex/classes.dex", b"dex")
        if signed:
            z.writestr("META-INF/MANIFEST.MF", b"manifest")
            z.writestr("META-INF/OLD.SF", b"sf")
            z.writestr("META-INF/OLD.RSA", b"rsa")


class AndroidSigningTests(unittest.TestCase):
    def test_signature_metadata_is_removed_from_copy(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "source.aab"
            clean = root / "clean.aab"
            make_aab(source, signed=True)
            evidence = strip_existing_signatures(source, clean)
            self.assertTrue(valid_aab(clean))
            self.assertEqual(
                evidence["removed_signature_entries"],
                ["META-INF/MANIFEST.MF", "META-INF/OLD.RSA", "META-INF/OLD.SF"],
            )
            with zipfile.ZipFile(clean) as z:
                self.assertNotIn("META-INF/OLD.RSA", z.namelist())

    def test_credentials_reject_keystore_inside_project_workspace(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            key = root / "upload.jks"
            key.write_bytes(b"key")
            env = {
                "STUDIO_ANDROID_UPLOAD_KEYSTORE_PATH": str(key),
                "STUDIO_ANDROID_UPLOAD_KEY_ALIAS": "upload",
                "STUDIO_ANDROID_UPLOAD_STORE_PASSWORD": "secret",
            }
            with self.assertRaisesRegex(StudioError, "outside project workspace"):
                signing_credentials(env, project_root=root)

    def test_missing_credentials_are_explicit_but_not_exceptional(self):
        result = signing_credentials({})
        self.assertFalse(result["available"])
        self.assertEqual(result["blocker"], "android_upload_keystore_required")

    def test_signer_never_places_password_on_command_line(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            unsigned = root / "u.aab"
            signed = root / "s.aab"
            key = root / "upload.jks"
            key.write_bytes(b"key")
            make_aab(unsigned, signed=True)
            calls = []

            def runner(cmd, **kwargs):
                calls.append((list(cmd), dict(kwargs.get("env", {}))))
                if cmd[0] == "jarsigner" and "-verify" not in cmd:
                    make_aab(signed, signed=True)
                    return subprocess.CompletedProcess(cmd, 0, stdout=b"signed")
                if cmd[0] == "jarsigner":
                    return subprocess.CompletedProcess(cmd, 0, stdout=b"jar verified.")
                return subprocess.CompletedProcess(
                    cmd, 0, stdout=("SHA256: " + ":".join(["AA"] * 32)).encode()
                )

            result = sign_aab(
                unsigned,
                signed,
                key,
                "upload",
                "StoreSecret",
                "KeySecret",
                runner=runner,
            )

        self.assertTrue(result["passed"])
        self.assertTrue(all("StoreSecret" not in " ".join(cmd) for cmd, _ in calls))
        self.assertTrue(all("KeySecret" not in " ".join(cmd) for cmd, _ in calls))
        self.assertEqual(calls[0][1]["STUDIO_AAB_STOREPASS"], "StoreSecret")
        self.assertEqual(calls[0][1]["STUDIO_AAB_KEYPASS"], "KeySecret")
        self.assertEqual(result["signing_scope"], "artifact_only")
        self.assertFalse(result["project_code_had_signing_material"])


if __name__ == "__main__":
    unittest.main()
