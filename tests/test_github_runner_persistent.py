import json
from pathlib import Path
import tempfile
import os
import unittest
from unittest.mock import patch

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from github_runner import run
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
            with patch.dict(os.environ,{"STUDIO_PERSIST_REMOTE":"1","GITHUB_REPOSITORY":"owner/control"},clear=False), \
                 patch("github_runner.RepoGitHub"), \
                 patch("github_runner.restore_local"), \
                 patch("github_runner.restore_memory_local"), \
                 patch("github_runner.run_persistent_project",return_value=state), \
                 patch("github_runner.load_project_memory",return_value={"memory":"before"}), \
                 patch("github_runner.ingest_run",side_effect=lambda *a,**k:(order.append("ingest") or {"memory":"after"})), \
                 patch("github_runner.save_project_memory"), \
                 patch("github_runner.persist_local",side_effect=lambda *a,**k:order.append("state")), \
                 patch("github_runner.persist_memory_local",side_effect=lambda *a,**k:order.append("memory")):
                run(request,out,runner=lambda *a,**k:None,clock=lambda:0,budget_seconds=100,baseline_sha="d"*40)
            self.assertEqual(order,["ingest","state","memory"])

    def test_invalid_memory_ingestion_blocks_state_checkpoint(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); request=self.request(root); out=root/"out"
            out.mkdir(parents=True,exist_ok=True)
            state={"status":"blocked","human_action":None,"blocked_reason":"test-stop"}
            with patch.dict(os.environ,{"STUDIO_PERSIST_REMOTE":"1","GITHUB_REPOSITORY":"owner/control"},clear=False), \
                 patch("github_runner.RepoGitHub"), \
                 patch("github_runner.restore_local"), \
                 patch("github_runner.restore_memory_local"), \
                 patch("github_runner.run_persistent_project",return_value=state), \
                 patch("github_runner.load_project_memory",return_value={"memory":"before"}), \
                 patch("github_runner.ingest_run",side_effect=ValueError("invalid learning")), \
                 patch("github_runner.persist_local") as persist_state:
                with self.assertRaisesRegex(Exception,"Project memory ingestion failed"):
                    run(request,out,runner=lambda *a,**k:None,clock=lambda:0,budget_seconds=100,baseline_sha="e"*40)
                persist_state.assert_not_called()


if __name__=="__main__":
    unittest.main()
