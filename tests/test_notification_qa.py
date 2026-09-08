from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))
from notification_qa import _count_package_notifications, _dependencies, _manifest_permissions
from stage_registry import get_stage


class NotificationQATests(unittest.TestCase):
    def test_counts_only_target_package_notification_records(self):
        sample = '''NotificationRecord(0x1: pkg=com.example.demo user=UserHandle{0})\nNotificationRecord(0x2: pkg=com.other.app user=UserHandle{0})\nNotificationRecord(0x3: pkg=com.example.demo user=UserHandle{0})\n'''
        self.assertEqual(_count_package_notifications(sample, 'com.example.demo'), 2)
        self.assertEqual(_count_package_notifications(sample, 'com.missing'), 0)

    def test_detects_notification_dependency_and_permission(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'pubspec.yaml').write_text(
                'name: demo\ndependencies:\n  flutter:\n    sdk: flutter\n  flutter_local_notifications: ^1.0.0\n'
            )
            manifest = root / 'android/app/src/main/AndroidManifest.xml'
            manifest.parent.mkdir(parents=True)
            manifest.write_text(
                '<manifest xmlns:android="http://schemas.android.com/apk/res/android">'
                '<uses-permission android:name="android.permission.POST_NOTIFICATIONS"/>'
                '<application />'
                '</manifest>'
            )
            self.assertIn('flutter_local_notifications', _dependencies(root))
            self.assertIn('android.permission.POST_NOTIFICATIONS', _manifest_permissions(root))

    def test_notification_stage_is_registered(self):
        stage = get_stage('notification_qa')
        self.assertIsNotNone(stage)
        self.assertEqual(stage.script, 'studio/notification_stage.py')
        self.assertEqual(stage.failed_status, 'notification_failed')


if __name__ == '__main__':
    unittest.main()
