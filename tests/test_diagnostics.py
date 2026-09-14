import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from diagnostics import classify, repairable


class DiagnosticsTests(unittest.TestCase):
    def test_separates_code_environment_external_and_prerequisite(self):
        evidence = {
            "passed": False,
            "blockers": [
                "excessive_jank",
                "adb_unavailable",
                "play_billing_sandbox_purchase_not_verified",
                "release_apk_missing",
            ],
        }
        result = classify("performance_qa", evidence)
        self.assertEqual(result["code"], ["excessive_jank"])
        self.assertEqual(result["environment"], ["adb_unavailable"])
        self.assertEqual(
            result["human_or_external"],
            ["play_billing_sandbox_purchase_not_verified"],
        )
        self.assertEqual(result["prerequisite"], ["release_apk_missing"])

    def test_prefixed_runtime_failure_is_code_repairable(self):
        evidence = {
            "passed": False,
            "blockers": [
                "app_unstable_for_denied_permission_state:android.permission.CAMERA"
            ],
        }
        self.assertEqual(
            repairable("native_qa", evidence),
            [
                "app_unstable_for_denied_permission_state:android.permission.CAMERA"
            ],
        )


if __name__ == "__main__":
    unittest.main()
