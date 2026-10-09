"""Production-OS native runner round persistence wiring and identity guards."""

import json
import os
import tempfile
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from github_runner import run


class GithubRunnerRoundPersistenceTests(unittest.TestCase):
    def request(self, root):
        path = root / "request.json"
        path.write_text(json.dumps({
            "id": "demo",
            "target_repo": "owner/demo",
            "app_name": "demo",
            "brief": "Build a simple offline application.",
            "enabled": True,
        }))
        return path

    def test_remote_generic_published_round_is_flushed_before_cycle_finishes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            request = self.request(root)
            out = root / "out"
            checkpoints = []
            checkpoint = {
                "project_id": "demo",
                "phase": "published",
                "round": 1,
                "base_sha": "b" * 40,
            }
            remote_saves = []
            with ExitStack() as stack:
                stack.enter_context(patch.dict(
                    os.environ,
                    {"STUDIO_PERSIST_REMOTE": "1", "GITHUB_REPOSITORY": "owner/control"},
                    clear=False,
                ))
                for name in (
                    "RepoGitHub", "restore_local", "restore_memory_local",
                    "restore_agent_performance_local", "restore_provider_health_local",
                    "restore_provider_metrics_local", "restore_routing_history_local",
                    "restore_verification_cost_local", "restore_phase_cost_baseline_local",
                    "restore_strategy_efficiency_local",
                    "restore_contextual_strategy_efficiency_local",
                    "restore_quick_gate_cache_local", "restore_full_gate_cache_local",
                    "restore_artifact_cas_stats_local", "restore_artifact_cas_audit_local",
                    "restore_execution_checkpoint_local", "save_project_memory",
                    "persist_local", "persist_memory_local",
                    "persist_agent_performance_local", "persist_provider_health_local",
                    "persist_provider_metrics_local", "persist_routing_history_local",
                    "persist_verification_cost_local", "persist_phase_cost_baseline_local",
                    "persist_strategy_efficiency_local",
                    "persist_contextual_strategy_efficiency_local",
                    "persist_quick_gate_cache_local", "persist_full_gate_cache_local",
                    "persist_artifact_cas_stats_local", "persist_artifact_cas_audit_local",
                ):
                    stack.enter_context(patch("github_runner." + name))
                flush = stack.enter_context(patch(
                    "github_runner.persist_execution_checkpoint_local",
                    side_effect=lambda *args: remote_saves.append(args),
                ))
                stack.enter_context(patch(
                    "github_runner.load_project_memory", return_value={},
                ))
                stack.enter_context(patch(
                    "github_runner.ingest_run", return_value={},
                ))

                def emulate_generic(*args, **kwargs):
                    self.assertIn("checkpoint_observer", kwargs)
                    kwargs["checkpoint_observer"](checkpoint)
                    checkpoints.append("generic-round-returned")
                    return {"status": "deferred", "report": {}, "next_stage": "generic_continue"}

                stack.enter_context(patch(
                    "github_runner.run_multi_engine_project",
                    side_effect=emulate_generic,
                ))

                def emulate_goal_loop(*args, **kwargs):
                    self.assertIn("checkpoint_observer", kwargs)
                    kwargs["run_once"](
                        "request.json", out, str(root / "work"),
                        lambda *a, **k: None, 100, lambda: 0, "a" * 40,
                    )
                    return {"status": "active", "attempt": 1}

                stack.enter_context(patch(
                    "github_runner.run_persistent_project",
                    side_effect=emulate_goal_loop,
                ))
                result = run(
                    request, out, runner=lambda *args, **kwargs: None,
                    clock=lambda: 0, budget_seconds=100, baseline_sha="a" * 40,
                )
                self.assertEqual(result["status"], "active")
                self.assertEqual(checkpoints, ["generic-round-returned"])
                self.assertEqual(flush.call_count, 2)
                self.assertEqual(len(remote_saves), 2)
                self.assertEqual(remote_saves[0][1], "demo")
                self.assertEqual(
                    remote_saves[0][2],
                    out / ".autonomy/generic-execution-checkpoint.json",
                )

    def test_wrong_project_round_checkpoint_is_refused(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            request = self.request(root)
            out = root / "out"
            with ExitStack() as stack:
                stack.enter_context(patch.dict(
                    os.environ,
                    {"STUDIO_PERSIST_REMOTE": "1", "GITHUB_REPOSITORY": "owner/control"},
                    clear=False,
                ))
                for name in (
                    "RepoGitHub", "restore_local", "restore_memory_local",
                    "restore_agent_performance_local", "restore_provider_health_local",
                    "restore_provider_metrics_local", "restore_routing_history_local",
                    "restore_verification_cost_local", "restore_phase_cost_baseline_local",
                    "restore_strategy_efficiency_local",
                    "restore_contextual_strategy_efficiency_local",
                    "restore_quick_gate_cache_local", "restore_full_gate_cache_local",
                    "restore_artifact_cas_stats_local", "restore_artifact_cas_audit_local",
                    "restore_execution_checkpoint_local",
                ):
                    stack.enter_context(patch("github_runner." + name))

                def bad_generic(*args, **kwargs):
                    kwargs["checkpoint_observer"]({
                        "project_id": "other-project",
                        "phase": "published", "round": 1,
                    })

                stack.enter_context(patch(
                    "github_runner.run_multi_engine_project", side_effect=bad_generic,
                ))

                def emulate_goal_loop(*args, **kwargs):
                    kwargs["run_once"](
                        "request.json", out, str(root / "work"),
                        lambda *a, **k: None, 100, lambda: 0, "a" * 40,
                    )

                stack.enter_context(patch(
                    "github_runner.run_persistent_project", side_effect=emulate_goal_loop,
                ))
                persist_remote = stack.enter_context(patch(
                    "github_runner.persist_execution_checkpoint_local",
                ))
                with self.assertRaisesRegex(Exception, "identity or phase invalid"):
                    run(
                        request, out, runner=lambda *args, **kwargs: None,
                        clock=lambda: 0, budget_seconds=100,
                        baseline_sha="a" * 40,
                    )
                persist_remote.assert_not_called()



if __name__ == "__main__":
    unittest.main()
