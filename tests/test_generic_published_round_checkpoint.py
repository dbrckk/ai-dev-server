"""Round-level recovery guarantees for generic autonomous projects."""

from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from execution_checkpoint import (
    ExecutionCheckpointError, advance, load as read_local, new,
)
from generic_project import _save_published_checkpoint
from github_execution_checkpoint_store import (
    load as read_remote, persist_local, restore_local,
)
from test_github_goal_store import FakeGitHub


class PublishedRoundCheckpointTests(unittest.TestCase):
    def test_two_published_rounds_restore_on_a_fresh_actions_runner(self):
        remote = FakeGitHub()
        with tempfile.TemporaryDirectory() as td:
            first = Path(td) / "runner-one" / ".autonomy" / "generic-execution-checkpoint.json"
            second = Path(td) / "runner-two" / ".autonomy" / "generic-execution-checkpoint.json"
            project_id = "isolated-generic-resume"
            calls = []

            def persist(checkpoint):
                # The local integrity-sealed state must exist before any
                # remote state branch mutation can begin.
                self.assertEqual(read_local(first), checkpoint)
                calls.append((checkpoint["round"], checkpoint["phase"]))
                persist_local(remote, project_id, first)

            checkpoint = new(project_id, "generic", "a" * 40)
            published_one = advance(
                checkpoint, base_sha="b" * 40, round_index=1,
                phase="published", last_verification={"passed": False},
            )
            _save_published_checkpoint(first, published_one, persist)
            published_two = advance(
                published_one, base_sha="c" * 40, round_index=2,
                phase="published", last_verification={"passed": True},
            )
            _save_published_checkpoint(first, published_two, persist)

            # Simulated crash before the enclosing goal cycle returns.
            self.assertFalse(second.exists())
            self.assertEqual(calls, [(1, "published"), (2, "published")])
            self.assertTrue(restore_local(remote, project_id, second))
            self.assertEqual(read_local(second), published_two)
            self.assertEqual(read_remote(remote, project_id), published_two)

    def test_complete_round_mirrors_final_checkpoint(self):
        remote = FakeGitHub()
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / ".autonomy" / "generic-execution-checkpoint.json"
            checkpoint = advance(
                new("complete-project", "generic", "a" * 40),
                round_index=1, phase="complete",
                last_verification={"passed": True},
            )
            _save_published_checkpoint(
                path, checkpoint,
                lambda value: persist_local(remote, value["project_id"], path),
            )
            self.assertEqual(read_remote(remote, "complete-project"), checkpoint)

    def test_unpublished_phase_never_reaches_remote_observer(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "checkpoint.json"
            called = []
            checkpoint = advance(
                new("test-project", "generic", "a" * 40),
                round_index=1, phase="planned",
            )
            with self.assertRaisesRegex(ExecutionCheckpointError, "published rounds"):
                _save_published_checkpoint(path, checkpoint, called.append)
            self.assertFalse(path.exists())
            self.assertEqual(called, [])

    def test_remote_failure_is_not_suppressed_after_local_save(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "checkpoint.json"
            checkpoint = advance(
                new("test-project", "generic", "a" * 40),
                round_index=1, phase="published",
            )

            def unavailable(_value):
                self.assertEqual(read_local(path), checkpoint)
                raise RuntimeError("checkpoint service unavailable")

            with self.assertRaisesRegex(RuntimeError, "checkpoint service unavailable"):
                _save_published_checkpoint(path, checkpoint, unavailable)
            self.assertEqual(read_local(path), checkpoint)


if __name__ == "__main__":
    unittest.main()
