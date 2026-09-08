import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))
from privacy_audit import analyze, build_data_safety, build_privacy_package


class PrivacyAuditTests(unittest.TestCase):
    def make_app(self, root: Path, manifest: str, dart: str = 'void main() {}', pubspec: str = 'name: demo\ndependencies:\n  flutter:\n    sdk: flutter\n'):
        target = root / 'android/app/src/main'
        target.mkdir(parents=True)
        (target / 'AndroidManifest.xml').write_text(manifest)
        lib = root / 'lib'
        lib.mkdir()
        (lib / 'main.dart').write_text(dart)
        (root / 'pubspec.yaml').write_text(pubspec)

    def test_offline_app_can_derive_no_external_collection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_app(root, '<manifest xmlns:android="http://schemas.android.com/apk/res/android"><application /></manifest>')
            audit = analyze(root)
            self.assertFalse(audit['network_capable'])
            self.assertTrue(audit['can_assert_no_external_collection'])
            safety = build_data_safety(audit)
            self.assertEqual(safety['status'], 'derived')
            self.assertFalse(safety['data_collected'])
            self.assertFalse(safety['data_shared'])

    def test_internet_capability_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_app(root, '<manifest xmlns:android="http://schemas.android.com/apk/res/android"><uses-permission android:name="android.permission.INTERNET"/><application /></manifest>')
            audit = analyze(root)
            self.assertTrue(audit['network_capable'])
            self.assertFalse(audit['can_assert_no_external_collection'])
            self.assertIn('network_capability_requires_verified_data_flow_classification', audit['blockers'])
            self.assertEqual(build_data_safety(audit)['status'], 'needs_verified_classification')

    def test_sensitive_permission_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_app(root, '<manifest xmlns:android="http://schemas.android.com/apk/res/android"><uses-permission android:name="android.permission.CAMERA"/><application /></manifest>')
            audit = analyze(root)
            self.assertEqual(audit['sensitive_data_classes'], ['photos_or_videos'])
            self.assertFalse(audit['can_assert_no_external_collection'])

    def test_local_storage_is_reported_without_becoming_collection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_app(root, '<manifest xmlns:android="http://schemas.android.com/apk/res/android"><application /></manifest>', "import 'dart:io';\nvoid main(){ File('x').writeAsStringSync('y'); }")
            audit = analyze(root)
            self.assertTrue(audit['local_storage_detected'])
            self.assertTrue(audit['network_capable'])
            self.assertFalse(audit['can_assert_no_external_collection'])

    def test_package_writes_policy_and_data_safety_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'app'
            out = Path(tmp) / 'out'
            root.mkdir()
            self.make_app(root, '<manifest xmlns:android="http://schemas.android.com/apk/res/android"><application /></manifest>')
            state = {'release_evidence': {'store_metadata': {'listing': {'title': 'Demo'}}}}
            evidence = build_privacy_package(root, out, state)
            self.assertTrue(evidence['passed'])
            self.assertEqual(len(evidence['policy_sha256']), 64)
            self.assertEqual(len(evidence['data_safety_sha256']), 64)
            self.assertTrue((out / 'privacy/privacy-policy.md').is_file())
            payload = json.loads((out / 'privacy/data-safety.json').read_text())
            self.assertFalse(payload['data_safety']['data_collected'])
            self.assertTrue(payload['data_safety']['requires_human_legal_attestation'])


if __name__ == '__main__':
    unittest.main()
