from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))
from capability_qa import classify
from completion import apply_completion, next_stage, required_release_stages


class CapabilityQATests(unittest.TestCase):
    def make_app(self, root: Path, *, pubspec_extra: str = '', manifest_permissions=(), source='void main() {}'):
        (root / 'lib').mkdir(parents=True)
        (root / 'lib/main.dart').write_text(source)
        (root / 'pubspec.yaml').write_text(
            'name: demo\ndependencies:\n  flutter:\n    sdk: flutter\n' + pubspec_extra)
        target = root / 'android/app/src/main'
        target.mkdir(parents=True)
        permissions = ''.join(
            f'<uses-permission android:name="{permission}"/>' for permission in manifest_permissions)
        (target / 'AndroidManifest.xml').write_text(
            '<manifest xmlns:android="http://schemas.android.com/apk/res/android">' +
            permissions + '<application /></manifest>')

    def base_state(self):
        return {
            'status': 'validated_preview', 'validation_contract': 2,
            'code_review': {'passed': True}, 'visual_review': {'passed': True},
            'apk_sha256': 'a' * 64,
            'release_evidence': {
                'release_build': {'passed': True},
                'real_device': {'passed': True},
            },
        }

    def test_standard_app_requires_no_specialized_qa(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_app(root)
            evidence = classify(root)
            self.assertEqual(evidence['profiles'], ['standard'])
            self.assertEqual(evidence['required_qa_stages'], [])

    def test_game_dependency_requires_performance_qa(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_app(root, pubspec_extra='  flame: ^1.18.0\n')
            evidence = classify(root)
            self.assertIn('performance_qa', evidence['profiles'])
            self.assertEqual(evidence['required_qa_stages'], ['performance_qa'])

    def test_native_and_notification_permissions_require_distinct_qa(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_app(root, manifest_permissions=(
                'android.permission.CAMERA', 'android.permission.POST_NOTIFICATIONS'))
            evidence = classify(root)
            self.assertIn('native_qa', evidence['required_qa_stages'])
            self.assertIn('notification_qa', evidence['required_qa_stages'])

    def test_capability_requirements_block_finished_until_evidence_exists(self):
        state = self.base_state()
        state['release_evidence']['capability_qa'] = {
            'passed': True, 'required_qa_stages': ['performance_qa']}
        state['release_evidence'].update({
            'store_metadata': {'passed': True}, 'artwork_qa': {'passed': True}, 'privacy_policy': {'passed': True},
            'security_scan': {'passed': True},
        })
        self.assertEqual(next_stage(state), 'performance_qa')
        self.assertIn('performance_qa', required_release_stages(state))
        self.assertFalse(apply_completion(state)['finished'])
        state['release_evidence']['performance_qa'] = {'passed': True}
        self.assertTrue(apply_completion(state)['finished'])

    def test_untrusted_dynamic_stage_name_is_ignored(self):
        state = self.base_state()
        state['release_evidence']['capability_qa'] = {
            'passed': True, 'required_qa_stages': ['arbitrary_shell_stage']}
        stages = required_release_stages(state)
        self.assertNotIn('arbitrary_shell_stage', stages)


if __name__ == '__main__':
    unittest.main()
