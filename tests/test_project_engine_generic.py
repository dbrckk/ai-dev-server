from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
STUDIO=ROOT/"studio"
if str(STUDIO) not in sys.path:
    sys.path.insert(0,str(STUDIO))

from project_engine import EngineError, infer


class GenericEngineTests(unittest.TestCase):
    def test_node_project_is_generic(self):
        self.assertEqual(infer(["package.json","src/index.ts"]).name,"generic")

    def test_python_project_is_generic(self):
        self.assertEqual(infer(["pyproject.toml","src/app.py"]).name,"generic")

    def test_flutter_stays_specialized(self):
        self.assertEqual(infer(["pubspec.yaml","lib/main.dart"]).name,"flutter")

    def test_godot_stays_specialized(self):
        self.assertEqual(infer(["project.godot","scripts/main.gd"]).name,"godot")

    def test_ambiguous_specialized_markers_fail(self):
        with self.assertRaises(EngineError):
            infer(["pubspec.yaml","project.godot"])


if __name__=="__main__":
    unittest.main()
