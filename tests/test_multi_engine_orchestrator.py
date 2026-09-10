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

    @patch('multi_engine_orchestrator.GitHub')
    @patch('multi_engine_orchestrator.detect_engine', return_value='flutter')
    @patch('multi_engine_orchestrator.run_flutter_project')
    def test_flutter_delegates_unchanged(self, legacy, detect, github):
        legacy.return_value = {'status':'complete','report':{'completion':{'finished':True}},'next_stage':None}
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); req = self.request(root)
            result = run_project(str(req), root/'out', str(root/'work'), object(), 100, lambda:0, 'a'*40)
        self.assertEqual(result['status'], 'complete')
        legacy.assert_called_once()

    @patch('multi_engine_orchestrator.GitHub')
    @patch('multi_engine_orchestrator.detect_engine', return_value='godot')
    def test_godot_runs_engine_entry_and_never_flutter_post_preview(self, detect, github):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); out = root/'out'; req = self.request(root); calls=[]
            def runner(args, timeout):
                calls.append(args); out.mkdir(parents=True, exist_ok=True)
                (out/'report.json').write_text(json.dumps({'engine':'godot','status':'godot_preview_validated','completion':{'finished':False,'next_stage':'godot_android_export_qa'}}))
                return subprocess.CompletedProcess(args, 0)
            result = run_project(str(req), out, str(root/'work'), runner, 100, lambda:0, 'a'*40)
        self.assertEqual(result['status'], 'godot_preview_ready')
        self.assertEqual(result['next_stage'], 'godot_android_export_qa')
        self.assertTrue(any('studio/engine_entry.py' in call for call in calls))
        self.assertFalse(any('studio/post_preview.py' in call for call in calls))

    @patch('multi_engine_orchestrator.GitHub')
    @patch('multi_engine_orchestrator.detect_engine', return_value='godot')
    def test_godot_cannot_claim_finished(self, detect, github):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); out = root/'out'; req = self.request(root)
            def runner(args, timeout):
                out.mkdir(parents=True, exist_ok=True)
                (out/'report.json').write_text(json.dumps({'engine':'godot','completion':{'finished':True,'next_stage':None}}))
                return subprocess.CompletedProcess(args, 0)
            with self.assertRaisesRegex(StudioError, 'must remain unfinished'):
                run_project(str(req), out, str(root/'work'), runner, 100, lambda:0, 'a'*40)

    @patch('multi_engine_orchestrator.GitHub')
    @patch('multi_engine_orchestrator.detect_engine', return_value='godot')
    def test_godot_wrong_next_stage_fails_closed(self, detect, github):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); out = root/'out'; req = self.request(root)
            def runner(args, timeout):
                out.mkdir(parents=True, exist_ok=True)
                (out/'report.json').write_text(json.dumps({'engine':'godot','completion':{'finished':False,'next_stage':'release_build'}}))
                return subprocess.CompletedProcess(args, 0)
            with self.assertRaisesRegex(StudioError, 'unexpected next stage'):
                run_project(str(req), out, str(root/'work'), runner, 100, lambda:0, 'a'*40)


if __name__ == '__main__': unittest.main()
