from pathlib import Path
import json
import tempfile
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from failure_memory import FailureMemoryError, advance, load, new, resume, save


class FailureMemoryTests(unittest.TestCase):
    def test_persists_streak_bound_to_published_base(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "failure-memory.json"
            memory = new("demo", "generic", "a" * 40)
            memory = advance(
                memory,
                base_sha="b" * 40,
                signature="c" * 64,
                repeated_failures=3,
                avoid_providers=["p2", "p1"],
                avoid_models=["m2", "m1"],
            )
            save(path, memory)
            restored = load(path)
            self.assertEqual(restored["base_sha"], "b" * 40)
            self.assertEqual(restored["repeated_failures"], 3)
            self.assertEqual(restored["avoid_providers"], ["p1", "p2"])
            self.assertEqual(restored["avoid_models"], ["m1", "m2"])

    def test_base_mismatch_resets_memory(self):
        memory = advance(
            new("demo", "generic", "a" * 40),
            base_sha="a" * 40,
            signature="c" * 64,
            repeated_failures=2,
            avoid_providers=["p1"],
            avoid_models=["m1"],
        )
        restored = resume(
            memory,
            project_id="demo",
            engine="generic",
            base_sha="b" * 40,
        )
        self.assertEqual(restored["base_sha"], "b" * 40)
        self.assertEqual(restored["repeated_failures"], 0)
        self.assertIsNone(restored["signature"])

    def test_success_clears_streak(self):
        memory = advance(
            new("demo", "generic", "a" * 40),
            base_sha="b" * 40,
            signature=None,
            repeated_failures=0,
            avoid_providers=["ignored"],
            avoid_models=["ignored"],
        )
        self.assertEqual(memory["repeated_failures"], 0)
        self.assertIsNone(memory["signature"])
        self.assertEqual(memory["avoid_providers"], [])
        self.assertEqual(memory["avoid_models"], [])

    def test_tampering_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "failure-memory.json"
            save(path, new("demo", "generic", "a" * 40))
            value = json.loads(path.read_text())
            value["repeated_failures"] = 99
            path.write_text(json.dumps(value))
            with self.assertRaisesRegex(FailureMemoryError, "integrity"):
                load(path)


if __name__ == "__main__":
    unittest.main()
