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
from core import request_check
from production_os_resume_objectives import OperatorClient, resume


@unittest.skipIf(ControlPlane is None, 'Production-OS installed by dedicated integration CI')
class RealServerWorkerTests(unittest.TestCase):
    def test_legacy_recovery_launch_is_idempotent_and_leaves_attempts_unchanged(self):
        with tempfile.TemporaryDirectory() as td:
            auth = TokenAuthorizer([{'name': 'test-operator', 'role': 'operator',
                                     'sha256': token_digest('operator-token')}])
            control = ControlPlane(str(Path(td) / 'state.sqlite'), authorizer=auth)
            goal = 'Verify the original repository and report real evidence'
            workflow = control.workflows.create(name='legacy', repository='dbrckk/integration-fixture',
                tasks=[WorkflowTaskSpec('implementation', 'Implement original goal', {
                    'handoff': {'repository': 'dbrckk/integration-fixture', 'task': goal, 'final_goal': goal}},
                    max_attempts=2)])
            for _ in range(2):
                control.workflows.dispatch_ready(workflow['id'])
                control.workflows.record_result(workflow['id'], 'implementation', succeeded=False)
            server = ThreadingHTTPServer(('127.0.0.1', 0), make_handler(control))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                client = OperatorClient(f'http://127.0.0.1:{server.server_port}', 'operator-token')
                result = resume(client, [workflow['id']], apply=True)
                self.assertEqual(result['objectives'][0]['status'], 'relaunched')
                duplicate = client.launch(workflow['id'], 'dbrckk/integration-fixture', goal)
                self.assertEqual(duplicate['project']['project_id'], result['objectives'][0]['project_id'])
                self.assertEqual(resume(client, [workflow['id']], apply=True)['objectives'][0]['status'], 'already_managed')
                projects = control.managed_projects.list()
                self.assertEqual(len(projects), 1)
                self.assertEqual(projects[0]['final_goal'], goal)
                original = control.workflows.get(workflow['id'])
                self.assertEqual(original['tasks'][0]['attempts'], 2)
                self.assertEqual(original['status'], 'failed')
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=2)

    def test_operator_recovery_preserves_goal_and_does_not_duplicate_active_generation(self):
        with tempfile.TemporaryDirectory() as td:
            auth = TokenAuthorizer([{'name': 'test-operator', 'role': 'operator',
                                     'sha256': token_digest('operator-token')}])
            control = ControlPlane(str(Path(td) / 'state.sqlite'), authorizer=auth)
            project = control.managed_projects.create(repository='dbrckk/integration-fixture',
                final_goal='Verify the existing repository and report real evidence', token_budget=5000)
            for _ in range(3):
                control.workflows.record_result(project['workflow_id'], 'implementation', succeeded=False)
            self.assertEqual(control.managed_projects.get(project['project_id'])['status'], 'NEEDS_ATTENTION')
            server = ThreadingHTTPServer(('127.0.0.1', 0), make_handler(control))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                client = OperatorClient(f'http://127.0.0.1:{server.server_port}', 'operator-token')
                result = resume(client, [project['workflow_id']], apply=True)
                self.assertEqual(result['objectives'][0]['status'], 'resumed')
                updated = control.managed_projects.get(project['project_id'])
                self.assertEqual(updated['generation'], 2)
                self.assertEqual(updated['final_goal'], project['final_goal'])
                self.assertEqual(updated['status'], 'ACTIVE')
                resume(client, [project['workflow_id']], apply=True)
                self.assertEqual(control.managed_projects.get(project['project_id'])['generation'], 2)
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=2)

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
                                'tool_contracts': {'skill_learning': {
                                    'schema': 'production-os/learned-skill/v1',
                                    'result_field': 'learned_skill',
                                    'max_procedure_steps': 12, 'optional': True}},
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
                    request = request_check(json.loads(request_path.read_text()))
                    self.assertTrue(request['tool_contracts']['skill_learning']['optional'])
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
