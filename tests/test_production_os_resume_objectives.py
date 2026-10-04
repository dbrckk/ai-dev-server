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
                return {'projects': [dict(project)]} if path == '/v1/managed-projects' else {'project': dict(self.project)}
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
