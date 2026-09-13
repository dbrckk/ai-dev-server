from pathlib import Path
import json
import tempfile
import unittest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from execution_checkpoint import ExecutionCheckpointError, advance, load, new, resume, save


class ExecutionCheckpointTests(unittest.TestCase):
    def test_round_and_verification_resume_from_published_commit(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "checkpoint.json"
            checkpoint = new("demo", "generic", "a" * 40)
            checkpoint = advance(
                checkpoint,
                base_sha="b" * 40,
                round_index=3,
                phase="published",
                last_verification={"passed": True, "status": "passed"},
            )
            save(path, checkpoint)
            restored = load(path)
            self.assertEqual(restored["round"], 3)
            self.assertEqual(restored["base_sha"], "b" * 40)
            self.assertTrue(restored["last_verification"]["passed"])

    def test_tampering_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "checkpoint.json"
            checkpoint = new("demo", "generic", "a" * 40)
            save(path, checkpoint)
            value = json.loads(path.read_text())
            value["round"] = 99
            path.write_text(json.dumps(value))
            with self.assertRaisesRegex(ExecutionCheckpointError, "integrity"):
                load(path)

    def test_interrupted_verified_round_resets_to_authoritative_base(self):
        checkpoint = new("demo", "generic", "a" * 40)
        checkpoint = advance(
            checkpoint,
            round_index=3,
            phase="verified",
            last_verification={"passed": True},
        )
        restored = resume(
            checkpoint,
            project_id="demo",
            engine="generic",
            base_sha="a" * 40,
        )
        self.assertEqual(restored["round"], 0)
        self.assertEqual(restored["phase"], "restored")
        self.assertIsNone(restored["last_verification"])

    def test_published_round_is_preserved_for_resume(self):
        checkpoint = new("demo", "generic", "a" * 40)
        checkpoint = advance(
            checkpoint,
            base_sha="b" * 40,
            round_index=2,
            phase="published",
            last_verification={"passed": False},
        )
        restored = resume(
            checkpoint,
            project_id="demo",
            engine="generic",
            base_sha="b" * 40,
        )
        self.assertEqual(restored["round"], 2)
        self.assertEqual(restored["phase"], "published")
        self.assertFalse(restored["last_verification"]["passed"])

    def test_round_cannot_regress(self):
        checkpoint = new("demo", "generic", "a" * 40)
        checkpoint = advance(checkpoint, round_index=4, phase="published")
        with self.assertRaisesRegex(ExecutionCheckpointError, "regression"):
            advance(checkpoint, round_index=3, phase="planned")


if __name__ == "__main__":
    unittest.main()
