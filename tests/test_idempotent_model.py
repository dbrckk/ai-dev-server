import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from idempotent_model import ask


class FakeModel:
    def __init__(self):
        self.calls = 0
        self.network_calls = 0

    def ask(self, role, context, screenshots=()):
        self.calls += 1
        self.network_calls += 1
        return {"files": [{"path": "lib/app.dart", "content": "ok"}]}


class IdempotentModelTests(unittest.TestCase):
    def test_replay_after_crash_does_not_call_model_twice(self):
        with tempfile.TemporaryDirectory() as td:
            checkpoint = Path(td) / "checkpoints.json"
            with patch.dict(os.environ, {"STUDIO_CHECKPOINT_PATH": str(checkpoint)}, clear=False):
                first_model = FakeModel()
                first, reused_first, key_first = ask(
                    first_model, "implementation", '{"task":"x"}', namespace="preview-implementation"
                )
                self.assertEqual(first_model.calls, 1)
                self.assertFalse(reused_first)

                restarted_model = FakeModel()
                second, reused_second, key_second = ask(
                    restarted_model, "implementation", '{"task":"x"}', namespace="preview-implementation"
                )

                self.assertEqual(restarted_model.network_calls, 0)
                self.assertEqual(restarted_model.calls, 1)
                self.assertEqual(restarted_model.checkpoint_replays, 1)
                self.assertTrue(reused_second)
                self.assertEqual(first, second)
                self.assertEqual(key_first, key_second)

    def test_changed_context_causes_new_call(self):
        with tempfile.TemporaryDirectory() as td:
            checkpoint = Path(td) / "checkpoints.json"
            with patch.dict(os.environ, {"STUDIO_CHECKPOINT_PATH": str(checkpoint)}, clear=False):
                model = FakeModel()
                ask(model, "implementation", '{"task":"a"}')
                ask(model, "implementation", '{"task":"b"}')
                self.assertEqual(model.calls, 2)


if __name__ == "__main__":
    unittest.main()
