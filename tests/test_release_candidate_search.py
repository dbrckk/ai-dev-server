import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from release_candidate_search import apply_winner, run_candidate, select_winner


STATE = {
    "product": {
        "journeys": [
            {
                "id": "launch",
                "title": "Launch",
                "steps": ["Open the application"],
                "expected": ["Main screen is visible"],
            }
        ]
    }
}


class PassingSandbox:
    def __init__(self, root):
        self.root = root

    def gates(self, name, journeys):
        return True, [{"command": ["flutter", "test"], "exit_code": 0, "output": ""}]


class FailingSandbox:
    def __init__(self, root):
        self.root = root

    def gates(self, name, journeys):
        return False, [{"command": ["flutter", "test"], "exit_code": 1, "output": "failed"}]


class ReleaseCandidateSearchTests(unittest.TestCase):
    def test_candidate_isolation_restores_workspace(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "lib/app.dart"
            source.parent.mkdir(parents=True)
            source.write_text("base\n")

            def mutate():
                source.write_text("candidate\n")
                return {"model_calls": 1}

            candidate = run_candidate(
                root,
                strategy="model_only",
                strategy_prior_score=10,
                mutate=mutate,
                state=STATE,
                app_name="demo_app",
                sandbox_factory=PassingSandbox,
            )

            self.assertTrue(candidate["passed"])
            self.assertEqual(source.read_text(), "base\n")
            self.assertEqual(candidate["changed_files"], ["lib/app.dart"])

    def test_generated_flutter_artifacts_are_purged_between_candidates(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "lib/app.dart"
            source.parent.mkdir(parents=True)
            source.write_text("base\n")

            def mutate():
                source.write_text("candidate\n")
                (root / "build").mkdir()
                (root / "build/stale.txt").write_text("stale")
                (root / ".dart_tool").mkdir()
                (root / ".dart_tool/stale.txt").write_text("stale")
                goldens = root / "test/goldens"
                goldens.mkdir(parents=True)
                (goldens / "stale.png").write_bytes(b"png")
                return {"model_calls": 1}

            candidate = run_candidate(
                root,
                strategy="model_only",
                strategy_prior_score=10,
                mutate=mutate,
                state=STATE,
                app_name="demo_app",
                sandbox_factory=PassingSandbox,
            )

            self.assertTrue(candidate["passed"])
            self.assertFalse((root / "build").exists())
            self.assertFalse((root / ".dart_tool").exists())
            self.assertFalse((root / "test/goldens").exists())
            self.assertEqual(source.read_text(), "base\n")


    def test_failed_candidate_cannot_contaminate_next_candidate(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "lib/app.dart"
            source.parent.mkdir(parents=True)
            source.write_text("base\n")

            def bad():
                source.write_text("bad\n")
                return {"model_calls": 1}

            first = run_candidate(
                root,
                strategy="model_only",
                strategy_prior_score=30,
                mutate=bad,
                state=STATE,
                app_name="demo_app",
                sandbox_factory=FailingSandbox,
            )
            self.assertFalse(first["passed"])
            self.assertEqual(source.read_text(), "base\n")

            def good():
                self.assertEqual(source.read_text(), "base\n")
                source.write_text("good\n")
                return {"model_calls": 0}

            second = run_candidate(
                root,
                strategy="agent_only",
                strategy_prior_score=20,
                mutate=good,
                state=STATE,
                app_name="demo_app",
                sandbox_factory=PassingSandbox,
            )
            self.assertTrue(second["passed"])

    def test_verified_candidate_with_better_score_wins(self):
        candidates = [
            {
                "strategy": "model_only",
                "passed": True,
                "strategy_prior_score": 20,
                "changed_files": ["lib/a.dart", "lib/b.dart"],
                "model_calls": 1,
                "elapsed_seconds": 30,
            },
            {
                "strategy": "agent_only",
                "passed": True,
                "strategy_prior_score": 18,
                "changed_files": ["lib/a.dart"],
                "model_calls": 0,
                "elapsed_seconds": 10,
            },
        ]
        winner = select_winner(candidates)
        self.assertEqual(winner["strategy"], "agent_only")

    def test_apply_winner_materializes_only_selected_patch(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "lib/app.dart"
            source.parent.mkdir(parents=True)
            source.write_text("base\n")

            apply_winner(
                root,
                {
                    "files": [
                        {"path": "lib/app.dart", "content": "winner\n"},
                    ]
                },
            )
            self.assertEqual(source.read_text(), "winner\n")


if __name__ == "__main__":
    unittest.main()
