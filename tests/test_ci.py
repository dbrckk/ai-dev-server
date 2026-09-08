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
    def test_separate_artifacts_and_continue_after_one_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            queue = root / 'requests'
            queue.mkdir()
            for i in range(2):
                (queue / f'p{i}.json').write_text(json.dumps({
                    'id': f'p{i}', 'target_repo': f'owner/app{i}', 'app_name': f'app{i}',
                    'brief': 'Build a simple offline timer application.', 'enabled': True}))
            calls = []
            def runner(args, timeout):
                calls.append(args)
                self.assertGreater(timeout, 0)
                return subprocess.CompletedProcess(args, 1 if len(calls) == 1 else 0)
            out = root / 'out'
            self.assertEqual(run_queue(queue, out, runner), 1)
            self.assertEqual(len(calls), 2)
            self.assertNotEqual(calls[0][-1], calls[1][-1])
            report = json.loads((out / 'queue.json').read_text())
            self.assertEqual([p['status'] for p in report['projects']], ['failed', 'finished'])

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
