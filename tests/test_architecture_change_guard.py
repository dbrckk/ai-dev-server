import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import architecture_change_guard as guard


class ArchitectureChangeGuardTests(unittest.TestCase):
    def test_source_only_patch_is_allowed_on_hold(self):
        result = guard.enforce(
            {"files": [{"path": "lib/feature.dart", "content": "void main() {}"}]},
            engine="flutter",
            architecture_changes_allowed=False,
        )
        self.assertFalse(result["architecture_sensitive"])

    def test_flutter_dependency_manifest_is_blocked_on_hold(self):
        with self.assertRaises(guard.ArchitectureChangeBlocked):
            guard.enforce(
                {"files": [{"path": "pubspec.yaml", "content": "name: demo"}]},
                engine="flutter",
                architecture_changes_allowed=False,
            )

    def test_generic_infrastructure_file_is_blocked_on_hold(self):
        with self.assertRaises(guard.ArchitectureChangeBlocked):
            guard.enforce(
                {"files": [{"path": ".github/workflows/ci.yml", "content": "name: ci"}]},
                engine="generic",
                architecture_changes_allowed=False,
            )

    def test_godot_project_file_is_blocked_on_hold(self):
        with self.assertRaises(guard.ArchitectureChangeBlocked):
            guard.enforce(
                {"files": [{"path": "project.godot", "content": "[application]"}]},
                engine="godot",
                architecture_changes_allowed=False,
            )

    def test_architecture_patch_is_allowed_after_preflight_pass(self):
        result = guard.enforce(
            {"files": [{"path": "pyproject.toml", "content": "[project]\nname='demo'"}]},
            engine="generic",
            architecture_changes_allowed=True,
        )
        self.assertTrue(result["architecture_sensitive"])
        self.assertEqual(result["sensitive_paths"], ["pyproject.toml"])


if __name__ == "__main__":
    unittest.main()
