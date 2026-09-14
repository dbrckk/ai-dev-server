import base64
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from core import StudioError
from immutable_artifact_cache import APK_REL, capture, restore, verify_entry


class ImmutableArtifactCacheTests(unittest.TestCase):
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
            entry = capture(root, key)
            apk_meta = entry["files"][APK_REL]
            payload = bytearray(base64.b64decode(apk_meta["content_base64"]))
            payload[0] ^= 0x01
            apk_meta["content_base64"] = base64.b64encode(bytes(payload)).decode("ascii")

            with self.assertRaises(StudioError):
                verify_entry(entry, key)

    def test_validation_key_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = self._root(td)
            entry = capture(root, "c" * 64)
            with self.assertRaises(StudioError):
                restore(root, entry, "d" * 64)


if __name__ == "__main__":
    unittest.main()
