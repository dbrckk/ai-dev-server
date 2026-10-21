import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'studio'))
from core import StudioError
from multi_engine_orchestrator import run_project

REQUEST={'id':'demo-v1','target_repo':'owner/app','app_name':'demo_app','brief':'Build a complete polished mobile application.','enabled':True,'max_rounds':2,'max_calls':8,'max_cycles':3}

class MultiEngineOrchestratorTests(unittest.TestCase):
    def request(self,root):
        path=root/'request.json'; path.write_text(json.dumps(REQUEST)); return path

    @patch('multi_engine_orchestrator.run_flutter_project')
    def test_flutter_delegates_unchanged(self,legacy):
        legacy.return_value={'status':'complete','report':{'completion':{'finished':True}},'next_stage':None}
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); out=root/'out'; req=self.request(root)
            def runner(args,timeout):
                out.mkdir(parents=True,exist_ok=True)
                if 'studio/engine_detect.py' in args: (out/'engine-detection.json').write_text(json.dumps({'status':'detected','engine':'flutter'}))
                return subprocess.CompletedProcess(args,0)
            result=run_project(str(req),out,str(root/'work'),runner,100,lambda:0,'a'*40)
        self.assertEqual(result['status'],'complete'); legacy.assert_called_once()

    @patch("multi_engine_orchestrator.run_generic_project")
    def test_generic_only_forwards_published_round_checkpoint_callback(self, generic):
        generic.return_value = {
            "status": "deferred", "report": {}, "next_stage": "generic_continue",
        }
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out = root / "out"
            req = self.request(root)
            callback_calls = []

            def runner(args, timeout):
                out.mkdir(parents=True, exist_ok=True)
                (out / "engine-detection.json").write_text(json.dumps({
                    "status": "detected", "engine": "generic",
                }))
                return subprocess.CompletedProcess(args, 0)

            callback = callback_calls.append
            response = run_project(
                str(req), out, str(root / "work"), runner,
                100, lambda: 0, "a" * 40,
                checkpoint_observer=callback,
            )
            self.assertEqual(response["status"], "deferred")
            self.assertIs(
                generic.call_args.kwargs["checkpoint_observer"], callback,
            )
            self.assertEqual(callback_calls, [])

    @patch("multi_engine_orchestrator.run_generic_project")
    def test_generic_without_callback_preserves_original_call(self, generic):
        generic.return_value = {
            "status": "deferred", "report": {}, "next_stage": "generic_continue",
        }
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out = root / "out"
            req = self.request(root)

            def runner(args, timeout):
                out.mkdir(parents=True, exist_ok=True)
                (out / "engine-detection.json").write_text(json.dumps({
                    "status": "detected", "engine": "generic",
                }))
                return subprocess.CompletedProcess(args, 0)

            run_project(
                str(req), out, str(root / "work"), runner,
                100, lambda: 0, "a" * 40,
            )
            self.assertNotIn("checkpoint_observer", generic.call_args.kwargs)

    def _runner(self,out,fail_stage=None,bad_journey=False,bad_visual=False,release_ready=False,artifact_credentials=True,exhausted_preview=False):
        calls=[]
        def runner(args,timeout):
            calls.append(args); out.mkdir(parents=True,exist_ok=True)
            script=next((x for x in args if isinstance(x,str) and x.startswith('studio/')),None)
            if script=='studio/engine_detect.py':
                (out/'engine-detection.json').write_text(json.dumps({'status':'detected','engine':'godot'}))
            elif script=='studio/engine_entry.py':
                if exhausted_preview:
                    (out/'report.json').write_text(json.dumps({'engine':'godot','status':'blocked',
                        'preview_cycle_budget_exhausted':True,'checkpoint_commit':'f'*40}))
                    return subprocess.CompletedProcess(args,1)
                (out/'report.json').write_text(json.dumps({'engine':'godot','status':'godot_preview_validated','completion':{'finished':False,'next_stage':'godot_android_export_qa'},'coverage':{}}))
            elif script=='studio/godot_android_stage.py':
                if fail_stage=='android': return subprocess.CompletedProcess(args,1)
                (out/'report.json').write_text(json.dumps({'engine':'godot','status':'godot_android_export_validated','completion':{'finished':False,'next_stage':'godot_device_qa'},'coverage':{'android_export':True,'device_qa':False}}))
            elif script=='studio/godot_device_stage.py':
                if fail_stage=='device': return subprocess.CompletedProcess(args,1)
                (out/'report.json').write_text(json.dumps({'engine':'godot','status':'godot_device_validated','completion':{'finished':False,'next_stage':'godot_runtime_journey_qa'},'coverage':{'android_export':True,'device_qa':True,'journeys_executed':False,'visual_qa':False}}))
            elif script=='studio/godot_runtime_journey_stage.py':
                if fail_stage=='journey': return subprocess.CompletedProcess(args,1)
                coverage={'android_export':True,'device_qa':True,'journeys_executed':not bad_journey,'visual_qa':False}
                (out/'report.json').write_text(json.dumps({'engine':'godot','status':'godot_runtime_journeys_validated','completion':{'finished':False,'next_stage':'godot_visual_qa'},'coverage':coverage}))
            elif script=='studio/godot_visual_stage.py':
                if fail_stage=='visual': return subprocess.CompletedProcess(args,1)
                coverage={'android_export':True,'device_qa':True,'journeys_executed':True,'visual_qa':not bad_visual}
                (out/'report.json').write_text(json.dumps({'engine':'godot','status':'godot_visual_validated','completion':{'finished':False,'next_stage':'godot_release_qa'},'coverage':coverage}))
            elif script=='studio/godot_release_stage.py':
                if fail_stage=='release': return subprocess.CompletedProcess(args,1)
                coverage={'android_export':True,'device_qa':True,'journeys_executed':True,'visual_qa':True}
                if release_ready:
                    report={'engine':'godot','status':'godot_release_preflight_validated','release_status':'not_store_ready','completion':{'finished':False,'next_stage':'godot_release_artifact_qa'},'coverage':coverage}
                else:
                    report={'engine':'godot','status':'godot_release_credentials_required','release_status':'human_action_required','completion':{'finished':False,'next_stage':'godot_release_qa'},'coverage':coverage}
                (out/'report.json').write_text(json.dumps(report))
            elif script=='studio/godot_release_artifact_stage.py':
                if fail_stage=='artifact': return subprocess.CompletedProcess(args,1)
                if not artifact_credentials:
                    report={'engine':'godot','status':'godot_release_credentials_required','release_status':'human_action_required','completion':{'finished':False,'next_stage':'godot_release_qa'},'coverage':{'visual_qa':True}}
                else:
                    report={'engine':'godot','status':'godot_release_artifact_validated','release_status':'not_store_ready','completion':{'finished':False,'next_stage':'godot_store_metadata_qa'},'coverage':{'visual_qa':True,'release_artifact':True,'release_signed':True},'release_artifact':{'project_code_had_signing_material':False}}
                (out/'report.json').write_text(json.dumps(report))
            elif script=='studio/godot_store_metadata_stage.py':
                if fail_stage=='store': return subprocess.CompletedProcess(args,1)
                report={'engine':'godot','status':'godot_store_metadata_validated','release_status':'not_store_ready','completion':{'finished':False,'next_stage':'godot_privacy_security_qa'},'coverage':{'release_artifact':True,'release_signed':True,'store_metadata':True}}
                (out/'report.json').write_text(json.dumps(report))
            elif script=='studio/godot_privacy_security_stage.py':
                if fail_stage=='privacy': return subprocess.CompletedProcess(args,1)
                report={'engine':'godot','status':'godot_privacy_security_validated','release_status':'not_store_ready','completion':{'finished':False,'next_stage':'godot_final_review_qa'},'coverage':{'release_artifact':True,'release_signed':True,'store_metadata':True,'privacy_qa':True,'security_qa':True}}
                (out/'report.json').write_text(json.dumps(report))
            elif script=='studio/godot_final_review_stage.py':
                if fail_stage=='final': return subprocess.CompletedProcess(args,1)
                report={'engine':'godot','status':'godot_technical_store_ready','release_status':'technical_store_ready','completion':{'finished':False,'next_stage':'godot_play_submission'},'coverage':{'release_artifact':True,'release_signed':True,'store_metadata':True,'privacy_qa':True,'security_qa':True,'final_review':True}}
                (out/'report.json').write_text(json.dumps(report))
            elif script=='studio/godot_play_stage.py':
                if fail_stage=='play': return subprocess.CompletedProcess(args,1)
                report={'engine':'godot','status':'godot_play_validated','release_status':'play_validated','completion':{'finished':True,'next_stage':None},'coverage':{'release_artifact':True,'release_signed':True,'store_metadata':True,'privacy_qa':True,'security_qa':True,'final_review':True,'play_publish':True}}
                (out/'report.json').write_text(json.dumps(report))
            return subprocess.CompletedProcess(args,0)
        return runner,calls

    def test_godot_stops_cleanly_when_release_keystore_is_missing(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); out=root/'out'; req=self.request(root); runner,calls=self._runner(out)
            result=run_project(str(req),out,str(root/'work'),runner,100,lambda:0,'a'*40)
        self.assertEqual(result['status'],'human_action_required'); self.assertEqual(result['next_stage'],'godot_release_qa')
        self.assertTrue(any('studio/godot_release_stage.py' in call for call in calls)); self.assertFalse(any('studio/post_preview.py' in call for call in calls))

    def test_release_chain_reaches_human_play_submission_only(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); out=root/'out'; req=self.request(root); runner,calls=self._runner(out,release_ready=True)
            result=run_project(str(req),out,str(root/'work'),runner,100,lambda:0,'a'*40)
        self.assertEqual(result['status'],'human_action_required'); self.assertEqual(result['next_stage'],'godot_play_submission')
        self.assertTrue(any('studio/godot_final_review_stage.py' in call for call in calls))

    def test_opt_in_play_validation_can_complete_godot_pipeline(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); out=root/'out'
            request=dict(REQUEST)
            request['play_publish']={'enabled':True,'track':'internal','commit':False}
            req=root/'request.json'; req.write_text(json.dumps(request))
            runner,calls=self._runner(out,release_ready=True)
            result=run_project(str(req),out,str(root/'work'),runner,100,lambda:0,'a'*40)
        self.assertEqual(result['status'],'complete')
        self.assertIsNone(result['next_stage'])
        self.assertTrue(any('studio/godot_play_stage.py' in call for call in calls))

    def test_credentials_lost_between_preflight_and_signing_return_to_human_action(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); out=root/'out'; req=self.request(root); runner,_=self._runner(out,release_ready=True,artifact_credentials=False)
            result=run_project(str(req),out,str(root/'work'),runner,100,lambda:0,'a'*40)
        self.assertEqual(result['status'],'human_action_required'); self.assertEqual(result['next_stage'],'godot_release_qa')

    def test_each_failed_godot_stage_stays_on_itself(self):
        expected={'android':'godot_android_export_qa','device':'godot_device_qa','journey':'godot_runtime_journey_qa','visual':'godot_visual_qa','release':'godot_release_qa','artifact':'godot_release_artifact_qa','store':'godot_store_metadata_qa','privacy':'godot_privacy_security_qa','final':'godot_final_review_qa'}
        for failed,next_stage in expected.items():
            with self.subTest(failed=failed), tempfile.TemporaryDirectory() as td:
                root=Path(td); out=root/'out'; req=self.request(root); runner,_=self._runner(out,fail_stage=failed,release_ready=failed in {'artifact','store','privacy','final'})
                result=run_project(str(req),out,str(root/'work'),runner,100,lambda:0,'a'*40)
                self.assertEqual(result['status'],'failed'); self.assertEqual(result['next_stage'],next_stage)
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); out=root/'out'; req=self.request(root)
            runner,calls=self._runner(out,exhausted_preview=True)
            result=run_project(str(req),out,str(root/'work'),runner,100,lambda:0,'a'*40)
            self.assertEqual(result['status'],'blocked')
            self.assertEqual(result['next_stage'],'godot_preview_cycle_budget_exhausted')
            self.assertEqual(result['report']['checkpoint_commit'],'f'*40)
            self.assertEqual(len(calls),2)

    def test_journey_stage_cannot_fake_execution_coverage(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); out=root/'out'; req=self.request(root); runner,_=self._runner(out,bad_journey=True)
            with self.assertRaisesRegex(StudioError,'journey stage returned invalid coverage'):
                run_project(str(req),out,str(root/'work'),runner,100,lambda:0,'a'*40)

    def test_visual_stage_cannot_fake_visual_coverage(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); out=root/'out'; req=self.request(root); runner,_=self._runner(out,bad_visual=True)
            with self.assertRaisesRegex(StudioError,'visual stage returned invalid coverage'):
                run_project(str(req),out,str(root/'work'),runner,100,lambda:0,'a'*40)

    def test_missing_detection_evidence_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); req=self.request(root)
            def runner(args,timeout): return subprocess.CompletedProcess(args,0)
            with self.assertRaisesRegex(StudioError,'produced no evidence'):
                run_project(str(req),root/'out',str(root/'work'),runner,100,lambda:0,'a'*40)

        # An exact operator-approved *model* source-repair canary must bypass
        # the costly Godot game-generation pipeline. It must never fall back
        # to a deterministic patch or match unrelated projects/instructions.
        from production_os_jumpy_source_repair import contract, apply_model_guard
        from production_os_worker_canary import canary_instruction
        exact = {
            **REQUEST,
            "target_repo": "dbrckk/Jumpy",
            "repository_branch_id": "mp-" + "a" * 24,
            "production_os": {"workflow_id": "wf", "workflow_task_id": "implementation"},
            "brief": canary_instruction(40, "jumpy_share_clipboard_guard"),
        }
        self.assertEqual(contract(exact), 40)
        self.assertIsNone(contract({**exact, "target_repo": "other/repo"}))
        self.assertIsNone(contract({**exact, "brief": exact["brief"] + " extra"}))
        self.assertIsNone(contract({**exact, "repository_branch_id": "unsafe"}))
        with tempfile.TemporaryDirectory() as td, patch(
            "multi_engine_orchestrator.run_jumpy_source_repair"
        ) as repair:
            root = Path(td); req = root / "request.json"; req.write_text(json.dumps(exact))
            repair.return_value = {"status": "complete", "report": {}, "next_stage": None}
            def never_detect(*args, **kwargs):
                raise AssertionError("Exact source canary must not invoke game stages")
            marker = object()
            result = run_project(str(req), root / "out", str(root / "work"),
                                 never_detect, 100, lambda: 0, "a" * 40,
                                 checkpoint_observer=lambda item: marker)
            self.assertEqual(result["status"], "complete")
            repair.assert_called_once()

        # The model's narrowly reviewed contribution is a real GDScript
        # insertion. Baseline and successful-share analytics remain byte-identical.
        source = (
            "func share_score(score: int, daily: bool = false) -> void:\n"
            '\tvar text = "Score"\n'
            "\tDisplayServer.clipboard_set(text)\n"
            '\tevent("share_score", {"score": score, "daily": daily})\n'
            "func leaderboard_submit(score):\n\tpass\n"
        )
        answer = {"guard_lines": [
            "if not DisplayServer.has_feature(DisplayServer.FEATURE_CLIPBOARD):",
            'event("share_unavailable", {"reason": "clipboard_unsupported"})',
            "return",
        ]}
        fixed = apply_model_guard(source, answer)
        self.assertNotEqual(fixed, source)
        self.assertIn('event("share_score", {"score": score, "daily": daily})', fixed)
        self.assertEqual(
            fixed.replace(
                '\tif not DisplayServer.has_feature(DisplayServer.FEATURE_CLIPBOARD):\n'
                '\t\tevent("share_unavailable", {"reason": "clipboard_unsupported"})\n'
                '\t\treturn\n',
                "", 1,
            ),
            source,
        )
        with self.assertRaises(StudioError):
            apply_model_guard(source, {"guard_lines": ["return", "return", "return"]})
        with self.assertRaises(StudioError):
            apply_model_guard(fixed, answer)

        # A successful source edit or a draft PR is not a verified delivery.
        # Persist the exact CI gate in the execution checkpoint instead of
        # publishing a misleading local "passed" success.
        from target_ci_verification import finalize_source_delivery_evidence
        provisional = {"status": "pending", "passed": False,
                       "source_validation": "passed", "target_ci": "pending_exact_commit"}
        for ci, reviewed, expected_status, finished in (
            ({"status": "pending"}, False, "pending", False),
            ({"status": "pending", "run_id": 12}, True, "pending", False),
            ({"status": "failed", "run_id": 12}, True, "failed", False),
            ({"status": "passed", "run_id": 12}, False, "pending", False),
            ({"status": "passed", "run_id": 12}, True, "passed", True),
        ):
            evidence, complete = finalize_source_delivery_evidence(
                provisional, ci, pr_confirmed=reviewed)
            self.assertEqual(evidence["status"], expected_status)
            self.assertEqual(evidence["passed"], finished)
            self.assertEqual(complete, finished)
            self.assertEqual(evidence["source_validation"], "passed")
            self.assertEqual(evidence["target_ci"], ci["status"])
            if "run_id" in ci:
                self.assertEqual(evidence["target_ci_run_id"], ci["run_id"])
        self.assertEqual(provisional["status"], "pending")
        self.assertFalse(provisional["passed"])
        with self.assertRaises(StudioError):
            finalize_source_delivery_evidence(
                provisional, {"status": "not_validated"}, pr_confirmed=True)

        # The second public target uses the same bounded one-source engine.
        # A trusted source request must be exact; do not invoke the game engine.
        from production_os_bounded_source_repair import (
            contract as bounded_contract, apply_model_edit,
        )
        from production_os_source_tasks import TASKS, instruction
        from production_os_worker_canary import canary_instruction as approved_instruction
        task = TASKS["starlist_mcp_www_guard"]
        request = {
            **REQUEST,
            "target_repo": task.repo,
            "repository_branch_id": "mp-" + "a" * 24,
            "production_os": {"workflow_id": "wf", "workflow_task_id": "implementation"},
            "brief": instruction(41, task.task_id),
        }
        self.assertEqual(bounded_contract(request)[0], 41)
        self.assertEqual(approved_instruction(41, "approved_source_repair", task.task_id), request["brief"])
        for rejected in (
            {**request, "target_repo": "other/repo"},
            {**request, "brief": request["brief"] + " injected"},
            {**request, "repository_branch_id": "studio/main"},
            {**request, "production_os": {}},
        ):
            self.assertIsNone(bounded_contract(rejected))
        source = (
            "def check_websites(data, schema):\n"
            "    for site in []:\n"
            "        if site:\n"
            "            if site:\n"
            "                root = website.hostname.lower()\n"
            "    return None\n"
            "def other():\n    pass\n"
        )
        proposal = {"replacement_line": task.old_line + '.removeprefix("www.")'}
        updated = apply_model_edit(source, proposal, task)
        self.assertEqual(updated.replace(proposal["replacement_line"], task.old_line), source)
        for rejected in (
            {"replacement_line": '                root = __import__("os").system("env")'},
            {"replacement_line": "                root = website.hostname.lower()\nother()"},
            {"replacement_line": task.old_line},
            {"replacement_line": "    " + proposal["replacement_line"]},
            {"replacement_line": proposal["replacement_line"], "extra": "change"},
        ):
            with self.assertRaises(StudioError):
                apply_model_edit(source, rejected, task)
        with self.assertRaises(StudioError):
            apply_model_edit(updated, proposal, task)
        with tempfile.TemporaryDirectory() as td, patch(
            "multi_engine_orchestrator.run_bounded_source"
        ) as source_repair:
            root = Path(td); req_path = root / "request.json"
            req_path.write_text(json.dumps(request))
            source_repair.return_value = {"status": "blocked", "report": {}, "next_stage": "exact_commit_target_ci"}
            def never_detect(*args, **kwargs):
                raise AssertionError("Trusted source task must not invoke game-generation")
            observed = run_project(str(req_path), root / "out", str(root / "work"),
                                   never_detect, 100, lambda: 0, "a" * 40)
            self.assertEqual(observed["status"], "blocked")
            source_repair.assert_called_once()

        # PR creation and GitHub_TOKEN pull_request checks do not prove that
        # the independent, exact-commit Godot validation has actually passed.
        from target_ci_verification import inspect_exact_commit_ci
        source_sha = "f" * 40
        review_branch = "studio/mp-" + "a" * 24
        workflow_path = ".github/workflows/validate.yml"
        required_steps = (
            "Verify dispatched checkpoint identity",
            "Import and parse project",
            "Smoke-test touch routing and HUD input passthrough",
        )
        good_run = {"id": 12, "head_sha": source_sha,
                    "head_branch": review_branch, "path": workflow_path,
                    "event": "workflow_dispatch", "status": "completed",
                    "conclusion": "success"}
        good_job = {"status": "completed", "conclusion": "success",
                    "steps": [{"name": name, "status": "completed",
                               "conclusion": "success"} for name in required_steps]}

        class ReadOnlyGitHub:
            def __init__(self, runs, jobs=None):
                self.runs = runs
                self.jobs = [good_job] if jobs is None else jobs
            def get(self, endpoint):
                if endpoint.startswith("/actions/runs?"):
                    return {"workflow_runs": self.runs}
                if endpoint.endswith("/jobs?per_page=100"):
                    return {"total_count": len(self.jobs), "jobs": self.jobs}
                raise AssertionError("Unexpected CI endpoint")

        def inspect(client):
            return inspect_exact_commit_ci(
                client, commit_sha=source_sha, branch=review_branch,
                workflow_path=workflow_path, required_steps=required_steps)
        verified = inspect(ReadOnlyGitHub([good_run]))
        self.assertEqual(verified["status"], "passed")
        self.assertEqual(verified["commit_sha"], source_sha)
        for invalid in (
            {**good_run, "event": "pull_request"},
            {**good_run, "head_sha": "e" * 40},
            {**good_run, "head_branch": "main"},
            {**good_run, "path": ".github/workflows/other.yml"},
        ):
            self.assertEqual(inspect(ReadOnlyGitHub([invalid]))["status"], "pending")
        self.assertEqual(inspect(ReadOnlyGitHub([]))["status"], "pending")
        self.assertEqual(inspect(ReadOnlyGitHub([
            {**good_run, "status": "in_progress"}]))["status"], "pending")
        self.assertEqual(inspect(ReadOnlyGitHub([
            {**good_run, "conclusion": "failure"}]))["status"], "failed")
        self.assertEqual(inspect(ReadOnlyGitHub([
            good_run, {**good_run, "id": 13, "conclusion": "failure"}]))["status"], "failed")
        self.assertEqual(inspect(ReadOnlyGitHub([good_run], [
            {**good_job, "steps": good_job["steps"][:-1]}]))["status"], "failed")
        with self.assertRaises(StudioError):
            inspect_exact_commit_ci(
                ReadOnlyGitHub([good_run]), commit_sha="wrong",
                branch=review_branch, workflow_path=workflow_path,
                required_steps=required_steps)

if __name__=='__main__': unittest.main()
