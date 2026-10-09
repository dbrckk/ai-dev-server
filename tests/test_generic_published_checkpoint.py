"""Integrity and ordering guarantees for intra-cycle published-round checkpoints."""
import tempfile
import unittest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from execution_checkpoint import (
    ExecutionCheckpointError,
    advance, load, new,
)
from generic_project import _save_published_checkpoint


class GenericPublishedCheckpointTests(unittest.TestCase):
    def test_observer_reads_sealed_checkpoint_after_verified_round(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / ".autonomy/generic-execution-checkpoint.json"
            checkpoint = advance(
                new("demo-project", "generic", "a" * 40),
                base_sha="b" * 40,
                round_index=2,
                phase="published",
                last_verification={"passed": True, "checks": 3},
            )
            observed = []

            def observer(value):
                self.assertEqual(load(path), checkpoint)
                self.assertEqual(value, checkpoint)
                observed.append(value)

            _save_published_checkpoint(path, checkpoint, observer)
            self.assertEqual(observed, [checkpoint])
            self.assertEqual(load(path)["base_sha"], "b" * 40)

    def test_unpublished_phase_is_rejected_and_not_persisted(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "checkpoint.json"
            checkpoint = advance(
                new("demo-project", "generic", "a" * 40),
                round_index=1,
                phase="planned",
            )
            seen = []
            with self.assertRaisesRegex(
                ExecutionCheckpointError, "only published rounds",
            ):
                _save_published_checkpoint(path, checkpoint, seen.append)
            self.assertFalse(path.exists())
            self.assertEqual(seen, [])

    def test_remote_persistence_failure_stops_after_local_commit(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "checkpoint.json"
            checkpoint = advance(
                new("demo-project", "generic", "a" * 40),
                round_index=1,
                phase="complete",
                last_verification={"passed": True},
            )

            def failure(_value):
                raise RuntimeError("remote checkpoint rejected")

            with self.assertRaisesRegex(RuntimeError, "remote checkpoint rejected"):
                _save_published_checkpoint(path, checkpoint, failure)
            self.assertEqual(load(path), checkpoint)

    def test_missing_observer_keeps_original_local_behavior(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "checkpoint.json"
            checkpoint = advance(
                new("demo-project", "generic", "a" * 40),
                round_index=1,
                phase="published",
                last_verification={"passed": False},
            )
            _save_published_checkpoint(path, checkpoint)
            self.assertEqual(load(path), checkpoint)


if __name__ == "__main__":
    unittest.main()
