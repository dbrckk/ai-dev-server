from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))
from native_qa import _declared_permissions, RUNTIME_PERMISSIONS
from stage_registry import get_stage


class NativeQATests(unittest.TestCase):
    def test_declared_runtime_permissions_are_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = root / 'android/app/src/main/AndroidManifest.xml'
            manifest.parent.mkdir(parents=True)
            manifest.write_text(
                '<manifest xmlns:android="http://schemas.android.com/apk/res/android">'
                '<uses-permission android:name="android.permission.CAMERA"/>'
                '<uses-permission android:name="android.permission.RECORD_AUDIO"/>'
                '<application />'
                '</manifest>'
            )
            permissions = _declared_permissions(root)
            self.assertEqual(permissions, ['android.permission.CAMERA', 'android.permission.RECORD_AUDIO'])
            self.assertTrue(set(permissions).issubset(RUNTIME_PERMISSIONS))

    def test_native_stage_is_registered(self):
        stage = get_stage('native_qa')
        self.assertIsNotNone(stage)
        self.assertEqual(stage.script, 'studio/native_stage.py')
        self.assertEqual(stage.failed_status, 'native_failed')


if __name__ == '__main__':
    unittest.main()
