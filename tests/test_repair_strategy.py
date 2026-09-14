import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from contextual_strategy_efficiency import record as record_contextual
from repair_strategy import choose


class RepairStrategyTests(unittest.TestCase):
    def test_stage_context_can_select_different_mature_strategy(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            global_path = root / "global.json"
            contextual_path = root / "contextual.json"
            env = {
                "STUDIO_STRATEGY_EFFICIENCY_PATH": str(global_path),
                "STUDIO_CONTEXTUAL_STRATEGY_EFFICIENCY_PATH": str(contextual_path),
            }
            with patch.dict(os.environ, env, clear=False):
                for _ in range(4):
                    record_contextual(
                        contextual_path,
                        "repair:performance_qa",
                        "agent_only",
                        success=True,
                        cost_seconds=10,
                    )
                    record_contextual(
                        contextual_path,
                        "repair:performance_qa",
                        "model_only",
                        success=False,
                        cost_seconds=20,
                    )
                result = choose(
                    None,
                    stage="performance_qa",
                    agent_available=True,
                )

        self.assertIn(result["strategy"], result["allowed"])
        self.assertEqual(result["evidence_source"], "stage_context")
        self.assertEqual(result["candidate_ranking"][0]["strategy"], "agent_only")
        self.assertTrue(result["candidate_ranking"][0]["mature"])

    def test_stagnation_rotates_away_from_last_strategy(self):
        result = choose(
            {
                "rotate_strategy": True,
                "last_strategy": "model_only",
            },
            stage="performance_qa",
            agent_available=True,
        )
        self.assertEqual(result["strategy"], "agent_only")
        self.assertEqual(result["mode"], "stagnation_rotation")

    def test_agent_to_model_is_available_when_agent_exists(self):
        result = choose(
            None,
            stage="native_qa",
            agent_available=True,
        )
        self.assertIn("agent_to_model", result["allowed"])
        self.assertTrue(
            any(row["strategy"] == "agent_to_model" for row in result["candidate_ranking"])
        )


    def test_without_agent_bootstraps_model_only(self):
        result = choose(
            None,
            stage="billing_qa",
            agent_available=False,
        )
        self.assertEqual(result["strategy"], "model_only")
        self.assertEqual(result["allowed"], ["model_only"])
        self.assertEqual(result["candidate_ranking"][0]["strategy"], "model_only")


if __name__ == "__main__":
    unittest.main()
