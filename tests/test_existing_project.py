import base64
from pathlib import Path
import tempfile
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))

from existing_project import ExistingProjectError, materialize, plan

SHA = 'a' * 40


def item(path, size=3, mode='100644', kind='blob', sha=SHA):
    return {'path': path, 'size': size, 'mode': mode, 'type': kind, 'sha': sha}


class ExistingProjectTests(unittest.TestCase):
    def test_plans_existing_godot_project_without_workflow_or_binary_assets(self):
        tree = {'truncated': False, 'tree': [
            item('project.godot'), item('scripts/player.gd'), item('scenes/Main.tscn'),
            item('README.md'), item('SETUP_REQUIRED.txt'), item('.github/workflows/validate.yml'),
            item('assets/sprite.png', size=100),
        ]}
        result = plan(tree, 'godot')
        paths = {entry['path'] for entry in result['files']}
        self.assertEqual(result['engine'], 'godot')
        self.assertIn('project.godot', paths)
        self.assertIn('scripts/player.gd', paths)
        self.assertIn('README.md', paths)
        self.assertNotIn('.github/workflows/validate.yml', paths)
        self.assertNotIn('assets/sprite.png', paths)

    def test_engine_mismatch_and_ambiguous_markers_fail_closed(self):
        with self.assertRaisesRegex(ExistingProjectError, 'does not match'):
            plan({'truncated': False, 'tree': [item('project.godot')]}, 'flutter')
        with self.assertRaisesRegex(ExistingProjectError, 'Ambiguous'):
            plan({'truncated': False, 'tree': [item('project.godot'), item('pubspec.yaml')]})

    def test_rejects_symlink_mode_large_file_and_truncated_tree(self):
        with self.assertRaisesRegex(ExistingProjectError, 'metadata'):
            plan({'truncated': False, 'tree': [item('project.godot', mode='120000')]})
        with self.assertRaisesRegex(ExistingProjectError, 'too large'):
            plan({'truncated': False, 'tree': [item('project.godot', size=700000)]})
        with self.assertRaisesRegex(ExistingProjectError, 'truncated'):
            plan({'truncated': True, 'tree': [item('project.godot')]})

    def test_materialize_validates_all_blobs_before_writing(self):
        import_plan = {'engine': 'godot', 'files': [
            {'path': 'project.godot', 'sha': 'a' * 40, 'size': 3},
            {'path': 'scripts/player.gd', 'sha': 'b' * 40, 'size': 4},
        ]}
        def fetch(sha):
            raw = b'abc' if sha.startswith('a') else b'xx'
            return {'encoding': 'base64', 'content': base64.b64encode(raw).decode()}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaisesRegex(ExistingProjectError, 'size mismatch'):
                materialize(root, import_plan, fetch)
            self.assertFalse((root / 'project.godot').exists())

    def test_materialize_writes_valid_utf8_snapshot(self):
        payloads = {'a' * 40: b'[application]\n', 'b' * 40: b'extends Node\n'}
        import_plan = {'engine': 'godot', 'files': [
            {'path': 'project.godot', 'sha': 'a' * 40, 'size': len(payloads['a' * 40])},
            {'path': 'scripts/player.gd', 'sha': 'b' * 40, 'size': len(payloads['b' * 40])},
        ]}
        def fetch(sha): return {'encoding': 'base64', 'content': base64.b64encode(payloads[sha]).decode()}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); materialize(root, import_plan, fetch)
            self.assertEqual((root / 'project.godot').read_text(), '[application]\n')
            self.assertEqual((root / 'scripts/player.gd').read_text(), 'extends Node\n')


if __name__ == '__main__':
    unittest.main()
