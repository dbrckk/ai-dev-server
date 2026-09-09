from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))

from evolution_isolated_runner import (
    _capability_result, _docker_python, _parse_unittest, _trusted_flutter_smoke,
    IsolatedRunError,
)


class IsolatedEvolutionRunnerTests(unittest.TestCase):
    def test_unittest_parser_requires_real_collected_tests(self):
        passed = _parse_unittest('Ran 3 tests in 0.01s\n\nOK\n', 0)
        self.assertEqual(passed, {'passed': True, 'count': 3, 'failures': 0, 'errors': 0})
        empty = _parse_unittest('OK\n', 0)
        self.assertFalse(empty['passed'])
        failed = _parse_unittest('Ran 3 tests in 0.01s\nFAILED (failures=1, errors=1)\n', 1)
        self.assertEqual(failed['failures'], 1)
        self.assertEqual(failed['errors'], 1)
        self.assertFalse(failed['passed'])

    @patch('evolution_isolated_runner.shutil.which', return_value='/usr/bin/docker')
    @patch('evolution_isolated_runner._run')
    def test_candidate_python_runs_without_network_or_writable_repo(self, run, which):
        run.return_value = subprocess.CompletedProcess([], 0, '', '')
        root = Path('/tmp/candidate')
        _docker_python(root, ['-m', 'unittest', 'discover', '-s', 'tests'])
        command = run.call_args.args[0]
        self.assertIn('--network', command)
        self.assertEqual(command[command.index('--network') + 1], 'none')
        self.assertIn('--read-only', command)
        self.assertIn('--cap-drop', command)
        self.assertEqual(command[command.index('--cap-drop') + 1], 'ALL')
        self.assertIn('no-new-privileges', command)
        mount = command[command.index('-v') + 1]
        self.assertTrue(mount.endswith(':/workspace:ro'))
        joined = ' '.join(command)
        self.assertNotIn('GITHUB_TOKEN', joined)
        self.assertNotIn('STUDIO_API_KEY', joined)

    @patch('evolution_isolated_runner._run')
    def test_trusted_smoke_uses_unique_scrubbed_root(self, run):
        run.return_value = subprocess.CompletedProcess([], 0, '', '')
        smoke_root = Path('/tmp/evolution-smoke-never-created')
        self.assertTrue(_trusted_flutter_smoke(Path('/repo'), smoke_root))
        env = run.call_args.kwargs['env']
        self.assertEqual(env['STUDIO_SMOKE_ROOT'], str(smoke_root))
        self.assertNotIn('GITHUB_TOKEN', env)
        self.assertNotIn('STUDIO_API_KEY', env)
        self.assertEqual(run.call_args.args[0], ['python3', 'studio/smoke.py'])

    def test_capability_evidence_is_counted_not_invented(self):
        failed = _capability_result('future_qa', 4, False)
        self.assertEqual(failed['assertions_passed'], 0)
        passed = _capability_result('future_qa', 4, True)
        self.assertEqual(passed['assertions_passed'], 4)
        with self.assertRaises(IsolatedRunError):
            _capability_result('future_qa', 0, True)

    @patch('evolution_isolated_runner.shutil.which', return_value=None)
    def test_missing_docker_fails_closed(self, which):
        with self.assertRaisesRegex(IsolatedRunError, 'Docker unavailable'):
            _docker_python(Path('/tmp/candidate'), ['-m', 'unittest'])


if __name__ == '__main__':
    unittest.main()
