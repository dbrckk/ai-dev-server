"""Exercise the worker against Production-OS's real authenticated HTTP API.

The dedicated CI job installs the pinned server and requires these tests.
The runner executes a deterministic Python artifact; no live LLM is involved.
"""
import json
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

    def _exercise(self, expected):
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
