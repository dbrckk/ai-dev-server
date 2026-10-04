"""Exercise the worker against Production-OS's real authenticated HTTP API.

The dedicated CI job installs the pinned server and requires these tests.
The runner executes a deterministic Python artifact; no live LLM is involved.
"""
import json
import io
import textwrap
from contextlib import redirect_stdout
from unittest.mock import patch
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path

try:
    from production_os.api_auth import TokenAuthorizer, token_digest
    from production_os.control_plane import ControlPlane, make_handler
    from production_os.workflow_engine import WorkflowTaskSpec
except ModuleNotFoundError as exc:
    if exc.name != 'production_os' or os.environ.get('REQUIRE_PRODUCTION_OS_INTEGRATION') == '1':
        raise
    ControlPlane = None


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))
from production_os_worker import ProductionOSClient, run_once


@unittest.skipIf(ControlPlane is None, 'Production-OS installed by dedicated integration CI')
class RealServerWorkerTests(unittest.TestCase):
    def test_worker_only_session_executes_and_reports_real_workflow(self):
        self._exercise('completed')

    def test_unreadable_result_is_reported_to_real_server(self):
        self._exercise('failed')

    def test_actions_preflight_recovers_interrupted_job_before_idle_check(self):
        self._exercise('completed', abandon=True)

    def _exercise(self, expected, abandon=False):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            auth = TokenAuthorizer([{
                'name': 'github-actions-worker', 'role': 'worker',
                'sha256': token_digest('integration-token'),
            }])
            control = ControlPlane(str(root / 'state.sqlite'), authorizer=auth)
            workflow = control.workflows.create(
                name='worker-integration', repository='dbrckk/integration-fixture',
                tasks=[WorkflowTaskSpec('verify', 'Run Python verification', {
                    'required_capabilities': ['python'],
                    'handoff': {'repository': 'dbrckk/integration-fixture',
                                'token_budget': 5000,
                                'task': 'Run Python verification of the generated artifact'},
                })],
            )
            jobs = control.workflows.dispatch_ready(workflow['id'])
            self.assertEqual(len(jobs), 1)
            server = ThreadingHTTPServer(('127.0.0.1', 0), make_handler(control))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                client = ProductionOSClient(f'http://127.0.0.1:{server.server_port}',
                                            'integration-token')
                # No operator token: validates real /v1/workers/session permissions.
                client.register('github-actions-worker', ['python'])
                if abandon:
                    abandoned = client.claim('github-actions-worker', ['python'])
                    client.ack(abandoned['key'], 'github-actions-worker')
                    self.assertFalse(client._post('/v1/jobs/availability', {
                        'worker_id': 'github-actions-worker', 'capabilities': ['python'],
                    })['available'])
                    workflow_source = (Path(__file__).resolve().parents[1] /
                        '.github/workflows/production-os-actions-worker.yml').read_text()
                    block = workflow_source.split('- name: Probe compatible Production-OS work', 1)[1]
                    block = block.split("python - <<'PY'\n", 1)[1].split('\n          PY', 1)[0]
                    outputs = root / 'github-output'
                    with patch.dict(os.environ, {
                        'PRODUCTION_OS_URL': client.base_url,
                        'PRODUCTION_OS_WORKER_TOKEN': 'integration-token',
                        'PRODUCTION_OS_WORKER_ID': 'github-actions-worker',
                        'GITHUB_OUTPUT': str(outputs),
                    }, clear=True), patch('production_os_worker.worker_capabilities', return_value=['python']), redirect_stdout(io.StringIO()):
                        exec(compile(textwrap.dedent(block), 'actions-worker-preflight', 'exec'), {})
                    self.assertIn('base_available=true', outputs.read_text())
                    self.assertEqual(control.queue.get(abandoned['key'])['status'], 'queued')

                executed = []
                def runner(request_path, project_out, **kwargs):
                    artifact = project_out / 'verify.py'
                    artifact.write_text('assert sum([1, 2, 3]) == 6\nprint("verified")\n')
                    proc = subprocess.run([sys.executable, str(artifact)], check=True,
                                          capture_output=True, text=True, timeout=10)
                    executed.append(proc.stdout.strip())
                    if expected == 'failed':
                        (project_out / 'production-os-result.json').write_text('{')
                    return {'status': 'complete', 'finished': True, 'usage': {}}
                result = run_once(client, worker_id='github-actions-worker',
                                  output_root=root / 'output', run_project=runner,
                                  capabilities=['python'], heartbeat_interval_seconds=0.05)
                self.assertEqual(executed, ['verified'])
                self.assertEqual(result['status'], expected)
                current = control.workflows.get(workflow['id'])
                self.assertEqual(current['status'], 'succeeded' if expected == 'completed' else 'failed')
                self.assertEqual(current['tasks'][0]['status'], 'succeeded' if expected == 'completed' else 'failed')
                self.assertEqual(run_once(client, worker_id='github-actions-worker',
                                          output_root=root / 'output', run_project=runner,
                                          capabilities=['python'])['status'], 'idle')
                self.assertEqual(executed, ['verified'])
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=2)
