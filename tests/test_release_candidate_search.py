import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from release_candidate_search import apply_winner, run_branch, run_candidate, select_winner


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

    def quick_gates(self):
        return True, [{"command": ["flutter", "analyze"], "exit_code": 0, "output": ""}]

    def gates(self, name, journeys):
        return True, [{"command": ["flutter", "test"], "exit_code": 0, "output": ""}]


class FailingSandbox:
    def __init__(self, root):
        self.root = root

    def quick_gates(self):
        return False, [{"command": ["flutter", "analyze"], "exit_code": 1, "output": "failed"}]

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

    def test_failed_first_gate_gets_one_local_refinement(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "lib/app.dart"
            source.parent.mkdir(parents=True)
            source.write_text("base\n")
            gate_calls = {"count": 0}

            class FlakySandbox:
                def __init__(self, root):
                    self.root = root

                def gates(self, name, journeys):
                    gate_calls["count"] += 1
                    if gate_calls["count"] == 1:
                        return False, [{"command": ["flutter", "test"], "exit_code": 1, "output": "first failure"}]
                    return True, [{"command": ["flutter", "test"], "exit_code": 0, "output": ""}]

            def first_step():
                source.write_text("first\n")
                return {"model_calls": 1}

            def refine(failure):
                self.assertIn("first failure", failure)
                source.write_text("refined\n")
                return {"model_calls": 1}

            candidate = run_branch(
                root,
                strategy="model_only",
                strategy_prior_score=10,
                steps=[first_step],
                refine=refine,
                state=STATE,
                app_name="demo_app",
                sandbox_factory=FlakySandbox,
                strategy_row={
                    "conservative_success_rate": 0.8,
                    "risk": 0.2,
                    "estimated_seconds": 20,
                    "estimated_model_calls": 1,
                },
                remaining_model_calls=2,
            )

            self.assertTrue(candidate["passed"])
            self.assertEqual(candidate["refinements"], 1)
            self.assertEqual(candidate["model_calls"], 2)
            self.assertEqual(len(candidate["steps"]), 2)
            self.assertEqual(source.read_text(), "base\n")

    def test_multi_step_branch_preserves_step_order(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "lib/app.dart"
            source.parent.mkdir(parents=True)
            source.write_text("base\n")
            order = []

            def agent_step():
                order.append("agent")
                source.write_text("agent\n")
                return {"model_calls": 0, "agent": {"agent": "fake"}}

            def model_step():
                order.append("model")
                self.assertEqual(source.read_text(), "agent\n")
                source.write_text("agent+model\n")
                return {"model_calls": 1}

            candidate = run_branch(
                root,
                strategy="agent_to_model",
                strategy_prior_score=10,
                steps=[agent_step, model_step],
                refine=None,
                state=STATE,
                app_name="demo_app",
                sandbox_factory=PassingSandbox,
            )

            self.assertTrue(candidate["passed"])
            self.assertEqual(order, ["agent", "model"])
            self.assertEqual(candidate["model_calls"], 1)
            self.assertEqual(source.read_text(), "base\n")


    def test_failed_quick_gate_prunes_unpromising_branch_before_full_gates(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "lib/app.dart"
            source.parent.mkdir(parents=True)
            source.write_text("base\n")
            full_gate_calls = {"count": 0}

            class PruningSandbox:
                def __init__(self, root):
                    self.root = root

                def quick_gates(self):
                    return False, [{"command": ["flutter", "analyze"], "exit_code": 1, "output": "compile failure"}]

                def gates(self, name, journeys):
                    full_gate_calls["count"] += 1
                    return True, []

            def first_step():
                source.write_text("broken\n")
                return {"model_calls": 1}

            def second_step():
                source.write_text("should-not-run\n")
                return {"model_calls": 1}

            candidate = run_branch(
                root,
                strategy="model_to_agent",
                strategy_prior_score=0,
                steps=[first_step, second_step],
                refine=None,
                state=STATE,
                app_name="demo_app",
                sandbox_factory=PruningSandbox,
                strategy_row={
                    "conservative_success_rate": 0.0,
                    "risk": 1.0,
                    "estimated_seconds": 100,
                    "estimated_model_calls": 1,
                },
                remaining_model_calls=2,
                step_model_calls=[1, 1],
            )

            self.assertFalse(candidate["passed"])
            self.assertEqual(full_gate_calls["count"], 0)
            self.assertIn("pruned", candidate["failure"])
            self.assertEqual(source.read_text(), "base\n")


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
