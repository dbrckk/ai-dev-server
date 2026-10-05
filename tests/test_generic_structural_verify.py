from pathlib import Path
import tempfile
import unittest

from studio.generic_verify import verify_structural_text_changes


class GenericStructuralVerifyTests(unittest.TestCase):
    def test_accepts_bounded_text_and_json_changes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / ".production-os").mkdir()
            (root / ".production-os" / "worker-canary-7.txt").write_text(
                "production-os-worker-canary sequence 7\n",
                encoding="utf-8",
            )
            (root / "metadata.json").write_text('{"ok": true}\n', encoding="utf-8")
            result = verify_structural_text_changes(
                root,
                [".production-os/worker-canary-7.txt", "metadata.json"],
            )
            self.assertTrue(result["passed"])
            self.assertTrue(result["structural_only"])
            self.assertEqual(len(result["files"]), 2)
            self.assertEqual(len(result["files"][0]["sha256"]), 64)

    def test_source_code_change_requires_executable_verification(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "app.py").write_text("print('ok')\n", encoding="utf-8")
            result = verify_structural_text_changes(root, ["app.py"])
            self.assertEqual(result["status"], "not_applicable")
            self.assertFalse(result["passed"])

    def test_invalid_json_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "metadata.json").write_text("{broken", encoding="utf-8")
            result = verify_structural_text_changes(root, ["metadata.json"])
            self.assertEqual(result["status"], "failed")
            self.assertFalse(result["passed"])
            self.assertEqual(result["reason"], "changed JSON is invalid")

    def test_secret_like_text_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "note.txt").write_text(
                "token ghp_abcdefghijklmnopqrstuvwxyz123456\n",
                encoding="utf-8",
            )
            result = verify_structural_text_changes(root, ["note.txt"])
            self.assertEqual(result["status"], "failed")
            self.assertFalse(result["passed"])


if __name__ == "__main__":
    unittest.main()
