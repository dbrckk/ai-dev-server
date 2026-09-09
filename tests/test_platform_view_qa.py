from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))

from platform_view_qa import _dependencies, _ui_classes
from stage_registry import STAGES


class PlatformViewQATests(unittest.TestCase):
    def test_platform_view_stage_is_registered(self):
        self.assertIn('platform_view_qa', STAGES)
        self.assertEqual(STAGES['platform_view_qa'].failed_status, 'platform_view_failed')

    def test_detects_supported_platform_view_dependencies(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'pubspec.yaml').write_text(
                'name: demo\ndependencies:\n  flutter:\n    sdk: flutter\n  webview_flutter: ^4.0.0\n  video_player: ^2.0.0\n')
            self.assertEqual(_dependencies(root), ['video_player', 'webview_flutter'])

    def test_native_ui_classes_are_parsed(self):
        xml = '<hierarchy><node class="android.webkit.WebView"/><node class="android.view.TextureView"/></hierarchy>'
        self.assertEqual(_ui_classes(xml), {'android.webkit.WebView', 'android.view.TextureView'})

    def test_unrelated_dependency_does_not_require_platform_view(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'pubspec.yaml').write_text('name: demo\ndependencies:\n  flutter:\n    sdk: flutter\n  shared_preferences: ^2.0.0\n')
            self.assertEqual(_dependencies(root), [])


if __name__ == '__main__':
    unittest.main()
