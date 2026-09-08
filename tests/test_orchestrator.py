import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))

from core import StudioError
from github_runner import main as github_main, run as github_run
from orchestrator import run_project


class OrchestratorTests(unittest.TestCase):
    def payload_for(self, args):
        if 'studio/post_preview.py' in args:
            return {'status': 'validated_preview', 'completion': {'finished': False, 'next_stage': 'real_device'}}
        if 'studio/device_stage.py' in args:
            return {'status': 'validated_preview', 'completion': {'finished': False, 'next_stage': 'capability_qa'}}
        if 'studio/capability_stage.py' in args:
            return {'status': 'validated_preview', 'completion': {'finished': False, 'next_stage': 'store_metadata'}}
        if 'studio/store_stage.py' in args:
            return {'status': 'validated_preview', 'completion': {'finished': False, 'next_stage': 'privacy_policy'}}
        if 'studio/privacy_stage.py' in args:
            return {'status': 'validated_preview', 'completion': {'finished': False, 'next_stage': 'security_scan'}}
        if 'studio/security_stage.py' in args:
            return {'status': 'finished', 'completion': {'finished': True, 'next_stage': None}}
        return {'status': 'validated_preview'}

    def test_full_pipeline_is_provider_neutral_and_reaches_finished(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = root / 'out'
            request = root / 'request.json'
            request.write_text('{}')
            calls = []
            def runner(args, timeout):
                calls.append(args)
                out.mkdir(parents=True, exist_ok=True)
                (out / 'report.json').write_text(json.dumps(self.payload_for(args)))
                return subprocess.CompletedProcess(args, 0)
            result = run_project(str(request), out, str(root / 'work'), runner, 1000, lambda: 0)
            self.assertEqual(result['status'], 'complete')
            expected = ['studio/run.py', 'studio/post_preview.py', 'studio/device_stage.py',
                        'studio/capability_stage.py', 'studio/store_stage.py',
                        'studio/privacy_stage.py', 'studio/security_stage.py']
            self.assertEqual(len(calls), len(expected))
            for call, script in zip(calls, expected):
                self.assertIn(script, call)

    def test_unregistered_required_stage_creates_adaptation_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = root / 'out'
            request = root / 'request.json'
            request.write_text('{}')
            def runner(args, timeout):
                out.mkdir(parents=True, exist_ok=True)
                if 'studio/run.py' in args:
                    report = {'status': 'validated_preview'}
                else:
                    report = {
                        'status': 'validated_preview',
                        'completion': {'finished': False, 'next_stage': 'billing_qa', 'blockers': ['billing_qa_missing']},
                        'release_evidence': {
                            'capability_qa': {
                                'passed': True,
                                'required_qa_stages': ['billing_qa'],
                                'permissions': [],
                                'reasons': [{'profile': 'billing_qa', 'source': 'dependency', 'value': 'in_app_purchase'}],
                            }
                        },
                    }
                (out / 'report.json').write_text(json.dumps(report))
                return subprocess.CompletedProcess(args, 0)
            result = run_project(str(request), out, str(root / 'work'), runner, 1000, lambda: 0)
            self.assertEqual(result['status'], 'adaptation_required')
            evolution = json.loads((out / 'evolution-request.json').read_text())
            self.assertEqual(evolution['status'], 'adaptation_required')
            self.assertTrue(any(g['value'] == 'billing_qa' for g in evolution['gaps']))

    def test_successful_stage_must_advance(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = root / 'out'
            request = root / 'request.json'
            request.write_text('{}')
            def runner(args, timeout):
                out.mkdir(parents=True, exist_ok=True)
                report = {'status': 'validated_preview'} if 'studio/run.py' in args else {
                    'status': 'validated_preview',
                    'completion': {'finished': False, 'next_stage': 'real_device'},
                }
                (out / 'report.json').write_text(json.dumps(report))
                return subprocess.CompletedProcess(args, 0)
            with self.assertRaisesRegex(StudioError, 'did not advance'):
                run_project(str(request), out, str(root / 'work'), runner, 1000, lambda: 0)


class GitHubRunnerTests(unittest.TestCase):
    def request(self, root):
        path = root / 'request.json'
        path.write_text(json.dumps({
            'id': 'app-one',
            'target_repo': 'owner/app-one',
            'app_name': 'app_one',
            'brief': 'Build a polished offline focus timer mobile application.',
            'enabled': True,
        }))
        return path

    def test_non_main_is_rejected_before_generation(self):
        with patch.dict('os.environ', {'GITHUB_REF': 'refs/heads/feature'}, clear=True):
            with self.assertRaisesRegex(StudioError, 'requires main'):
                github_main(['request.json'])

    def test_adapter_reports_complete_only_from_completion_pipeline(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            request = self.request(root)
            out = root / 'out'
            def runner(args, timeout):
                out.mkdir(parents=True, exist_ok=True)
                if 'studio/post_preview.py' in args:
                    report = {'status': 'finished', 'completion': {'finished': True, 'next_stage': None}}
                else:
                    report = {'status': 'validated_preview'}
                (out / 'report.json').write_text(json.dumps(report))
                return subprocess.CompletedProcess(args, 0)
            result = github_run(request, out, runner=runner, clock=lambda: 0, budget_seconds=1000)
            self.assertEqual(result['status'], 'complete')
            self.assertTrue(result['finished'])
            persisted = json.loads((out / 'github-pipeline.json').read_text())
            self.assertEqual(persisted['status'], 'complete')


if __name__ == '__main__':
    unittest.main()
