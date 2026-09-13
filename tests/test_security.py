import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))
from security_audit import android_permissions, build_security_package, dependency_inventory, scan


class SecurityAuditTests(unittest.TestCase):
    def make_app(self, root: Path, manifest: str = '<manifest xmlns:android="http://schemas.android.com/apk/res/android"><application /></manifest>', dart: str = 'void main() {}', lock: str | None = None, pubspec: str = 'name: demo\ndependencies:\n  flutter:\n    sdk: flutter\n'):
        target = root / 'android/app/src/main'
        target.mkdir(parents=True)
        (target / 'AndroidManifest.xml').write_text(manifest)
        lib = root / 'lib'
        lib.mkdir()
        (lib / 'main.dart').write_text(dart)
        (root / 'pubspec.yaml').write_text(pubspec)
        if lock is not None:
            (root / 'pubspec.lock').write_text(lock)

    def test_clean_offline_app_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_app(root)
            audit = scan(root)
            self.assertTrue(audit['passed'])
            self.assertEqual(audit['blockers'], [])

    def test_secret_material_fails_closed_without_exposing_value(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_app(root, dart="const token = 'sk-abcdefghijklmnopqrstuvwxyz123456';")
            audit = scan(root)
            self.assertFalse(audit['passed'])
            self.assertIn('credential_material_detected', audit['blockers'])
            self.assertEqual(audit['secrets'][0]['type'], 'openai_key')
            self.assertNotIn('abcdefghijklmnopqrstuvwxyz', json.dumps(audit))

    def test_cleartext_endpoint_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_app(root, dart="const endpoint = 'http://example.test/api';")
            audit = scan(root)
            self.assertFalse(audit['passed'])
            self.assertIn('cleartext_network_traffic_detected', audit['blockers'])

    def test_android_schema_url_is_not_mistaken_for_cleartext_endpoint(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_app(root)
            self.assertTrue(scan(root)['passed'])

    def test_dangerous_permission_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = '<manifest xmlns:android="http://schemas.android.com/apk/res/android"><uses-permission android:name="android.permission.READ_SMS"/><application /></manifest>'
            self.make_app(root, manifest=manifest)
            audit = scan(root)
            self.assertEqual(android_permissions(root), ['android.permission.READ_SMS'])
            self.assertIn('dangerous_android_permissions_require_explicit_review', audit['blockers'])

    def test_lockfile_inventory_records_versions_and_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            lock = '''packages:\n  characters:\n    dependency: transitive\n    description:\n      name: characters\n    source: hosted\n    version: "1.4.0"\n  flutter:\n    dependency: direct main\n    description: flutter\n    source: sdk\n    version: "0.0.0"\n'''
            self.make_app(root, lock=lock)
            inventory = dependency_inventory(root)
            self.assertEqual(inventory[0]['name'], 'characters')
            self.assertEqual(inventory[0]['version'], '1.4.0')
            self.assertEqual(inventory[0]['source'], 'hosted')

    def test_git_or_path_dependency_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pubspec = '''name: demo\ndependencies:\n  flutter:\n    sdk: flutter\n  unsafe_pkg:\n    git: https://example.test/repo.git\n'''
            self.make_app(root, pubspec=pubspec)
            audit = scan(root)
            self.assertIn('unreviewed_git_or_path_dependency', audit['blockers'])

    def test_hosted_dependency_requires_content_hash_and_trusted_registry(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            lock = '''packages:
  demo_pkg:
    dependency: direct main
    description:
      name: demo_pkg
      url: "https://packages.example.invalid"
    source: hosted
    version: "1.2.3"
'''
            self.make_app(root, lock=lock)
            audit = scan(root)
            self.assertIn('unreviewed_hosted_registry:demo_pkg', audit['blockers'])
            self.assertIn('hosted_dependency_without_content_hash:demo_pkg', audit['blockers'])

    def test_cached_mit_license_and_hash_produce_resolved_dependency_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            digest = 'a' * 64
            lock = f'''packages:
  demo_pkg:
    dependency: direct main
    description:
      name: demo_pkg
      sha256: "{digest}"
      url: "https://pub.dev"
    source: hosted
    version: "1.2.3"
'''
            self.make_app(root, lock=lock)
            cache = root / '.studio-cache/pub/hosted/pub.dev/demo_pkg-1.2.3'
            cache.mkdir(parents=True)
            (cache / 'LICENSE').write_text(
                'Permission is hereby granted, free of charge, to any person obtaining a copy '
                'of this software and associated documentation files.'
            )
            audit = scan(root)
            self.assertTrue(audit['passed'])
            dep = audit['dependencies'][0]
            self.assertEqual(dep['sha256'], digest)
            self.assertEqual(dep['registry'], 'https://pub.dev')
            self.assertEqual(audit['dependency_licenses'][0]['license'], 'MIT')

    def test_unknown_dependency_license_blocks_release(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            digest = 'b' * 64
            lock = f'''packages:
  mystery_pkg:
    dependency: direct main
    description:
      name: mystery_pkg
      sha256: "{digest}"
      url: "https://pub.dev"
    source: hosted
    version: "9.9.9"
'''
            self.make_app(root, lock=lock)
            cache = root / '.studio-cache/pub/hosted/pub.dev/mystery_pkg-9.9.9'
            cache.mkdir(parents=True)
            (cache / 'LICENSE').write_text('Custom proprietary terms.')
            audit = scan(root)
            self.assertFalse(audit['passed'])
            self.assertIn('dependency_license_unresolved:mystery_pkg', audit['blockers'])

    def test_package_writes_hashed_audit_and_sbom(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'app'
            out = Path(tmp) / 'out'
            root.mkdir()
            self.make_app(root)
            evidence = build_security_package(root, out)
            self.assertTrue(evidence['passed'])
            self.assertEqual(len(evidence['audit_sha256']), 64)
            self.assertEqual(len(evidence['sbom_sha256']), 64)
            self.assertTrue((out / 'security/audit.json').is_file())
            self.assertTrue((out / 'security/sbom.json').is_file())


if __name__ == '__main__':
    unittest.main()
