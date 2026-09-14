import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from diff_quick_gates import plan


class DiffQuickGateTests(unittest.TestCase):
    def test_lib_change_skips_dependency_gate_and_targets_matching_test(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            test = root / "test/services/api_test.dart"
            test.parent.mkdir(parents=True)
            test.write_text("void main() {}\n")

            result = plan(root, ["lib/services/api.dart"])

        self.assertFalse(result["dependency"])
        self.assertTrue(result["analyze"])
        self.assertTrue(result["test"])
        self.assertEqual(result["targeted_tests"], ["test/services/api_test.dart"])
        self.assertEqual(result["test_mode"], "targeted")

    def test_import_impact_selects_non_matching_test_name(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "pubspec.yaml").write_text("name: demo_app\n")
            test = root / "test/integration/network_flow_test.dart"
            test.parent.mkdir(parents=True)
            test.write_text(
                "import 'package:demo_app/services/api.dart';\nvoid main() {}\n"
            )

            result = plan(root, ["lib/services/api.dart"])

        self.assertEqual(
            result["targeted_tests"],
            ["test/integration/network_flow_test.dart"],
        )
        self.assertEqual(result["test_mode"], "targeted")


    def test_pubspec_change_requires_dependency_and_analyze_but_not_quick_tests(self):
        with tempfile.TemporaryDirectory() as td:
            result = plan(Path(td), ["pubspec.yaml"])

        self.assertTrue(result["dependency"])
        self.assertTrue(result["analyze"])
        self.assertFalse(result["test"])
        self.assertEqual(result["test_mode"], "skip")

    def test_asset_only_change_skips_all_quick_gates(self):
        with tempfile.TemporaryDirectory() as td:
            result = plan(Path(td), ["assets/icon.svg"])

        self.assertFalse(result["dependency"])
        self.assertFalse(result["analyze"])
        self.assertFalse(result["test"])

    def test_changed_test_targets_itself(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            test = root / "test/widget/foo_test.dart"
            test.parent.mkdir(parents=True)
            test.write_text("void main() {}\n")

            result = plan(root, ["test/widget/foo_test.dart"])

        self.assertFalse(result["analyze"])
        self.assertTrue(result["test"])
        self.assertEqual(result["targeted_tests"], ["test/widget/foo_test.dart"])
        self.assertEqual(result["test_mode"], "targeted")


if __name__ == "__main__":
    unittest.main()
