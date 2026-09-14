from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
STUDIO = ROOT / "studio"
if str(STUDIO) not in sys.path:
    sys.path.insert(0, str(STUDIO))

from agents.registry import AgentRegistry, AgentSpec
from agents.router import choose_agent, rank_agents
from agents.orchestrator import invocation_for


class AgentRouterTests(unittest.TestCase):
    def setUp(self):
        self.registry = AgentRegistry([
            AgentSpec("free-code", "free-code", frozenset({"code_editing", "tests"}), priority=50, free_preferred=True),
            AgentSpec("paid-code", "paid-code", frozenset({"code_editing", "tests", "review"}), priority=90, free_preferred=False),
            AgentSpec("research", "research", frozenset({"research", "planning"}), priority=80, free_preferred=True),
        ])

    def test_free_preference_changes_ranking(self):
        with patch("shutil.which", return_value="/bin/tool"):
            ranked = rank_agents({"code_editing", "tests"}, registry=self.registry, prefer_free=True)
        self.assertEqual(ranked[0].agent.name, "free-code")

    def test_paid_can_win_when_free_preference_disabled(self):
        with patch("shutil.which", return_value="/bin/tool"):
            ranked = rank_agents({"code_editing", "tests"}, registry=self.registry, prefer_free=False)
        self.assertEqual(ranked[0].agent.name, "paid-code")

    def test_unavailable_agent_is_not_selected(self):
        def which(name):
            return "/bin/tool" if name == "research" else None
        with patch("shutil.which", side_effect=which):
            decision = choose_agent({"research"}, registry=self.registry)
        self.assertEqual(decision.agent.name, "research")

    def test_learned_agent_weights_affect_ranking_and_trace(self):
        with patch("shutil.which", return_value="/bin/tool"):
            ranked = rank_agents(
                {"code_editing", "tests"},
                registry=self.registry,
                prefer_free=True,
                reliability={"free-code": 20.0, "paid-code": -20.0},
                weights={"reliability": 1.25},
            )
        self.assertEqual(ranked[0].agent.name, "free-code")
        self.assertIsInstance(ranked[0].trace, dict)
        self.assertIn("reliability", ranked[0].trace["components"])

    def test_architecture_discipline_penalizes_repeatedly_risky_agent(self):
        summary = {
            "origin_rankings": [{
                "kind": "agent",
                "name": "paid-code",
                "samples": 10,
                "verification_pass_rate": 0.0,
                "eligible_for_routing_bias": True,
            }],
            "rewrite_rankings": [],
        }
        with patch("shutil.which", return_value="/bin/tool"):
            ranked = rank_agents(
                {"code_editing", "tests"},
                registry=self.registry,
                prefer_free=False,
                safe_rewrite_summary=summary,
            )
        risky = next(item for item in ranked if item.agent.name == "paid-code")
        self.assertIn("architecture_violation", risky.trace["components"])
        self.assertLess(risky.trace["components"]["architecture_violation"], 0)

    def test_opencode_invocation_uses_secret_alias(self):
        env={
            "STUDIO_API_BASE":"https://example.invalid/v1",
            "STUDIO_API_KEY":"super-secret",
            "STUDIO_CODE_MODEL":"coder/model",
        }
        with patch.dict("os.environ",env,clear=True):
            argv,extra=invocation_for("opencode","do work")
        self.assertIn("--model",argv)
        self.assertEqual(extra["OPENCODE_STUDIO_API_KEY"],"super-secret")
        self.assertNotIn("super-secret",extra["OPENCODE_CONFIG_CONTENT"])
        self.assertIn("OPENCODE_STUDIO_API_KEY",extra["OPENCODE_CONFIG_CONTENT"])


if __name__ == "__main__":
    unittest.main()
