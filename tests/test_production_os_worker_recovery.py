"""Regression coverage for acknowledged jobs and worker process outcomes."""
import json
import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from test_production_os_worker_runtime import _FakeClient, sample_job
from test_production_os_worker_cli import _Client
from production_os_worker import ProductionOSWorkerError, main, run_once


class WorkerRecoveryTests(unittest.TestCase):
    def test_local_setup_failure_reports_failure_and_releases_active_slot(self):
        job = sample_job()
        del job['payload']['handoff']
        client = _FakeClient(job)
        with tempfile.TemporaryDirectory() as td:
            result = run_once(client, worker_id='w', output_root=Path(td),
                              run_project=lambda *a, **kw: self.fail('must not run'),
                              capabilities=['python'])
        self.assertEqual(result['status'], 'failed')
        self.assertEqual([c[0] for c in client.calls],
                         ['heartbeat', 'claim', 'ack', 'heartbeat', 'fail', 'heartbeat'])
        self.assertEqual(client.calls[-1][2], ())
        self.assertEqual(client.calls[-2][1]['result']['evidence']['pipeline_status'], 'setup_error')

    def test_corrupt_or_uncorrelated_results_never_complete_job(self):
        for corruption in ('json', 'workflow_id', 'workflow_task_id', 'project_id',
                           'target_repo', 'schema_version', 'succeeded', 'usage', 'evidence'):
            with self.subTest(corruption=corruption), tempfile.TemporaryDirectory() as td:
                client = _FakeClient(sample_job())
                def runner(request_path, project_out, **kwargs):
                    request = json.loads(request_path.read_text())
                    result = {
                        'schema_version': 'ai-dev-server/production-os-result/v1',
                        **request['production_os'], 'project_id': request['id'],
                        'target_repo': request['target_repo'], 'succeeded': True,
                        'status': 'complete', 'usage': {}, 'evidence': {},
                    }
                    result[corruption] = 'wrong'
                    (project_out / 'production-os-result.json').write_text(
                        '{' if corruption == 'json' else json.dumps(result))
                    return {'status': 'complete'}
                result = run_once(client, worker_id='w', output_root=Path(td),
                                  run_project=runner, capabilities=['python'])
                self.assertEqual(result['status'], 'failed')
                self.assertNotIn('complete', [c[0] for c in client.calls])
                self.assertEqual(client.calls[-1][2], ())
                self.assertEqual(client.calls[-2][1]['result']['evidence']['pipeline_status'], 'result_error')

    def test_invalid_timing_configuration_does_not_claim_job(self):
        for kwargs in ({'heartbeat_interval_seconds': math.nan},
                       {'heartbeat_interval_seconds': 0},
                       {'runner_retry_backoff_seconds': math.inf},
                       {'runner_retry_attempts': 11}):
            with self.subTest(kwargs=kwargs):
                client = _FakeClient(sample_job())
                with self.assertRaises(ProductionOSWorkerError):
                    run_once(client, worker_id='w', output_root=Path('unused'),
                             run_project=lambda *a, **kw: None, capabilities=['python'], **kwargs)
                self.assertEqual(client.calls, [])

    def test_uncertain_completion_delivery_does_not_report_opposite_outcome(self):
        client = _FakeClient(sample_job())
        with tempfile.TemporaryDirectory() as td, patch.object(
            client, 'complete', side_effect=ProductionOSWorkerError('delivery unavailable')
        ):
            with self.assertRaises(ProductionOSWorkerError):
                run_once(client, worker_id='w', output_root=Path(td),
                         run_project=lambda *a, **kw: {'status': 'complete', 'finished': True},
                         capabilities=['python'])
        self.assertNotIn('fail', [c[0] for c in client.calls])

    def _main(self, args, run_once_fn, **kwargs):
        return main(args, environ={'PRODUCTION_OS_URL': 'http://localhost:8787',
                                   'PRODUCTION_OS_WORKER_TOKEN': 'test'},
                    client_factory=_Client, run_once_fn=run_once_fn,
                    capacity_provider=lambda env: {}, capabilities_provider=lambda env: ['python'],
                    **kwargs)

    def test_bounded_failure_returns_nonzero_and_preserves_status_artifact(self):
        with tempfile.TemporaryDirectory() as td:
            status = Path(td) / 'status.json'
            self.assertEqual(self._main(['--once', '--status-file', str(status)],
                                        lambda *a, **kw: {'status': 'failed'}), 1)
            self.assertEqual(json.loads(status.read_text())['status'], 'failed')
        outcomes = iter([{'status': 'failed'}, {'status': 'completed'}])
        self.assertEqual(self._main(['--cycles', '2'], lambda *a, **kw: next(outcomes)), 1)

    def test_paused_and_draining_continuous_workers_sleep_between_polls(self):
        for state in ('paused', 'draining'):
            with self.subTest(state=state):
                waits = []
                def sleep(seconds):
                    waits.append(seconds)
                    raise KeyboardInterrupt
                self.assertEqual(self._main(['--continuous', '--poll-interval', '2'],
                                            lambda *a, **kw: {'status': state}, sleeper=sleep), 0)
                self.assertEqual(waits, [2.0])
