import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import atomic_file


class AtomicFileTests(unittest.TestCase):
    def test_write_bytes_replaces_existing_file_without_temp_leak(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            path = root / "state.json"
            path.write_bytes(b"old")

            atomic_file.write_bytes(path, b"new")

            self.assertEqual(path.read_bytes(), b"new")
            self.assertEqual(list(root.glob(".state.json.*.tmp")), [])

    def test_replace_failure_preserves_previous_file_and_cleans_temp(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            path = root / "state.json"
            path.write_bytes(b"stable")

            with mock.patch("atomic_file.os.replace", side_effect=OSError("replace failed")):
                with self.assertRaises(OSError):
                    atomic_file.write_bytes(path, b"partial")

            self.assertEqual(path.read_bytes(), b"stable")
            self.assertEqual(list(root.glob(".state.json.*.tmp")), [])

    def test_write_text_uses_utf8(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "unicode.txt"
            atomic_file.write_text(path, "évidence")
            self.assertEqual(path.read_text(encoding="utf-8"), "évidence")


if __name__ == "__main__":
    unittest.main()
