import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from durable_state import save as save_state
from workflow_checkpoint import operation_key, put as put_checkpoint
from release_readiness import assess


class ReleaseReadinessTests(unittest.TestCase):
    def test_complete_project_is_ready(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            autonomy = root / ".autonomy"
            autonomy.mkdir()
            (root / "report.json").write_text(json.dumps({
                "release_status": "store_ready",
                "completion": {"finished": True},
            }))
            save_state(autonomy / "runtime-state.json", {"status": "complete"})
            checkpoint_path = autonomy / "workflow-checkpoints.json"
            with patch.dict(os.environ, {"STUDIO_CHECKPOINT_PATH": str(checkpoint_path)}, clear=False):
                key = operation_key("test", {"x": 1})
                put_checkpoint(key, {"ok": True}, kind="test")

            result = assess(root)

            self.assertTrue(result["ready"])
            self.assertEqual(result["failures"], [])

    def test_incomplete_project_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            root.mkdir(exist_ok=True)
            (root / "report.json").write_text(json.dumps({
                "release_status": "not_store_ready",
                "completion": {"finished": False},
            }))

            result = assess(root)

            self.assertFalse(result["ready"])
            self.assertIn("completion_not_finished", result["failures"])
            self.assertIn("release_not_store_ready", result["failures"])


if __name__ == "__main__":
    unittest.main()
