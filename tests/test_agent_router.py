from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
STUDIO = ROOT / "studio"
if str(STUDIO) not in sys.path:
    sys.path.insert(0, str(STUDIO))

from agents.adapters import AgentAdapter, AgentRun
from agents.registry import AgentRegistry, AgentSpec
from agents.router import choose_agent, rank_agents
from agents.orchestrator import execute_named, invocation_for
import capacity_ledger


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

    def test_external_agent_isolates_control_plane_credentials(self):
        # Hermes/OpenCode CLI processes may be untrusted third-party code.
        # Production-OS worker authority and Git/SSH publishing credentials
        # must never be inherited or reintroduced via extra_env.
        inherited = {
            "GITHUB_TOKEN": "github-secret",
            "GH_TOKEN": "gh-secret",
            "STUDIO_GITHUB_TOKEN": "studio-secret",
            "PRODUCTION_OS_OPERATOR_TOKEN": "operator-secret",
            "PRODUCTION_OS_WORKER_TOKEN": "worker-secret",
            "PRODUCTION_OS_URL": "https://operator.internal",
            "ASSET_FORGE_GITHUB_TOKEN": "asset-secret",
            "GIT_ASKPASS": "git-askpass-secret",
            "SSH_ASKPASS": "ssh-askpass-secret",
            "SSH_AUTH_SOCK": "/private/socket",
            "OMNIROUTE_API_KEY": "provider-model-key",
        }
        overrides = {
            "PRODUCTION_OS_OPERATOR_TOKEN": "override-operator",
            "GITHUB_TOKEN": "override-github",
            "GIT_CONFIG_COUNT": "5",
            "STUDIO_API_KEY": "override-studio",
            "SSH_AUTH_SOCK": "/other/private/socket",
            "OPENCODE_STUDIO_API_KEY": "scoped-model-key",
        }
        for name in ("opencode", "hermes"):
            adapter = AgentAdapter(AgentSpec(name, name, frozenset({"repo_analysis"})))
            with (
                patch.dict(os.environ, inherited, clear=True),
                patch("shutil.which", return_value="/usr/bin/" + name),
                patch("agents.adapters.subprocess.run",
                      return_value=subprocess.CompletedProcess(
                          [name, "run"], 0, "finished", "")) as child,
            ):
                result = adapter.run([name, "run"], cwd=ROOT,
                                     extra_env=overrides, timeout=10)
            self.assertEqual(result.returncode, 0)
            child_env = child.call_args.kwargs["env"]
            for secret in (
                "GITHUB_TOKEN", "GH_TOKEN", "STUDIO_GITHUB_TOKEN",
                "PRODUCTION_OS_OPERATOR_TOKEN", "PRODUCTION_OS_WORKER_TOKEN",
                "PRODUCTION_OS_URL", "ASSET_FORGE_GITHUB_TOKEN", "GIT_ASKPASS",
                "SSH_ASKPASS", "SSH_AUTH_SOCK", "GIT_CONFIG_COUNT", "STUDIO_API_KEY",
            ):
                self.assertNotIn(secret, child_env, (name, secret))
            self.assertEqual(child_env["OPENCODE_STUDIO_API_KEY"], "scoped-model-key")
            self.assertEqual(child_env["OMNIROUTE_API_KEY"], "provider-model-key")

    def test_opencode_headless_exit_zero_needs_real_assistant_output(self):
        from agents.orchestrator import _completion_verified

        def evidence(stdout):
            return AgentRun("opencode", 0, 1.0, stdout, "")

        self.assertFalse(_completion_verified(evidence("")))
        self.assertFalse(_completion_verified(evidence(
            '{"type":"step_start","part":{"type":"step-start"}}'
        )))
        self.assertFalse(_completion_verified(evidence(
            '{"type":"text","part":{"type":"text","text":""}}'
        )))
        self.assertFalse(_completion_verified(evidence(
            '{"type":"text","part":{"type":"text","text":"Continue",'
            '"synthetic":true}}'
        )))
        self.assertFalse(_completion_verified(evidence(
            '{"type":"text","part":{"type":"text","text":"compaction",'
            '"metadata":{"compaction_continue":true}}}'
        )))
        verified = evidence(
            '{"type":"step_start"}\n'
            '{"type":"text","part":{"type":"text","text":"Implemented and tested."}}\n'
            '{"type":"step_finish"}'
        )
        self.assertTrue(_completion_verified(verified))
        with patch("shutil.which", return_value="/usr/bin/opencode"), patch(
            "agents.orchestrator.AgentAdapter.run",
            return_value=evidence('{"type":"step_start"}')
        ):
            failed = execute_named("opencode", "edit this", cwd=ROOT)
        self.assertEqual(failed["status"], "failed")
        self.assertEqual(failed["attempts"][0]["returncode"], 0)
        self.assertFalse(failed["attempts"][0]["completion_verified"])
        self.assertEqual(
            failed["attempts"][0]["failure_reason"], "unverified-headless-output"
        )
        with patch("shutil.which", return_value="/usr/bin/opencode"), patch(
            "agents.orchestrator.AgentAdapter.run", return_value=verified
        ):
            succeeded = execute_named("opencode", "edit this", cwd=ROOT)
        self.assertEqual(succeeded["status"], "passed")
        self.assertTrue(succeeded["attempts"][0]["completion_verified"])

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
            "agents.orchestrator.omniroute_available_base", return_value=None
        ), patch(
            "agents.orchestrator.AgentAdapter.run", return_value=run
        ):
            result = execute_named("codex", "do work", cwd=ROOT)

        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["attempts"][0]["usage"]["total_tokens"], 13)
        self.assertEqual(result["attempts"][0]["usage"]["cached_input_tokens"], 4)


    def test_codex_execute_named_prefers_isolated_omniroute_profile_when_healthy(self):
        run = AgentRun(
            agent="codex",
            returncode=0,
            duration_seconds=1.0,
            stdout_tail='{"type":"turn.completed","usage":{"input_tokens":8,"output_tokens":2}}',
            stderr_tail="",
        )
        seen = {}

        def fake_run(_adapter, argv, *, cwd, timeout, extra_env):
            seen["argv"] = list(argv)
            seen["extra_env"] = dict(extra_env)
            return run

        with patch("shutil.which", return_value="/bin/codex"), patch(
            "agents.orchestrator.omniroute_available_base",
            return_value="http://127.0.0.1:20128/v1",
        ), patch(
            "agents.orchestrator.AgentAdapter.run",
            autospec=True,
            side_effect=fake_run,
        ):
            result = execute_named("codex", "do work", cwd=ROOT)

        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["attempts"][0]["capacity_source"], "omniroute-free")
        self.assertIn("--ignore-user-config", seen["argv"])
        self.assertEqual(
            result["attempts"][0]["usage"]["total_tokens"],
            10,
        )
        self.assertTrue(seen["extra_env"]["CODEX_HOME"])

    def test_codex_execute_named_uses_chatgpt_profile_when_omniroute_is_unavailable(self):
        run = AgentRun(
            agent="codex",
            returncode=0,
            duration_seconds=1.0,
            stdout_tail='{"type":"turn.completed","usage":{"input_tokens":4,"output_tokens":1}}',
            stderr_tail="",
        )
        seen = {}

        def fake_run(_adapter, argv, *, cwd, timeout, extra_env):
            seen["argv"] = list(argv)
            seen["extra_env"] = dict(extra_env)
            return run

        with patch("shutil.which", return_value="/bin/codex"), patch(
            "agents.orchestrator.omniroute_available_base",
            return_value=None,
        ), patch(
            "agents.orchestrator.AgentAdapter.run",
            autospec=True,
            side_effect=fake_run,
        ):
            result = execute_named("codex", "do work", cwd=ROOT)

        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["attempts"][0]["capacity_source"], "codex-chatgpt")
        self.assertNotIn("--ignore-user-config", seen["argv"])
        self.assertNotIn("CODEX_HOME", seen["extra_env"])


    def test_codex_execute_named_stops_when_project_token_envelope_is_exhausted(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            plan = root / "capacity-plan.json"
            ledger = root / "capacity-ledger.json"
            plan.write_text(json.dumps({
                "projects": [{"id": "project-a", "token_envelope": 1000}]
            }))
            reservation = capacity_ledger.reserve(
                ledger,
                project_id="project-a",
                provider="agent:codex",
                estimated_tokens=1000,
                provider_remaining_tokens=None,
                project_envelope_tokens=1000,
            )
            capacity_ledger.settle(
                ledger,
                reservation["reservation_id"],
                actual_tokens=1000,
            )
            env = {
                "STUDIO_PROJECT_ID": "project-a",
                "STUDIO_CAPACITY_PLAN_PATH": str(plan),
                "STUDIO_CAPACITY_LEDGER_PATH": str(ledger),
            }
            with patch.dict(os.environ, env, clear=False), patch(
                "shutil.which", return_value="/bin/codex"
            ), patch(
                "agents.orchestrator.omniroute_available_base",
                return_value=None,
            ), patch(
                "agents.orchestrator.AgentAdapter.run"
            ) as run:
                result = execute_named("codex", "do work", cwd=ROOT)

            self.assertEqual(result["status"], "unavailable")
            self.assertEqual(
                result["attempts"][0]["status"],
                "capacity_exhausted",
            )
            run.assert_not_called()

    def test_codex_execute_named_settles_reported_usage_in_project_ledger(self):
        run_result = AgentRun(
            agent="codex",
            returncode=0,
            duration_seconds=1.0,
            stdout_tail='{"type":"turn.completed","usage":{"input_tokens":10,"output_tokens":3}}',
            stderr_tail="",
        )
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            plan = root / "capacity-plan.json"
            ledger = root / "capacity-ledger.json"
            plan.write_text(json.dumps({
                "projects": [{"id": "project-a", "token_envelope": 10000}]
            }))
            env = {
                "STUDIO_PROJECT_ID": "project-a",
                "STUDIO_CAPACITY_PLAN_PATH": str(plan),
                "STUDIO_CAPACITY_LEDGER_PATH": str(ledger),
            }
            with patch.dict(os.environ, env, clear=False), patch(
                "shutil.which", return_value="/bin/codex"
            ), patch(
                "agents.orchestrator.omniroute_available_base",
                return_value=None,
            ), patch(
                "agents.orchestrator.AgentAdapter.run",
                return_value=run_result,
            ):
                result = execute_named("codex", "do work", cwd=ROOT)

            self.assertEqual(result["status"], "passed")
            self.assertEqual(
                capacity_ledger.consumed_tokens(
                    capacity_ledger.load(ledger),
                    project_id="project-a",
                ),
                13,
            )


if __name__ == "__main__":
    unittest.main()
