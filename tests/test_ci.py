import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))
from ci_provider import enabled, selected
from ci_runner import run_queue, main
from core import StudioError

class ProviderTests(unittest.TestCase):
    def test_exactly_one_owner(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'ci.json'
            for owner in ('github', 'circleci', 'disabled'):
                p.write_text(json.dumps({'provider': owner}))
                self.assertEqual(enabled('github', p), owner == 'github')
                self.assertEqual(enabled('circleci', p), owner == 'circleci')

    def test_invalid_policy_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'ci.json'
            for value in ({}, {'provider': 'auto'}, {'provider': 'circleci', 'extra': True}, []):
                p.write_text(json.dumps(value))
                with self.assertRaises(StudioError):
                    selected(p)

    def test_non_main_rejected_before_provider_or_model_access(self):
        with patch.dict('os.environ', {'CIRCLE_BRANCH': 'feature'}, clear=True):
            with self.assertRaisesRegex(StudioError, 'require main'):
                main()

class QueueRunnerTests(unittest.TestCase):
    def make_requests(self, root, count=2):
        queue = root / 'requests'
        queue.mkdir()
        for i in range(count):
            (queue / f'p{i}.json').write_text(json.dumps({
                'id': f'p{i}', 'target_repo': f'owner/app{i}', 'app_name': f'app{i}',
                'brief': 'Build a simple offline timer application.', 'enabled': True}))
        return queue

    def payload_for(self, args):
        if 'studio/post_preview.py' in args:
            return {'status': 'validated_preview', 'completion': {'finished': False, 'next_stage': 'real_device'}}
        if 'studio/device_stage.py' in args:
            return {'status': 'validated_preview', 'completion': {'finished': False, 'next_stage': 'capability_qa'}}
        if 'studio/capability_stage.py' in args:
            return {'status': 'validated_preview', 'completion': {'finished': False, 'next_stage': 'store_metadata'}}
        if 'studio/store_stage.py' in args:
            return {'status': 'validated_preview', 'completion': {'finished': False, 'next_stage': 'artwork_qa'}}
        if 'studio/artwork_stage.py' in args:
            return {'status': 'validated_preview', 'completion': {'finished': False, 'next_stage': 'privacy_policy'}}
        if 'studio/privacy_stage.py' in args:
            return {'status': 'validated_preview', 'completion': {'finished': False, 'next_stage': 'security_scan'}}
        if 'studio/security_stage.py' in args:
            return {'status': 'finished', 'completion': {'finished': True, 'next_stage': None}}
        return {'status': 'validated_preview'}

    def test_separate_artifacts_and_continue_after_one_preview_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            queue = self.make_requests(root)
            out = root / 'out'
            calls = []
            def runner(args, timeout):
                calls.append(args)
                self.assertGreater(timeout, 0)
                if 'studio/run.py' in args and args[2].endswith('p0.json'):
                    return subprocess.CompletedProcess(args, 1)
                project_out = Path(args[-1])
                project_out.mkdir(parents=True, exist_ok=True)
                (project_out / 'report.json').write_text(json.dumps(self.payload_for(args)))
                return subprocess.CompletedProcess(args, 0)
            self.assertEqual(run_queue(queue, out, runner), 1)
            self.assertEqual(len(calls), 9)
            report = json.loads((out / 'queue.json').read_text())
            self.assertEqual([p['status'] for p in report['projects']], ['failed', 'complete'])
            self.assertIsNone(report['projects'][1]['next_stage'])

    def test_preview_success_chains_every_stage_to_finished(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            queue = self.make_requests(root, 1)
            out = root / 'out'
            calls = []
            def runner(args, timeout):
                calls.append(args)
                project_out = Path(args[-1])
                project_out.mkdir(parents=True, exist_ok=True)
                (project_out / 'report.json').write_text(json.dumps(self.payload_for(args)))
                return subprocess.CompletedProcess(args, 0)
            self.assertEqual(run_queue(queue, out, runner), 0)
            self.assertEqual(len(calls), 8)
            expected = ['studio/run.py', 'studio/post_preview.py', 'studio/device_stage.py',
                        'studio/capability_stage.py', 'studio/store_stage.py',
                        'studio/artwork_stage.py', 'studio/privacy_stage.py', 'studio/security_stage.py']
            for call, script in zip(calls, expected):
                self.assertIn(script, call)
            report = json.loads((out / 'queue.json').read_text())
            self.assertEqual(report['projects'][0]['status'], 'complete')
            self.assertIsNone(report['projects'][0]['next_stage'])

    def test_security_failure_is_not_reported_as_complete(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            queue = self.make_requests(root, 1)
            out = root / 'out'
            def runner(args, timeout):
                project_out = Path(args[-1])
                project_out.mkdir(parents=True, exist_ok=True)
                (project_out / 'report.json').write_text(json.dumps(self.payload_for(args)))
                if 'studio/security_stage.py' in args:
                    return subprocess.CompletedProcess(args, 1)
                return subprocess.CompletedProcess(args, 0)
            self.assertEqual(run_queue(queue, out, runner), 1)
            report = json.loads((out / 'queue.json').read_text())
            self.assertEqual(report['projects'][0]['status'], 'security_failed')

    def test_entire_queue_validated_before_generation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'invalid.json').write_text('{}')
            with patch('ci_runner.subprocess.run') as execute:
                with self.assertRaises(StudioError):
                    run_queue(root, root / 'out', execute)
                execute.assert_not_called()

    def test_empty_queue_requires_no_credentials(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(run_queue(root, root / 'out'), 0)


    def test_persistent_mode_uses_goal_wrapper(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            queue = self.make_requests(root, 1)
            out = root / 'out'
            with patch.dict('os.environ', {'STUDIO_PERSISTENT_GOALS': '1'}, clear=False), \
                    patch('ci_runner.run_persistent_project') as persistent:
                persistent.return_value = {
                    'status': 'complete',
                    'human_action': None,
                    'blocked_reason': None,
                }
                self.assertEqual(run_queue(queue, out, runner=lambda *a, **k: None), 0)
                persistent.assert_called_once()
            report = json.loads((out / 'queue.json').read_text())
            self.assertEqual(report['projects'][0]['status'], 'complete')
            self.assertIsNone(report['projects'][0]['next_stage'])

class RecoveryTests(unittest.TestCase):
    def make_queue(self, root):
        queue = root / 'requests'
        queue.mkdir()
        for i in range(2):
            (queue / f'p{i}.json').write_text(json.dumps({
                'id': f'p{i}', 'target_repo': f'owner/app{i}', 'app_name': f'app{i}',
                'brief': 'Build a simple offline timer application.', 'enabled': True}))
        return queue

    def test_timeout_preserves_progress_and_defers_remaining_work(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            queue = self.make_queue(root)
            out = root / 'out'
            calls = []
            def runner(args, timeout):
                calls.append(args)
                report = json.loads((out / 'queue.json').read_text())
                self.assertEqual([p['status'] for p in report['projects']], ['running', 'pending'])
                raise subprocess.TimeoutExpired(args, timeout)
            self.assertEqual(run_queue(queue, out, runner), 1)
            self.assertEqual(len(calls), 1)
            report = json.loads((out / 'queue.json').read_text())
            self.assertEqual([p['status'] for p in report['projects']], ['timed_out', 'deferred'])

    def test_worker_launch_failure_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            queue = self.make_queue(root)
            out = root / 'out'
            def runner(*args, **kwargs):
                raise OSError('private detail')
            self.assertEqual(run_queue(queue, out, runner), 1)
            text = (out / 'queue.json').read_text()
            self.assertNotIn('private detail', text)
            self.assertEqual([p['status'] for p in json.loads(text)['projects']], ['worker_error', 'deferred'])

    def test_timeout_kills_group_and_only_removes_labeled_containers(self):
        from ci_runner import bounded_run
        from unittest.mock import Mock
        process = Mock(pid=12345)
        process.wait.side_effect = [subprocess.TimeoutExpired('worker', 1), 0, 0]
        with patch('ci_runner.subprocess.Popen', return_value=process) as popen, patch('ci_runner.os.killpg') as kill, patch('ci_runner.subprocess.run') as docker:
            docker.return_value.stdout = 'container1\n'
            with self.assertRaises(subprocess.TimeoutExpired):
                bounded_run(['worker'], timeout=1)
            self.assertTrue(popen.call_args.kwargs['start_new_session'])
            run_id = popen.call_args.kwargs['env']['STUDIO_RUN_ID']
            self.assertEqual(len(run_id), 32)
            self.assertEqual(kill.call_count, 2)
            self.assertIn('label=mobile-studio-run=' + run_id, docker.call_args_list[0].args[0])
            self.assertEqual(docker.call_args_list[1].args[0], ['docker', 'rm', '-f', 'container1'])
