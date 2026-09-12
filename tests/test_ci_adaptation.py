import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))
from ci_runner import run_queue


class QueueAdaptationTests(unittest.TestCase):
    def test_unknown_future_stage_becomes_adaptation_request_not_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            queue = root / 'requests'
            queue.mkdir()
            request = queue / 'future.json'
            request.write_text(json.dumps({
                'id': 'future',
                'target_repo': 'owner/future',
                'app_name': 'future_app',
                'brief': 'Build an app requiring a future capability not yet implemented by the factory.',
                'enabled': True,
            }))
            out = root / 'out'

            def payload(args):
                if 'studio/post_preview.py' in args:
                    return {'status': 'validated_preview', 'completion': {'finished': False, 'next_stage': 'real_device'}}
                if 'studio/device_stage.py' in args:
                    return {'status': 'validated_preview', 'completion': {'finished': False, 'next_stage': 'capability_qa'}}
                if 'studio/capability_stage.py' in args:
                    return {
                        'status': 'validated_preview',
                        'completion': {
                            'finished': False,
                            'next_stage': 'future_capability_qa',
                            'blockers': ['future_capability_qa_missing'],
                        },
                        'release_evidence': {
                            'capability_qa': {
                                'passed': True,
                                'required_qa_stages': ['future_capability_qa'],
                                'permissions': [],
                                'reasons': [
                                    {'profile': 'future_capability_qa', 'source': 'dependency', 'value': 'future_sdk'}
                                ],
                            }
                        },
                    }
                return {'status': 'validated_preview'}

            calls = []
            def runner(args, timeout):
                calls.append(args)
                project_out = Path(args[-1])
                project_out.mkdir(parents=True, exist_ok=True)
                (project_out / 'report.json').write_text(json.dumps(payload(args)))
                return subprocess.CompletedProcess(args, 0)

            with mock.patch.dict(os.environ, {'CIRCLE_SHA1': ''}, clear=False):
                self.assertEqual(run_queue(queue, out, runner), 1)
            self.assertEqual(len(calls), 4)
            queue_report = json.loads((out / 'queue.json').read_text())
            project = queue_report['projects'][0]
            self.assertEqual(project['status'], 'adaptation_required')
            self.assertEqual(project['next_stage'], 'future_capability_qa')

            evolution = json.loads((out / 'future/evolution-request.json').read_text())
            self.assertEqual(evolution['status'], 'adaptation_required')
            self.assertTrue(any(gap['value'] == 'future_capability_qa' for gap in evolution['gaps']))
            self.assertEqual(evolution['candidate_policy']['isolation'], 'dedicated_branch')
            self.assertEqual(evolution['candidate_policy']['promotion'], 'only_after_all_gates_pass')


if __name__ == '__main__':
    unittest.main()
