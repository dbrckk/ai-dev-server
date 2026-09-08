import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))
from ci_runner import run_queue


MISSING_STAGE = 'future_capability_qa'


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
                            'next_stage': MISSING_STAGE,
                            'blockers': [MISSING_STAGE + '_missing'],
                        },
                        'release_evidence': {
                            'capability_qa': {
                                'passed': True,
                                'required_qa_stages': [MISSING_STAGE],
                                'permissions': [],
                                'reasons': [
                                    {'profile': MISSING_STAGE, 'source': 'source_marker', 'value': 'future_capability'}
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

            self.assertEqual(run_queue(queue, out, runner), 1)
            self.assertEqual(len(calls), 4)
            queue_report = json.loads((out / 'queue.json').read_text())
            project = queue_report['projects'][0]
            self.assertEqual(project['status'], 'adaptation_required')
            self.assertEqual(project['next_stage'], MISSING_STAGE)

            evolution = json.loads((out / 'future/evolution-request.json').read_text())
            self.assertEqual(evolution['status'], 'adaptation_required')
            self.assertTrue(any(gap['value'] == MISSING_STAGE for gap in evolution['gaps']))
            self.assertEqual(evolution['candidate_policy']['isolation'], 'dedicated_branch')
            self.assertEqual(evolution['candidate_policy']['promotion'], 'only_after_all_gates_pass')


if __name__ == '__main__':
    unittest.main()
