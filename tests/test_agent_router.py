from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
STUDIO = ROOT / "studio"
if str(STUDIO) not in sys.path:
    sys.path.insert(0, str(STUDIO))

from agents.adapters import AgentRun
from agents.registry import AgentRegistry, AgentSpec
from agents.router import choose_agent, rank_agents
from agents.orchestrator import execute_named, invocation_for


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

    def test_contextual_memory_changes_agent_score(self):
        contextual = {
            "stack:python": {
                "agent:free-code": {
                    "samples": 8,
                    "successes": 8,
                    "ema_success_rate": 0.95,
                },
                "agent:paid-code": {
                    "samples": 8,
                    "successes": 1,
                    "ema_success_rate": 0.10,
                },
            }
        }
        with patch("shutil.which", return_value="/bin/tool"):
            ranked = rank_agents(
                {"code_editing", "tests"},
                registry=self.registry,
                prefer_free=False,
                contextual_routing=contextual,
                weighted_contexts=[("stack:python", 1.0)],
            )
        free_code = next(item for item in ranked if item.agent.name == "free-code")
        paid_code = next(item for item in ranked if item.agent.name == "paid-code")
        self.assertGreater(
            free_code.trace["components"]["contextual_performance"],
            paid_code.trace["components"]["contextual_performance"],
        )

    def test_cost_aware_utility_prefers_faster_agent_when_context_quality_is_equal(self):
        contextual = {
            "backend": {
                "agent:free-code": {
                    "samples": 12,
                    "successes": 10,
                    "ema_success_rate": 0.8,
                },
                "agent:paid-code": {
                    "samples": 12,
                    "successes": 10,
                    "ema_success_rate": 0.8,
                },
            }
        }
        with patch("shutil.which", return_value="/bin/tool"):
            ranked = rank_agents(
                {"code_editing", "tests"},
                registry=self.registry,
                prefer_free=False,
                contextual_routing=contextual,
                weighted_contexts=[("backend", 1.0)],
                execution_seconds={"free-code": 5.0, "paid-code": 90.0},
                verification_seconds=30.0,
            )
        free_code = next(item for item in ranked if item.agent.name == "free-code")
        paid_code = next(item for item in ranked if item.agent.name == "paid-code")
        self.assertGreater(
            free_code.trace["components"]["cost_aware_utility"],
            paid_code.trace["components"]["cost_aware_utility"],
        )

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

    def test_codex_invocation_uses_verified_headless_contract(self):
        argv, extra = invocation_for("codex", "do work")

        self.assertEqual(
            argv,
            ["codex", "exec", "--json", "--ephemeral", "--sandbox", "workspace-write", "do work"],
        )
        self.assertEqual(extra, {})

    def test_codex_execute_named_exposes_token_usage(self):
        run = AgentRun(
            agent="codex",
            returncode=0,
            duration_seconds=1.5,
            stdout_tail='{"type":"turn.completed","usage":{"input_tokens":10,"cached_input_tokens":4,"output_tokens":3}}',
            stderr_tail="",
        )
        with patch("shutil.which", return_value="/bin/codex"), patch(
            "agents.orchestrator.AgentAdapter.run", return_value=run
        ):
            result = execute_named("codex", "do work", cwd=ROOT)

        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["attempts"][0]["usage"]["total_tokens"], 13)
        self.assertEqual(result["attempts"][0]["usage"]["cached_input_tokens"], 4)


if __name__ == "__main__":
    unittest.main()
