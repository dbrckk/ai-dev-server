from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))

from project_engine import EngineError, editable, infer, profile, restorable


class ProjectEngineTests(unittest.TestCase):
    def test_infers_flutter_from_pubspec(self):
        self.assertEqual(infer(['README.md', 'pubspec.yaml', 'lib/app.dart']).name, 'flutter')

    def test_infers_godot_from_project_file(self):
        self.assertEqual(infer(['README.md', 'project.godot', 'scripts/player.gd']).name, 'godot')

    def test_ambiguous_or_unknown_project_fails_closed(self):
        with self.assertRaisesRegex(EngineError, 'Ambiguous'):
            infer(['pubspec.yaml', 'project.godot'])
        with self.assertRaisesRegex(EngineError, 'no trusted marker'):
            infer(['README.md', 'src/main.kt'])

    def test_godot_edit_scope_is_bounded_to_text_project_files(self):
        for path in ['project.godot','export_presets.cfg','scripts/player.gd','scenes/Main.tscn','assets/theme.tres','assets/icon.svg','tests/test_player.gd','docs/GAME_DESIGN.md']:
            self.assertTrue(editable(path, 'godot'), path)
        for path in ['.github/workflows/validate.yml','../escape.gd','/tmp/evil.gd','scripts/tool.py','assets/private.keystore','android/build.gradle','README.md']:
            self.assertFalse(editable(path, 'godot'), path)

    def test_godot_restore_can_read_production_docs_without_making_them_model_editable(self):
        for path in ('README.md','SETUP_REQUIRED.txt','THIRD_PARTY_NOTICES.md','.gitignore'):
            self.assertTrue(restorable(path,'godot'),path); self.assertFalse(editable(path,'godot'),path)

    def test_flutter_policy_remains_compatible(self):
        self.assertTrue(editable('lib/app.dart','flutter')); self.assertTrue(editable('test/app_test.dart','flutter')); self.assertTrue(editable('assets/logo.svg','flutter'))
        self.assertFalse(editable('android/app/build.gradle','flutter')); self.assertTrue(restorable('pubspec.lock','flutter'))

    def test_unknown_engine_is_rejected(self):
        with self.assertRaisesRegex(EngineError,'Unsupported'): profile('unity')
        with self.assertRaisesRegex(EngineError,'Unsupported'): editable('Assets/game.cs','unity')


if __name__ == '__main__': unittest.main()
