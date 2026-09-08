import tempfile
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))

from core import allowed
from project_context import render, write


class ProjectContextTests(unittest.TestCase):
    def request(self):
        return {
            'id': 'focus-app',
            'target_repo': 'owner/focus-app',
            'app_name': 'focus_app',
            'brief': 'Build a polished focus timer with local sessions and accessible controls.',
        }

    def state(self):
        return {
            'status': 'validated_preview',
            'product': {
                'acceptance_criteria': ['Start and stop a focus session', 'Persist session history locally'],
                'journeys': [{'id': 'start-session', 'steps': []}],
                'assumptions': ['No account is required for the initial release'],
            },
            'blockers': [],
            'completion': {
                'finished': False,
                'next_stage': 'real_device',
                'required_stages': ['release_build', 'real_device', 'capability_qa'],
                'blockers': ['real_device_missing'],
            },
            'release_evidence': {
                'release_build': {'passed': True},
                'capability_qa': {'passed': True, 'profiles': ['standard']},
            },
        }

    def test_render_uses_trusted_state_and_next_stage(self):
        text = render(self.request(), self.state())
        self.assertIn('focus_app — Project Context', text)
        self.assertIn('Start and stop a focus session', text)
        self.assertIn('`real_device`', text)
        self.assertIn('real_device_missing', text)
        self.assertIn('release_build', text)
        self.assertIn('Do not infer completion', text)
        self.assertNotIn('Project is finished', text)

    def test_write_creates_root_handoff_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = write(root, self.request(), self.state())
            self.assertEqual(path, root / 'PROJECT_CONTEXT.md')
            self.assertTrue(path.is_file())
            self.assertIn('Resume instructions', path.read_text())

    def test_model_patch_scope_cannot_edit_trusted_context(self):
        self.assertFalse(allowed('PROJECT_CONTEXT.md'))
        self.assertTrue(allowed('docs/product.md'))

    def test_no_evidence_is_not_presented_as_success(self):
        state = {'status': 'pending', 'blockers': []}
        text = render(self.request(), state)
        self.assertIn('No release evidence is recorded yet.', text)
        self.assertIn('Release stages have not yet been derived.', text)
        self.assertIn('not classified yet', text)


if __name__ == '__main__':
    unittest.main()
