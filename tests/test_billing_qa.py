from pathlib import Path
import hashlib
import json
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))

from billing_qa import validate_billing, validate_sandbox_evidence
from core import StudioError
from stage_registry import STAGES


class BillingQATests(unittest.TestCase):
    def make_app(self, root: Path):
        (root / 'android/app/src/main').mkdir(parents=True)
        (root / 'android/app/src/main/AndroidManifest.xml').write_text(
            '<manifest package="com.example.billing"><application /></manifest>')
        (root / 'lib').mkdir()
        (root / 'lib/main.dart').write_text('final billing = InAppPurchase.instance;')
        (root / 'pubspec.yaml').write_text(
            'name: billing_app\ndependencies:\n  flutter:\n    sdk: flutter\n  in_app_purchase: ^3.2.0\n')
        apk = root / 'build/app/outputs/flutter-apk/app-release.apk'
        apk.parent.mkdir(parents=True)
        apk.write_bytes(b'x' * 2000)
        return apk

    def evidence(self, apk: Path):
        return {
            'schema': 1,
            'provider': 'google_play_billing_sandbox',
            'package': 'com.example.billing',
            'apk_sha256': hashlib.sha256(apk.read_bytes()).hexdigest(),
            'tester_mode': True,
            'outcomes': {
                'product_query': {'passed': True},
                'purchase_success': {'passed': True},
                'purchase_cancel': {'passed': True},
                'purchase_restore': {'passed': True},
            },
        }

    def test_billing_stage_is_registered(self):
        self.assertIn('billing_qa', STAGES)
        self.assertEqual(STAGES['billing_qa'].failed_status, 'billing_failed')

    def test_without_play_sandbox_evidence_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'app'
            out = Path(tmp) / 'out'
            apk = self.make_app(root)
            result = validate_billing(root, out)
            self.assertFalse(result['passed'])
            self.assertEqual(result['apk_sha256'], hashlib.sha256(apk.read_bytes()).hexdigest())
            self.assertIn('play_billing_sandbox_purchase_not_verified', result['blockers'])
            self.assertIn('in_app_purchase', result['dependencies'])

    def test_matching_play_sandbox_evidence_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'app'
            out = Path(tmp) / 'out'
            out.mkdir()
            apk = self.make_app(root)
            (out / 'billing-sandbox-evidence.json').write_text(json.dumps(self.evidence(apk)))
            result = validate_billing(root, out)
            self.assertTrue(result['passed'])
            self.assertTrue(result['sandbox_verified'])
            self.assertEqual(result['blockers'], [])

    def test_wrong_apk_hash_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'app'
            apk = self.make_app(root)
            value = self.evidence(apk)
            value['apk_sha256'] = '0' * 64
            with self.assertRaisesRegex(StudioError, 'does not match'):
                validate_sandbox_evidence(value, 'com.example.billing', hashlib.sha256(apk.read_bytes()).hexdigest())

    def test_incomplete_purchase_lifecycle_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'app'
            apk = self.make_app(root)
            value = self.evidence(apk)
            value['outcomes'].pop('purchase_restore')
            with self.assertRaisesRegex(StudioError, 'incomplete'):
                validate_sandbox_evidence(value, 'com.example.billing', hashlib.sha256(apk.read_bytes()).hexdigest())


if __name__ == '__main__':
    unittest.main()
