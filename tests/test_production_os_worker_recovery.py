"""Regression coverage for acknowledged jobs and worker process outcomes."""
import json
import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from test_production_os_worker_runtime import _FakeClient, sample_job
from test_production_os_worker_cli import _Client
from production_os_worker import ProductionOSWorkerError, _failure_diagnostics, main, run_once


class WorkerRecoveryTests(unittest.TestCase):
    def test_persistence_diagnosis_identifies_component_without_publishing_messages(self):
        result = _failure_diagnostics(RuntimeError('Remote autonomous state persistence failed: local autonomous state unavailable'))
        self.assertEqual(result['error_component'], 'autonomous_state')
        self.assertEqual(result['error_reason'], 'local_autonomous_state_unavailable')
        result = _failure_diagnostics(RuntimeError('Remote provider health persistence failed: provider health fields invalid'))
        self.assertEqual(result['error_component'], 'provider_health')
        self.assertEqual(result['error_reason'], 'provider_health_fields_invalid')
        result = _failure_diagnostics(RuntimeError('Remote provider metrics persistence failed: credential-private-response'))
        self.assertEqual(result['error_component'], 'provider_metrics')
        self.assertNotIn('error_reason', result)
        self.assertNotIn('credential-private-response', json.dumps(result))
        from core import APIError
        from production_os_worker import _retryable_runner_error
        for permanent in (400, 401, 403, 404, 410, 422):
            self.assertFalse(_retryable_runner_error(APIError(permanent)))
            self.assertFalse(_retryable_runner_error(
                RuntimeError(f"All configured providers unavailable; last HTTP status {permanent}")))
            self.assertFalse(_retryable_runner_error(
                RuntimeError(f"provider temporarily unavailable; API HTTP {permanent}")))
        for transient in (429, 502, 503, 504):
            self.assertTrue(_retryable_runner_error(APIError(transient)))
            self.assertTrue(_retryable_runner_error(
                RuntimeError(f"provider unavailable; HTTP status {transient}")))
        self.assertTrue(_retryable_runner_error(TimeoutError("provider temporarily unavailable")))
        self.assertTrue(_retryable_runner_error(RuntimeError("provider temporarily unavailable")))
        self.assertFalse(_retryable_runner_error(RuntimeError("provider authorization denied")))
        from source_delivery_checkpoint import source_operation, SourceDeliveryHTTPError
        for stage in ("restore", "publish", "review", "target_ci"):
            with self.assertRaises(SourceDeliveryHTTPError) as raised:
                with source_operation(stage):
                    raise APIError(403)
            result = _failure_diagnostics(raised.exception)
            self.assertEqual(result["error_code"], "source_delivery_http_error")
            self.assertEqual(result["error_stage"], stage)
            self.assertEqual(result["error_http_status"], 403)
        with self.assertRaises(ValueError):
            SourceDeliveryHTTPError("private-response", 403)
        with self.assertRaises(ValueError):
            SourceDeliveryHTTPError("restore", "private-response")
    def test_runner_diagnostics_keep_http_status_and_never_publish_message(self):
        client = _FakeClient(sample_job())
        secret = 'sensitive-provider-response'
        def runner(*args, **kwargs):
            raise RuntimeError('All configured providers failed; last HTTP status 410 ' + secret)
        with tempfile.TemporaryDirectory() as td:
            result = run_once(client, worker_id='w', output_root=Path(td),
                              run_project=runner, capabilities=['python'], runner_retry_attempts=0)
            envelope = json.loads(next(Path(td).rglob('production-os-result.json')).read_text())
            self.assertEqual(envelope['evidence']['error_code'], 'provider_failed')
            self.assertEqual(envelope['evidence']['error_http_status'], 410)
            self.assertEqual(result['error']['error_http_status'], 410)
            self.assertNotIn(secret, json.dumps([client.calls, result, envelope]))

    def test_cli_passes_pinned_baseline_and_rejects_invalid_revision_before_registration(self):
        env = {'PRODUCTION_OS_URL': 'http://localhost:8787', 'PRODUCTION_OS_WORKER_TOKEN': 'test',
               'GITHUB_SHA': 'a' * 40}
        calls = []
        main(['--once'], environ=env, client_factory=_Client,
             run_once_fn=lambda *a, **kw: calls.append(kw) or {'status': 'idle'},
             capacity_provider=lambda env: {}, capabilities_provider=lambda env: ['python'])
        self.assertEqual(calls[0]['baseline_sha'], 'a' * 40)
        with self.assertRaisesRegex(RuntimeError, 'full commit SHA'):
            main(['--once', '--baseline-sha', 'bad'], environ=env,
                 client_factory=lambda *a: self.fail('must not register'))

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

        # Correlation alone cannot distinguish an earlier execution/continuation
        # of the same workflow task. Early runner returns must get fresh results.
        from github_runner import write_production_os_result
        from production_os_worker import build_studio_request
        for previous_status, current_status, continuation in (
            ('complete', 'adaptation_required', False),
            ('blocked', 'complete', False),
            ('active', 'complete', True),
        ):
            with self.subTest(previous=previous_status, current=current_status), tempfile.TemporaryDirectory() as td:
                client = _FakeClient(sample_job())
                request = build_studio_request(client.job)
                project_out = Path(td) / request['id']
                previous = {'status': previous_status, 'finished': previous_status == 'complete',
                            'commit_shas': ['a' * 40], 'usage': {'total_tokens': 777, 'runs': 1}}
                write_production_os_result(project_out, request, previous)
                calls = []
                current = {'status': current_status, 'finished': current_status == 'complete',
                           'usage': {'total_tokens': 7, 'runs': 1}}
                def runner(request_path, output, **kwargs):
                    calls.append(True)
                    if continuation and len(calls) == 1:
                        write_production_os_result(output, request, previous)
                        return {'status': 'active', 'finished': False}
                    return current
                result = run_once(client, worker_id='w', output_root=Path(td),
                                  run_project=runner, capabilities=['python'])
                self.assertEqual(result['status'], 'completed' if current['finished'] else 'failed')
                reported = json.loads((project_out / 'production-os-result.json').read_text())
                self.assertEqual(reported['evidence']['pipeline_status'], current_status)
                self.assertEqual(reported['usage'], current['usage'])
                self.assertEqual(reported['evidence']['commit_shas'], [])
                self.assertEqual(len(calls), 2 if continuation else 1)

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

        for capacity in (None, {'providers': []}):
            for cleanup_fails in (False, True):
                with self.subTest(capacity=capacity, cleanup_fails=cleanup_fails):
                    client = _FakeClient(sample_job())
                    heartbeat = client.heartbeat
                    lost = []
                    def lost_startup_response(*args, **kwargs):
                        response = heartbeat(*args, **kwargs)
                        if kwargs.get('active_job_keys'):
                            lost.append(True)
                            raise ProductionOSWorkerError('startup delivery unavailable')
                        if lost and cleanup_fails:
                            raise ProductionOSWorkerError('cleanup unavailable')
                        return response
                    with tempfile.TemporaryDirectory() as td, patch.object(
                        client, 'heartbeat', side_effect=lost_startup_response
                    ):
                        with self.assertRaisesRegex(ProductionOSWorkerError, '^startup delivery unavailable$'):
                            run_once(client, worker_id='w', output_root=Path(td),
                                     run_project=lambda *a, **kw: self.fail('must not start'),
                                     capabilities=['python'], capacity=capacity)
                    self.assertEqual([c[0] for c in client.calls],
                                     ['heartbeat', 'claim', 'ack', 'heartbeat', 'heartbeat'])
                    self.assertEqual(client.calls[-1][2], ())
                    self.assertEqual(client.calls[-1][3], capacity)

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
