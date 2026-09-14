import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import workflow_checkpoint as wc


class WorkflowCheckpointTests(unittest.TestCase):
    def test_completed_checkpoint_roundtrip(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "checkpoint.json"
            with patch.dict(os.environ, {"STUDIO_CHECKPOINT_PATH": str(path)}, clear=False):
                key = wc.operation_key("release_fix", {"stage": "performance_qa", "x": 1})
                value = {"patch": {"files": [{"path": "lib/app.dart", "content": "x"}]}}
                wc.put(key, value, kind="release_fix")
                self.assertEqual(wc.get(key), value)

    def test_operation_key_is_deterministic_and_context_sensitive(self):
        first = wc.operation_key("release_fix", {"a": 1, "b": 2})
        second = wc.operation_key("release_fix", {"b": 2, "a": 1})
        changed = wc.operation_key("release_fix", {"a": 1, "b": 3})
        self.assertEqual(first, second)
        self.assertNotEqual(first, changed)

    def test_discard_removes_checkpoint(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "checkpoint.json"
            with patch.dict(os.environ, {"STUDIO_CHECKPOINT_PATH": str(path)}, clear=False):
                key = wc.operation_key("release_fix", {"x": 1})
                wc.put(key, {"ok": True}, kind="release_fix")
                wc.discard(key)
                self.assertIsNone(wc.get(key))

    def test_stale_writer_merges_existing_checkpoints(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "checkpoint.json"
            with patch.dict(os.environ, {"STUDIO_CHECKPOINT_PATH": str(path)}, clear=False):
                first = wc.operation_key("one", {"x": 1})
                second = wc.operation_key("two", {"x": 2})
                wc.put(first, {"value": 1}, kind="one")
                wc.put(second, {"value": 2}, kind="two")
                loaded = wc.load()
                self.assertIn(first, loaded)
                self.assertIn(second, loaded)


if __name__ == "__main__":
    unittest.main()
