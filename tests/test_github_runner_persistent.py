import json
from pathlib import Path
import tempfile
import os
import unittest
from contextlib import ExitStack
from unittest.mock import patch

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from github_runner import run, _prepare_capability_promotion_handoff
from goal_engine import finalize, new_goal, record_cycle


class GithubRunnerPersistentTests(unittest.TestCase):
    def request(self, root):
        path=root/"request.json"
        path.write_text(json.dumps({
            "id":"demo",
            "target_repo":"owner/demo",
            "app_name":"demo",
            "brief":"Build a simple offline application.",
            "enabled":True,
        }))
        return path

    def test_run_uses_persistent_goal_engine(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); request=self.request(root); out=root/"out"
            with patch("github_runner.run_persistent_project") as persistent:
                goal=new_goal("demo","Complete demo",[{"name":"done","required_evidence":["project_completion"]}])
                goal=record_cycle(goal,evidence={"project_completion":{"finished":True}})
                persistent.return_value=finalize(goal)
                result=run(request,out,runner=lambda *a,**k:None,clock=lambda:0,budget_seconds=100,baseline_sha="a"*40)
                self.assertEqual(result["status"],"complete")
                self.assertTrue(result["finished"])
                persistent.assert_called_once()

    def test_human_action_is_not_reported_complete(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); request=self.request(root); out=root/"out"
            with patch("github_runner.run_persistent_project") as persistent:
                persistent.return_value={
                    "status":"human_action_required",
                    "human_action":"godot_play_submission",
                    "blocked_reason":None,
                }
                result=run(request,out,runner=lambda *a,**k:None,clock=lambda:0,budget_seconds=100,baseline_sha="b"*40)
                self.assertEqual(result["status"],"human_action_required")
                self.assertFalse(result["finished"])
                self.assertEqual(result["next_stage"],"godot_play_submission")

    def test_blocked_state_preserves_reason(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); request=self.request(root); out=root/"out"
            with patch("github_runner.run_persistent_project") as persistent:
                persistent.return_value={
                    "status":"blocked",
                    "human_action":None,
                    "blocked_reason":"attempt_budget_exhausted",
                }
                result=run(request,out,runner=lambda *a,**k:None,clock=lambda:0,budget_seconds=100,baseline_sha="c"*40)
                self.assertEqual(result["status"],"blocked")
                self.assertFalse(result["finished"])
                self.assertEqual(result["next_stage"],"attempt_budget_exhausted")


    def test_remote_checkpoint_ingests_memory_before_state_persistence(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); request=self.request(root); out=root/"out"
            out.mkdir(parents=True,exist_ok=True)
            order=[]
            state={"status":"blocked","human_action":None,"blocked_reason":"test-stop"}
            with ExitStack() as stack:
                stack.enter_context(patch.dict(os.environ,{"STUDIO_PERSIST_REMOTE":"1","GITHUB_REPOSITORY":"owner/control"},clear=False))
                for name in (
                    "RepoGitHub","restore_local","restore_memory_local","restore_agent_performance_local",
                    "restore_provider_health_local","restore_provider_metrics_local","restore_routing_history_local",
                    "restore_verification_cost_local","restore_phase_cost_baseline_local","restore_strategy_efficiency_local","restore_contextual_strategy_efficiency_local",
                    "restore_quick_gate_cache_local","restore_full_gate_cache_local","restore_artifact_cas_stats_local","restore_artifact_cas_audit_local",
                    "restore_execution_checkpoint_local","save_project_memory",
                ):
                    stack.enter_context(patch("github_runner."+name))
                stack.enter_context(patch("github_runner.run_persistent_project",return_value=state))
                stack.enter_context(patch("github_runner.load_project_memory",return_value={"memory":"before"}))
                stack.enter_context(patch("github_runner.ingest_run",side_effect=lambda *a,**k:(order.append("ingest") or {"memory":"after"})))
                stack.enter_context(patch("github_runner.persist_local",side_effect=lambda *a,**k:order.append("state")))
                stack.enter_context(patch("github_runner.persist_memory_local",side_effect=lambda *a,**k:order.append("memory")))
                stack.enter_context(patch("github_runner.persist_agent_performance_local",side_effect=lambda *a,**k:order.append("agent-performance")))
                stack.enter_context(patch("github_runner.persist_provider_health_local",side_effect=lambda *a,**k:order.append("provider-health")))
                stack.enter_context(patch("github_runner.persist_provider_metrics_local",side_effect=lambda *a,**k:order.append("provider-metrics")))
                stack.enter_context(patch("github_runner.persist_routing_history_local",side_effect=lambda *a,**k:order.append("routing-history")))
                stack.enter_context(patch("github_runner.persist_verification_cost_local",side_effect=lambda *a,**k:order.append("verification-cost")))
                stack.enter_context(patch("github_runner.persist_phase_cost_baseline_local",side_effect=lambda *a,**k:order.append("phase-cost-baseline")))
                stack.enter_context(patch("github_runner.persist_strategy_efficiency_local",side_effect=lambda *a,**k:order.append("strategy-efficiency")))
                stack.enter_context(patch("github_runner.persist_contextual_strategy_efficiency_local",side_effect=lambda *a,**k:order.append("contextual-strategy-efficiency")))
                stack.enter_context(patch("github_runner.persist_quick_gate_cache_local",side_effect=lambda *a,**k:order.append("quick-gate-cache")))
                stack.enter_context(patch("github_runner.persist_full_gate_cache_local",side_effect=lambda *a,**k:order.append("full-gate-cache")))
                stack.enter_context(patch("github_runner.persist_artifact_cas_stats_local",side_effect=lambda *a,**k:order.append("artifact-cas-stats")))
                stack.enter_context(patch("github_runner.persist_artifact_cas_audit_local",side_effect=lambda *a,**k:order.append("artifact-cas-audit")))
                stack.enter_context(patch("github_runner.persist_execution_checkpoint_local",side_effect=lambda *a,**k:order.append("execution-checkpoint")))
                run(request,out,runner=lambda *a,**k:None,clock=lambda:0,budget_seconds=100,baseline_sha="d"*40)
            self.assertEqual(order,["ingest","state","memory","agent-performance","provider-health","provider-metrics","routing-history","verification-cost","phase-cost-baseline","strategy-efficiency","contextual-strategy-efficiency","quick-gate-cache","full-gate-cache","artifact-cas-stats","artifact-cas-audit","execution-checkpoint"])

    def test_invalid_memory_ingestion_blocks_state_checkpoint(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); request=self.request(root); out=root/"out"
            out.mkdir(parents=True,exist_ok=True)
            state={"status":"blocked","human_action":None,"blocked_reason":"test-stop"}
            with patch.dict(os.environ,{"STUDIO_PERSIST_REMOTE":"1","GITHUB_REPOSITORY":"owner/control"},clear=False), \
                 patch("github_runner.RepoGitHub"), \
                 patch("github_runner.restore_local"), \
                 patch("github_runner.restore_memory_local"), \
                 patch("github_runner.restore_agent_performance_local"), \
                 patch("github_runner.restore_provider_health_local"), \
                 patch("github_runner.restore_provider_metrics_local"), \
                 patch("github_runner.restore_routing_history_local"), \
                 patch("github_runner.restore_verification_cost_local"), \
                 patch("github_runner.restore_phase_cost_baseline_local"), \
                 patch("github_runner.restore_strategy_efficiency_local"), \
                 patch("github_runner.restore_contextual_strategy_efficiency_local"), \
                 patch("github_runner.restore_quick_gate_cache_local"), \
                 patch("github_runner.restore_full_gate_cache_local"), \
                 patch("github_runner.restore_artifact_cas_stats_local"), \
                 patch("github_runner.restore_artifact_cas_audit_local"), \
                 patch("github_runner.restore_execution_checkpoint_local"), \
                 patch("github_runner.run_persistent_project",return_value=state), \
                 patch("github_runner.load_project_memory",return_value={"memory":"before"}), \
                 patch("github_runner.ingest_run",side_effect=ValueError("invalid learning")), \
                 patch("github_runner.persist_local") as persist_state:
                with self.assertRaisesRegex(Exception,"Project memory ingestion failed"):
                    run(request,out,runner=lambda *a,**k:None,clock=lambda:0,budget_seconds=100,baseline_sha="e"*40)
                persist_state.assert_not_called()


    def test_promotion_required_handoff_is_sealed_and_non_promoting(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)
            root=out/".autonomy"; root.mkdir(parents=True)
            (root/"capability-candidate.json").write_text("{}")
            (root/"capability-validation.json").write_text("{}")
            state={
                "status":"promotion_required",
                "promotion_status":"eligible",
                "capability":"image_assets",
                "synthesis_status":"candidate_synthesized:"+"a"*64,
            }
            candidate={
                "candidate_id":"candidate:1",
                "candidate_sha256":"a"*64,
                "candidate":{"capability":"image_assets","provider":"studio.capabilities.image_assets"},
            }
            validation={
                "candidate_id":"candidate:1",
                "candidate_sha256":"a"*64,
                "report_sha256":"b"*64,
                "validation":{"status":"candidate_validated"},
            }
            with patch("github_runner.validate_candidate_envelope",return_value=candidate), \
                 patch("github_runner.validate_isolated_validation_result",return_value=validation):
                handoff=_prepare_capability_promotion_handoff(out,state,"c"*40)
            self.assertEqual(handoff["status"],"promotion_required")
            self.assertFalse(handoff["capability_registered"])
            self.assertFalse(handoff["candidate_materialized_in_trusted_repo"])
            self.assertEqual(len(handoff["handoff_sha256"]),64)
            self.assertTrue((root/"capability-promotion-handoff.json").is_file())

    def test_promotion_handoff_rejects_cross_candidate_validation(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)
            root=out/".autonomy"; root.mkdir(parents=True)
            (root/"capability-candidate.json").write_text("{}")
            (root/"capability-validation.json").write_text("{}")
            state={
                "status":"promotion_required",
                "promotion_status":"eligible",
                "capability":"image_assets",
                "synthesis_status":"candidate_synthesized:"+"a"*64,
            }
            candidate={
                "candidate_id":"candidate:1",
                "candidate_sha256":"a"*64,
                "candidate":{"capability":"image_assets","provider":"studio.capabilities.image_assets"},
            }
            validation={
                "candidate_id":"candidate:2",
                "candidate_sha256":"a"*64,
                "report_sha256":"b"*64,
                "validation":{"status":"candidate_validated"},
            }
            with patch("github_runner.validate_candidate_envelope",return_value=candidate), \
                 patch("github_runner.validate_isolated_validation_result",return_value=validation):
                with self.assertRaisesRegex(Exception,"candidate mismatch"):
                    _prepare_capability_promotion_handoff(out,state,"c"*40)


if __name__=="__main__":
    unittest.main()
