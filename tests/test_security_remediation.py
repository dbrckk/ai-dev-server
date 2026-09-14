import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from security_remediation import remediate, remediation_candidate


class SecurityRemediationTests(unittest.TestCase):
    def test_manifest_release_flags_are_hardened(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            manifest = root / "android/app/src/main/AndroidManifest.xml"
            manifest.parent.mkdir(parents=True)
            manifest.write_text(
                '<manifest><application android:debuggable="true" '
                'android:usesCleartextTraffic="true"/></manifest>'
            )
            evidence = {
                "blockers": [
                    "release_manifest_debuggable",
                    "cleartext_network_traffic_detected",
                ]
            }

            result = remediate(root, evidence)
            text = manifest.read_text()

        self.assertTrue(result["changed"])
        self.assertNotIn('android:debuggable="true"', text)
        self.assertIn('android:usesCleartextTraffic="false"', text)
        self.assertEqual(
            [item["action"] for item in result["actions"]],
            [
                "remove_release_debuggable_true",
                "disable_android_cleartext_traffic",
            ],
        )

    def test_source_http_endpoint_is_not_blindly_rewritten(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "lib/api.dart"
            source.parent.mkdir(parents=True)
            source.write_text('const endpoint = "http://internal.example";')
            evidence = {"blockers": ["cleartext_network_traffic_detected"]}

            result = remediate(root, evidence)

            self.assertFalse(result["changed"])
            self.assertEqual(
                source.read_text(),
                'const endpoint = "http://internal.example";',
            )

    def test_secrets_and_process_execution_are_not_auto_remediated(self):
        evidence = {
            "blockers": [
                "credential_material_detected",
                "runtime_process_execution_detected",
            ]
        }
        self.assertFalse(remediation_candidate(evidence))


if __name__ == "__main__":
    unittest.main()
