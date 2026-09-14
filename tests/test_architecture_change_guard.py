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


    def test_semantic_router_change_is_blocked_on_hold(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target = root / "lib/router.dart"
            target.parent.mkdir(parents=True)
            target.write_text("void route() {}\n", encoding="utf-8")
            with self.assertRaises(guard.ArchitectureChangeBlocked):
                guard.enforce(
                    {"files": [{
                        "path": "lib/router.dart",
                        "content": "import 'package:go_router/go_router.dart';\nclass AppRouter {}\n",
                    }]},
                    engine="flutter",
                    architecture_changes_allowed=False,
                    root=root,
                )

    def test_semantic_import_churn_is_reported_when_allowed(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target = root / "src/main.py"
            target.parent.mkdir(parents=True)
            target.write_text("import os\n\ndef main():\n    pass\n", encoding="utf-8")
            result = guard.enforce(
                {"files": [{
                    "path": "src/main.py",
                    "content": "import fastapi\nimport sqlalchemy\nfrom dependency_injector import containers\nclass ServiceContainer: pass\n",
                }]},
                engine="generic",
                architecture_changes_allowed=True,
                root=root,
            )
        self.assertTrue(result["architecture_semantic"])
        self.assertIn("src/main.py", result["semantic_paths"])
        self.assertGreaterEqual(result["semantic_details"][0]["impact_score"], 4)

    def test_small_source_edit_does_not_trigger_semantic_guard(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target = root / "src/util.py"
            target.parent.mkdir(parents=True)
            target.write_text("def add(a, b):\n    return a+b\n", encoding="utf-8")
            result = guard.enforce(
                {"files": [{
                    "path": "src/util.py",
                    "content": "def add(a, b):\n    return a + b\n",
                }]},
                engine="generic",
                architecture_changes_allowed=False,
                root=root,
            )
        self.assertFalse(result["architecture_semantic"])


if __name__ == "__main__":
    unittest.main()
