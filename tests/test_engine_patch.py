from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))

from engine_patch import PatchPolicyError, validate


class EnginePatchTests(unittest.TestCase):
    def test_flutter_scope_remains_compatible(self):
        result = validate({'files': [{'path': 'lib/app.dart', 'content': 'void main() {}'}]}, 'flutter')
        self.assertEqual(result[0]['path'], 'lib/app.dart')

    def test_godot_implementation_accepts_project_text_scope(self):
        result = validate({'files': [
            {'path': 'scripts/player.gd', 'content': 'extends Node\n'},
            {'path': 'scenes/Main.tscn', 'content': '[gd_scene format=3]\n'},
        ]}, 'godot')
        self.assertEqual([x['path'] for x in result], ['scripts/player.gd', 'scenes/Main.tscn'])

        # Compact output contract: exact text edits are accepted only for
        # Godot implementation, never for QA or Flutter.
        edit = {'edits': [{'path': 'scripts/player.gd',
                           'find': 'if settings_open:\\n    start_game()',
                           'replace': 'if not settings_open:\\n    start_game()'}]}
        self.assertEqual(validate(edit, 'godot')[0]['path'], 'scripts/player.gd')
        for engine, role in (('flutter', 'implementation'), ('godot', 'tests')):
            with self.subTest(engine=engine, role=role), self.assertRaises(PatchPolicyError):
                validate(edit, engine, role)
        for invalid in (
            {'edits': []},
            {'edits': [{'path': '../escape.gd', 'find': 'x', 'replace': 'y'}]},
            {'edits': [{'path': 'scripts/player.gd', 'find': '', 'replace': 'y'}]},
            {'edits': [{'path': 'scripts/player.gd', 'find': 'x', 'replace': 'x'}]},
            {'edits': [{'path': 'scripts/player.gd', 'find': 'x', 'replace': 'y'},
                       {'path': 'scripts/player.gd', 'find': 'z', 'replace': 'w'}]},
            {'edits': [{'path': 'scripts/player.gd', 'find': 'x', 'replace': 'ghp_' + 'A' * 30}]},
            {'edits': [{'path': 'scripts/player.gd', 'find': 'x', 'replace': 'y', 'extra': 1}]},
            {'edits': [{'path': 'scripts/player.gd', 'find': 'x', 'replace': 'y' + chr(0)}]},
        ):
            with self.subTest(invalid=invalid), self.assertRaises(PatchPolicyError):
                validate(invalid, 'godot')

    def test_godot_rejects_workflow_binary_and_traversal(self):
        for path in ('.github/workflows/pwn.yml', 'assets/key.keystore', '../escape.gd'):
            with self.assertRaises(PatchPolicyError, msg=path):
                validate({'files': [{'path': path, 'content': 'x'}]}, 'godot')

    def test_engine_specific_test_roles_are_enforced(self):
        validate({'files': [{'path': 'tests/player.gd', 'content': 'extends Node\n'}]}, 'godot', 'tests')
        validate({'files': [{'path': 'test/app_test.dart', 'content': 'void main() {}'}]}, 'flutter', 'tests')
        with self.assertRaisesRegex(PatchPolicyError, 'Godot QA'):
            validate({'files': [{'path': 'scripts/player.gd', 'content': 'extends Node\n'}]}, 'godot', 'tests')
        with self.assertRaisesRegex(PatchPolicyError, 'Flutter QA'):
            validate({'files': [{'path': 'lib/app.dart', 'content': 'void main() {}'}]}, 'flutter', 'tests')

    def test_duplicate_empty_and_secret_content_fail_closed(self):
        with self.assertRaises(PatchPolicyError):
            validate({'files': [
                {'path': 'scripts/a.gd', 'content': 'x'},
                {'path': 'scripts/a.gd', 'content': 'y'},
            ]}, 'godot')
        with self.assertRaises(PatchPolicyError):
            validate({'files': [{'path': 'scripts/a.gd', 'content': ''}]}, 'godot')
        with self.assertRaisesRegex(PatchPolicyError, 'credential'):
            validate({'files': [{'path': 'scripts/a.gd', 'content': 'ghp_' + 'A' * 30}]}, 'godot')

    def test_unknown_engine_and_role_fail_closed(self):
        with self.assertRaises(Exception):
            validate({'files': [{'path': 'Assets/a.cs', 'content': 'x'}]}, 'unity')
        with self.assertRaisesRegex(PatchPolicyError, 'role'):
            validate({'files': [{'path': 'scripts/a.gd', 'content': 'x'}]}, 'godot', 'review')


if __name__ == '__main__':
    unittest.main()
