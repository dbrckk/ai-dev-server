import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from core import StudioError
from release_repair import attempt
from unittest.mock import patch


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
                    model_factory=CandidateModel,
                )

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
        }

        def edit(root, blockers, stage):
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
                {"passed": False, "blockers": ["cleartext_network_traffic_detected"]},
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
        self.assertEqual(result["candidate_search"]["evaluated"], 2)



if __name__ == "__main__":
    unittest.main()
