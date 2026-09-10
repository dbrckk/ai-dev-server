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

    def _runner(self,out,fail_stage=None,bad_journey=False,bad_visual=False,release_ready=False):
        calls=[]
        def runner(args,timeout):
            calls.append(args); out.mkdir(parents=True,exist_ok=True)
            script=next((x for x in args if isinstance(x,str) and x.startswith('studio/')),None)
            if script=='studio/engine_detect.py':
                (out/'engine-detection.json').write_text(json.dumps({'status':'detected','engine':'godot'}))
            elif script=='studio/engine_entry.py':
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
            return subprocess.CompletedProcess(args,0)
        return runner,calls

    def test_godot_stops_cleanly_when_release_keystore_is_missing(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); out=root/'out'; req=self.request(root); runner,calls=self._runner(out)
            result=run_project(str(req),out,str(root/'work'),runner,100,lambda:0,'a'*40)
        self.assertEqual(result['status'],'human_action_required'); self.assertEqual(result['next_stage'],'godot_release_qa')
        self.assertTrue(any('studio/godot_release_stage.py' in call for call in calls)); self.assertFalse(any('studio/post_preview.py' in call for call in calls))

    def test_release_inputs_advance_only_to_aab_artifact_qa(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); out=root/'out'; req=self.request(root); runner,_=self._runner(out,release_ready=True)
            result=run_project(str(req),out,str(root/'work'),runner,100,lambda:0,'a'*40)
        self.assertEqual(result['status'],'godot_release_preflight_ready'); self.assertEqual(result['next_stage'],'godot_release_artifact_qa')

    def test_each_failed_godot_stage_stays_on_itself(self):
        expected={'android':'godot_android_export_qa','device':'godot_device_qa','journey':'godot_runtime_journey_qa','visual':'godot_visual_qa','release':'godot_release_qa'}
        for failed,next_stage in expected.items():
            with self.subTest(failed=failed), tempfile.TemporaryDirectory() as td:
                root=Path(td); out=root/'out'; req=self.request(root); runner,_=self._runner(out,fail_stage=failed)
                result=run_project(str(req),out,str(root/'work'),runner,100,lambda:0,'a'*40)
                self.assertEqual(result['status'],'failed'); self.assertEqual(result['next_stage'],next_stage)

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

if __name__=='__main__': unittest.main()
