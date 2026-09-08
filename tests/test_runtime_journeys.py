import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / 'studio'))
from runtime_journeys import render_test, run_on_device


JOURNEYS = [{
    'id': 'settings',
    'steps': [
        {'action': 'tap', 'key': 'settings_button'},
        {'action': 'expect_text', 'value': 'Settings'},
    ],
}]


class RuntimeJourneyTests(unittest.TestCase):
    def test_render_uses_immutable_keys_and_ids(self):
        text = render_test('sample_app', JOURNEYS)
        self.assertIn("package:sample_app/app.dart", text)
        self.assertIn('studio-runtime:', text)
        self.assertIn('ValueKey<String>', text)

    def test_runner_restores_pubspec_and_lock(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / 'pubspec.yaml').write_text('name: sample_app\n')
            (root / 'pubspec.lock').write_text('original-lock')
            calls = []
            def runner(args, **kwargs):
                calls.append(args)
                if args[:3] == ['flutter', 'pub', 'add']:
                    (root / 'pubspec.yaml').write_text('changed')
                    (root / 'pubspec.lock').write_text('changed-lock')
                return subprocess.CompletedProcess(args, 0, stdout='ok')
            result = run_on_device(root, JOURNEYS, 'emulator-5554', runner=runner)
            self.assertTrue(result['passed'])
            self.assertEqual(result['journey_ids'], ['settings'])
            self.assertEqual((root / 'pubspec.yaml').read_text(), 'name: sample_app\n')
            self.assertEqual((root / 'pubspec.lock').read_text(), 'original-lock')
            self.assertFalse((root / 'integration_test/__studio_runtime_journeys_test.dart').exists())
            self.assertEqual(len(calls), 2)

    def test_failed_instrumentation_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / 'pubspec.yaml').write_text('name: sample_app\n')
            def runner(args, **kwargs):
                rc = 1 if args[:2] == ['flutter', 'test'] else 0
                return subprocess.CompletedProcess(args, rc, stdout='failed' if rc else 'ok')
            result = run_on_device(root, JOURNEYS, 'emulator-5554', runner=runner)
            self.assertFalse(result['passed'])
            self.assertIn('runtime_journey_failed', result['blockers'])


if __name__ == '__main__':
    unittest.main()
