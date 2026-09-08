from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))
from ci_runner import _run_registered_stages
from core import StudioError
from stage_registry import STAGES, get_stage


class StageRegistryTests(unittest.TestCase):
    def test_registry_contains_all_release_stages_after_release_build(self):
        self.assertEqual(set(STAGES), {'real_device', 'store_metadata', 'privacy_policy', 'security_scan'})
        self.assertEqual(get_stage('security_scan').failed_status, 'security_failed')
        self.assertIsNone(get_stage('unknown'))

    def test_generic_runner_advances_until_finished(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'out'
            out.mkdir()
            project = {'file': 'control/mobile-requests/demo.json'}
            sequence = ['real_device', 'store_metadata', 'privacy_policy', 'security_scan']
            state = {'completion': {'finished': False, 'next_stage': sequence[0]}}
            (out / 'report.json').write_text(json.dumps(state))
            calls = []
            def runner(args, timeout):
                calls.append(args[1])
                current = json.loads((out / 'report.json').read_text())
                name = current['completion']['next_stage']
                index = sequence.index(name)
                current['completion'] = ({'finished': True, 'next_stage': None} if index == len(sequence) - 1
                                         else {'finished': False, 'next_stage': sequence[index + 1]})
                (out / 'report.json').write_text(json.dumps(current))
                return subprocess.CompletedProcess(args, 0)
            report, status = _run_registered_stages(project, out, '/work', state, 100, runner, lambda: 0)
            self.assertIsNone(status)
            self.assertTrue(report['completion']['finished'])
            self.assertEqual(calls, [STAGES[name].script for name in sequence])

    def test_success_without_state_advance_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'out'
            out.mkdir()
            state = {'completion': {'finished': False, 'next_stage': 'real_device'}}
            (out / 'report.json').write_text(json.dumps(state))
            def runner(args, timeout):
                return subprocess.CompletedProcess(args, 0)
            with self.assertRaisesRegex(StudioError, 'did not advance'):
                _run_registered_stages({'file': 'request.json'}, out, '/work', state, 100, runner, lambda: 0)

    def test_deadline_returns_stage_specific_deferred_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'out'
            out.mkdir()
            state = {'completion': {'finished': False, 'next_stage': 'privacy_policy'}}
            (out / 'report.json').write_text(json.dumps(state))
            report, status = _run_registered_stages({'file': 'request.json'}, out, '/work', state, 0, None, lambda: 1)
            self.assertEqual(status, 'deferred_privacy')
            self.assertEqual(report, state)


if __name__ == '__main__':
    unittest.main()
