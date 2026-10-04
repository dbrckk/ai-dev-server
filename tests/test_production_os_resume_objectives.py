import unittest
from production_os_resume_objectives import resume


class ResumeObjectivesTests(unittest.TestCase):
    def client(self):
        workflow_id, project_id = 'a' * 32, 'b' * 32
        project = {'project_id': project_id, 'current_workflow_id': workflow_id,
                   'status': 'NEEDS_ATTENTION', 'current_workflow': {'status': 'failed'}}
        class Client:
            def __init__(self):
                self.submissions = []
                self.project = project
            def get(self, path):
                if path == '/v1/managed-projects':
                    return {'projects': [dict(project)]}
                if path.startswith('/v1/workflows/'):
                    return {'workflow': {'status': 'running'}}
                return {'project': dict(self.project)}
            def continue_project(self, pid):
                self.submissions.append(pid)
                self.project = {**project, 'current_workflow_id': 'c' * 32, 'status': 'ACTIVE'}
                return {'project': dict(self.project)}
        return Client()

    def test_dry_run_does_not_mutate_and_apply_submits_only_once(self):
        client = self.client()
        self.assertEqual(resume(client, ['a' * 32])['objectives'][0]['status'], 'eligible')
        self.assertEqual(client.submissions, [])
        result = resume(client, ['a' * 32], apply=True)
        self.assertEqual(result['objectives'][0]['new_workflow_id'], 'c' * 32)
        resume(client, ['a' * 32], apply=True)
        self.assertEqual(client.submissions, ['b' * 32])

    def test_active_successful_and_changed_workflows_are_never_resumed(self):
        for change in ({'status': 'ACTIVE'}, {'current_workflow': {'status': 'succeeded'}},
                       {'current_workflow_id': 'd' * 32}):
            with self.subTest(change=change):
                client = self.client()
                client.project.update(change)
                resume(client, ['a' * 32], apply=True)
                self.assertEqual(client.submissions, [])

    def test_invalid_and_duplicate_allowlists_fail_before_access(self):
        for ids in ([], ['a' * 32] * 2, ['bad'], ['../escape'], ['a' * 32] * 6):
            with self.subTest(ids=ids), self.assertRaises(ValueError):
                resume(None, ids, apply=True)

    def test_legacy_goal_launch_preserves_original_instruction_and_reuses_request_id(self):
        launches = []
        class Client:
            def get(self, path):
                if path == '/v1/managed-projects':
                    return {'projects': []}
                return {'workflow': {'status': 'failed', 'repository': 'owner/repo', 'tasks': [
                    {'status': 'failed', 'payload': {'handoff': {'final_goal': 'Original goal'}}}]}}
            def launch(self, workflow_id, repository, final_goal):
                launches.append((workflow_id, repository, final_goal))
                return {'project': {'project_id': 'b' * 32, 'current_workflow_id': 'c' * 32,
                                    'repository': repository, 'final_goal': final_goal}}
        self.assertEqual(resume(Client(), ['a' * 32])['objectives'][0]['status'], 'legacy_eligible')
        self.assertEqual(launches, [])
        self.assertEqual(resume(Client(), ['a' * 32], apply=True)['objectives'][0]['status'], 'relaunched')
        self.assertEqual(launches, [('a' * 32, 'owner/repo', 'Original goal')])

    def test_managed_history_cannot_be_relaunched_as_legacy(self):
        class Client:
            def get(self, path):
                if path == '/v1/managed-projects':
                    return {'projects': [{'runs': [{'workflow_id': 'a' * 32}]}]}
                raise AssertionError('Must not inspect or launch a managed history entry')
        self.assertEqual(resume(Client(), ['a' * 32], apply=True)['objectives'][0]['status'], 'not_current')
