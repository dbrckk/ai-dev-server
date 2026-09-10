import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))

from core import StudioError
from multi_engine_orchestrator import run_project

REQUEST = {'id':'demo-v1','target_repo':'owner/app','app_name':'demo_app','brief':'Build a complete polished mobile application.','enabled':True,'max_rounds':2,'max_calls':8,'max_cycles':3}


class MultiEngineOrchestratorTests(unittest.TestCase):
    def request(self, root):
        path = root / 'request.json'; path.write_text(json.dumps(REQUEST)); return path

    @patch('multi_engine_orchestrator.run_flutter_project')
    def test_flutter_delegates_unchanged(self, legacy):
        legacy.return_value = {'status':'complete','report':{'completion':{'finished':True}},'next_stage':None}
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); out = root/'out'; req = self.request(root); calls=[]
            def runner(args, timeout):
                calls.append(args); out.mkdir(parents=True, exist_ok=True)
                if 'studio/engine_detect.py' in args:
                    (out/'engine-detection.json').write_text(json.dumps({'status':'detected','engine':'flutter'}))
                return subprocess.CompletedProcess(args, 0)
            result = run_project(str(req), out, str(root/'work'), runner, 100, lambda:0, 'a'*40)
        self.assertEqual(result['status'], 'complete')
        legacy.assert_called_once()

    def _runner(self, out, android_ok=True, android_completion=None):
        calls=[]
        def runner(args, timeout):
            calls.append(args); out.mkdir(parents=True, exist_ok=True)
            if 'studio/engine_detect.py' in args:
                (out/'engine-detection.json').write_text(json.dumps({'status':'detected','engine':'godot'}))
            elif 'studio/engine_entry.py' in args:
                (out/'report.json').write_text(json.dumps({'engine':'godot','status':'godot_preview_validated','completion':{'finished':False,'next_stage':'godot_android_export_qa'}}))
            elif 'studio/godot_android_stage.py' in args:
                if android_ok:
                    completion = android_completion or {'finished':False,'next_stage':'godot_device_qa'}
                    (out/'report.json').write_text(json.dumps({'engine':'godot','status':'godot_android_export_validated','completion':completion}))
                    return subprocess.CompletedProcess(args, 0)
                return subprocess.CompletedProcess(args, 1)
            return subprocess.CompletedProcess(args, 0)
        return runner, calls

    def test_godot_chains_preview_to_android_then_device(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); out=root/'out'; req=self.request(root); runner,calls=self._runner(out)
            result=run_project(str(req),out,str(root/'work'),runner,100,lambda:0,'a'*40)
        self.assertEqual(result['status'],'godot_android_ready')
        self.assertEqual(result['next_stage'],'godot_device_qa')
        self.assertTrue(any('studio/engine_entry.py' in call for call in calls))
        self.assertTrue(any('studio/godot_android_stage.py' in call for call in calls))
        self.assertFalse(any('studio/post_preview.py' in call for call in calls))

    def test_android_failure_stays_on_android_stage(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); out=root/'out'; req=self.request(root); runner,_=self._runner(out,android_ok=False)
            result=run_project(str(req),out,str(root/'work'),runner,100,lambda:0,'a'*40)
        self.assertEqual(result['status'],'failed')
        self.assertEqual(result['next_stage'],'godot_android_export_qa')

    def test_android_cannot_claim_finished(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); out=root/'out'; req=self.request(root); runner,_=self._runner(out,android_completion={'finished':True,'next_stage':None})
            with self.assertRaisesRegex(StudioError,'advance only to device QA'):
                run_project(str(req),out,str(root/'work'),runner,100,lambda:0,'a'*40)

    def test_missing_detection_evidence_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); req=self.request(root)
            def runner(args, timeout): return subprocess.CompletedProcess(args,0)
            with self.assertRaisesRegex(StudioError,'produced no evidence'):
                run_project(str(req),root/'out',str(root/'work'),runner,100,lambda:0,'a'*40)


if __name__ == '__main__': unittest.main()
