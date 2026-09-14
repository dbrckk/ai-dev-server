import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from core import StudioError
from release_repair import _model_mutation, _persist_caches, attempt
from unittest.mock import patch


STATE = {
    "product": {
        "journeys": [
            {
                "id": "launch",
                "steps": [
                    {"action": "tap", "key": "start_button"},
                    {"action": "expect_text", "value": "Ready"},
                ],
            }
        ]
    }
}

class NeverModel:
    def __init__(self, limit):
        raise AssertionError("model must not be constructed")


class ReleaseRepairTests(unittest.TestCase):
    def test_credentials_abort_before_model_call(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "lib/app.dart"
            source.parent.mkdir(parents=True)
            source.write_text("const token = 'sk-abcdefghijklmnopqrstuvwxyz123456';\n")

            with self.assertRaises(StudioError):
                attempt(
                    root,
                    STATE,
                    {"passed": False, "blockers": ["excessive_jank"]},
                    "performance_qa",
                    "demo_app",
                    model_factory=NeverModel,
                )

    @patch("release_repair._agent_candidates", return_value=["fake-agent"])
    @patch("release_repair._run_agent")
    def test_credentials_abort_before_agent_access(self, run_agent, candidates):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "lib/app.dart"
            source.parent.mkdir(parents=True)
            source.write_text("const token = 'sk-abcdefghijklmnopqrstuvwxyz123456';\n")

            with self.assertRaises(StudioError):
                attempt(
                    root,
                    STATE,
                    {"passed": False, "blockers": ["excessive_jank"]},
                    "performance_qa",
                    "demo_app",
                )

        run_agent.assert_not_called()

    @patch("release_repair._agent_candidates", return_value=["fake-agent"])
    @patch("release_repair.choose_strategy")
    @patch("release_repair._run_agent")
    def test_agent_only_strategy_uses_no_model_call(self, run_agent, choose_strategy, candidates):
        choose_strategy.return_value = {
            "strategy": "agent_only",
            "mode": "test",
            "metrics": {},
            "allowed": ["agent_only", "model_only"],
            "evidence_source": "global",
            "candidate_ranking": [
                {
                    "strategy": "agent_only",
                    "score": 50.0,
                    "conservative_success_rate": 0.8,
                    "estimated_seconds": 10.0,
                    "risk": 0.2,
                    "estimated_model_calls": 0,
                    "mature": True,
                },
                {
                    "strategy": "model_only",
                    "score": 40.0,
                    "conservative_success_rate": 0.7,
                    "estimated_seconds": 20.0,
                    "risk": 0.15,
                    "estimated_model_calls": 1,
                    "mature": True,
                },
            ],
        }

        def edit(root, blockers, stage, failure=None):
            source = root / "lib/app.dart"
            source.write_text("const endpoint = 'https://example.com';\n")
            return {"agent": "fake-agent", "attempts": [], "changed": ["lib/app.dart"]}

        run_agent.side_effect = edit

        class PassingSandbox:
            def __init__(self, root):
                self.root = root

            def gates(self, name, journeys):
                return True, [{"command": ["flutter", "test"], "exit_code": 0, "output": ""}]

        class CandidateModel:
            def __init__(self, limit):
                self.calls = 0
                self.models_used = {}
                self.providers_used = {}
                self.avoid_providers = set()

            def ask(self, role, context, screenshots=()):
                self.calls += 1
                return {
                    "files": [
                        {
                            "path": "lib/app.dart",
                            "content": "const endpoint = 'https://model.example.com';\n",
                        }
                    ]
                }

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "lib/app.dart"
            source.parent.mkdir(parents=True)
            source.write_text("const endpoint = 'http://example.com';\n")
            result = attempt(
                root,
                STATE,
                {"passed": False, "blockers": ["excessive_jank"]},
                "performance_qa",
                "demo_app",
                model_factory=NeverModel,
                sandbox_factory=PassingSandbox,
            )

        self.assertTrue(result["changed"])
        self.assertEqual(result["strategy"], "agent_only")
        agent_candidate = next(
            item for item in result["candidate_search"]["candidates"]
            if item["strategy"] == "agent_only"
        )
        self.assertEqual(agent_candidate["model_calls"], 0)
        self.assertEqual(result["agent"]["agent"], "fake-agent")
        self.assertEqual(result["candidate_search"]["evaluated"], 1)



    @patch("release_repair.save_artifact_cache", side_effect=StudioError("artifact cache unavailable"))
    @patch("release_repair.save_full_gate_cache", side_effect=OSError("full cache disk error"))
    @patch("release_repair.save_persistent_quick_cache", side_effect=OSError("quick cache disk error"))
    def test_cache_persistence_failures_are_non_fatal(self, quick_save, full_save, artifact_save):
        result = _persist_caches({"q": {}}, {"f": {}}, {"a": {}})

        self.assertFalse(result["ok"])
        self.assertEqual(
            [item["cache"] for item in result["errors"]],
            ["quick_gate", "full_gate", "artifact"],
        )
        quick_save.assert_called_once()
        full_save.assert_called_once()
        artifact_save.assert_called_once()



    def test_release_fix_checkpoint_replay_does_not_spend_model_budget(self):
        class ReplayModel:
            def __init__(self, limit):
                self.calls = 0
                self.models_used = {}
                self.providers_used = {}
                self.avoid_providers = set()

            def ask(self, role, context, screenshots=()):
                self.calls += 1
                return {
                    "files": [
                        {
                            "path": "lib/app.dart",
                            "content": "const value = 2;\n",
                        }
                    ]
                }

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            checkpoint = root / "checkpoints.json"
            source = root / "lib/app.dart"
            source.parent.mkdir(parents=True)
            source.write_text("const value = 1;\n")

            with patch.dict(
                "os.environ",
                {"STUDIO_CHECKPOINT_PATH": str(checkpoint)},
                clear=False,
            ):
                first = _model_mutation(
                    root,
                    STATE,
                    "performance_qa",
                    ["excessive_jank"],
                    None,
                    ReplayModel,
                )
                self.assertEqual(first["model_calls"], 1)
                source.write_text("const value = 1;\n")

                second = _model_mutation(
                    root,
                    STATE,
                    "performance_qa",
                    ["excessive_jank"],
                    None,
                    ReplayModel,
                )

            self.assertTrue(second["checkpoint_reused"])
            self.assertEqual(second["model_calls"], 0)
            self.assertEqual(source.read_text(), "const value = 2;\n")



if __name__ == "__main__":
    unittest.main()
