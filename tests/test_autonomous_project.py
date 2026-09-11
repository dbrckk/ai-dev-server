from pathlib import Path
import tempfile
import unittest

from studio.autonomous_project import (
    ensure_project_goal,
    run_persistent_project,
    translate_orchestrator_result,
    _sync_promoted_capabilities,
)
from studio.goal_engine import load as load_goal


class AutonomousProjectTests(unittest.TestCase):
    def test_complete_requires_machine_completion_evidence(self):
        translated = translate_orchestrator_result({
            "status": "complete",
            "report": {"status": "finished", "completion": {"finished": True}, "release_status": "store_ready"},
            "next_stage": None,
        })
        self.assertTrue(translated["evidence"]["project_completion"]["finished"])

    def test_false_complete_fails_closed(self):
        translated = translate_orchestrator_result({
            "status": "complete",
            "report": {"completion": {"finished": False}},
            "next_stage": None,
        })
        self.assertIn("blocked_reason", translated)

    def test_human_action_is_preserved(self):
        translated = translate_orchestrator_result({
            "status": "human_action_required",
            "report": {},
            "next_stage": "godot_play_submission",
        })
        self.assertEqual(translated, {"human_action": "godot_play_submission"})

    def test_adaptation_yields_without_claiming_completion(self):
        translated = translate_orchestrator_result({
            "status": "adaptation_required",
            "report": {},
            "next_stage": "billing_qa",
            "research_status": "complete",
            "promotion_status": "not_ready",
        })
        self.assertTrue(translated["yield_run"])
        self.assertEqual(translated["evidence"]["adaptation_progress"]["capability"], "billing_qa")
        self.assertNotIn("project_completion", translated["evidence"])

    def test_promoted_stage_syncs_into_capability_registry(self):
        from studio.capability_registry import load as load_registry
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); out=root/"out"
            _,registry_path,_=ensure_project_goal(out,"project","goal")
            control=root/"control"; control.mkdir()
            (control/"promoted_stages.json").write_text('{"version":1,"stages":{"billing_qa":{"script":"studio/billing_stage.py","candidate_id":"billing-x","baseline_sha":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","candidate_sha":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"}}}')
            _sync_promoted_capabilities(registry_path,root)
            registry=load_registry(registry_path)
            self.assertIn("billing_qa",registry["capabilities"])
            self.assertEqual(registry["capabilities"]["billing_qa"]["provider"],"studio/billing_stage.py")

    def test_persistent_wrapper_relaunches_until_proved_complete(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            calls = {"n": 0}

            def run_once(*args):
                calls["n"] += 1
                if calls["n"] == 1:
                    return {"status": "failed", "report": {}, "next_stage": "preview"}
                return {
                    "status": "complete",
                    "report": {
                        "status": "finished",
                        "completion": {"finished": True},
                        "release_status": "store_ready",
                    },
                    "next_stage": None,
                }

            state = run_persistent_project(
                "request.json",
                root / "out",
                str(root / "work"),
                runner=lambda *a, **k: None,
                deadline=100,
                clock=lambda: 0,
                run_once=run_once,
                max_cycles=3,
            )
            self.assertEqual(state["status"], "complete")
            self.assertEqual(calls["n"], 2)
            goal_path, _, memory_path = ensure_project_goal(root / "out", "project", "ignored")
            self.assertEqual(load_goal(goal_path)["status"], "complete")
            self.assertTrue(memory_path.is_file())

    def test_human_action_persists_terminal_state(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)

            def run_once(*args):
                return {
                    "status": "human_action_required",
                    "report": {},
                    "next_stage": "approve_release",
                }

            state = run_persistent_project(
                "request.json",
                root / "out",
                str(root / "work"),
                runner=lambda *a, **k: None,
                deadline=100,
                clock=lambda: 0,
                run_once=run_once,
                max_cycles=2,
            )
            self.assertEqual(state["status"], "human_action_required")
            self.assertEqual(state["human_action"], "approve_release")


if __name__ == "__main__":
    unittest.main()
