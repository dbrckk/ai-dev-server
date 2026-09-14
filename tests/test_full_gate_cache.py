import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from full_gate_cache import validation_key


class FullGateCacheTests(unittest.TestCase):
    def _root(self, td):
        root = Path(td)
        (root / "lib").mkdir()
        (root / "lib/app.dart").write_text("void main() {}\n")
        (root / "pubspec.yaml").write_text("name: demo_app\n")
        (root / "android/app/src/main").mkdir(parents=True)
        (root / "android/app/src/main/AndroidManifest.xml").write_text("<manifest/>\n")
        return root

    def test_identical_inputs_produce_identical_key(self):
        with tempfile.TemporaryDirectory() as td:
            root = self._root(td)
            journeys = [{
                "id": "launch",
                "title": "Launch",
                "steps": ["Open"],
                "expected": ["Visible"],
            }]
            first = validation_key(root, app_name="demo_app", journeys=journeys)
            second = validation_key(root, app_name="demo_app", journeys=journeys)
        self.assertEqual(first, second)

    def test_journey_change_invalidates_key(self):
        with tempfile.TemporaryDirectory() as td:
            root = self._root(td)
            first = validation_key(
                root,
                app_name="demo_app",
                journeys=[{
                    "id": "launch",
                    "title": "Launch",
                    "steps": ["Open"],
                    "expected": ["Visible"],
                }],
            )
            second = validation_key(
                root,
                app_name="demo_app",
                journeys=[{
                    "id": "launch",
                    "title": "Launch",
                    "steps": ["Open"],
                    "expected": ["Different"],
                }],
            )
        self.assertNotEqual(first, second)

    def test_native_change_invalidates_key(self):
        with tempfile.TemporaryDirectory() as td:
            root = self._root(td)
            journeys = [{
                "id": "launch",
                "title": "Launch",
                "steps": ["Open"],
                "expected": ["Visible"],
            }]
            first = validation_key(root, app_name="demo_app", journeys=journeys)
            (root / "android/app/src/main/AndroidManifest.xml").write_text("<manifest changed='1'/>\n")
            second = validation_key(root, app_name="demo_app", journeys=journeys)
        self.assertNotEqual(first, second)

    def test_editable_source_change_invalidates_key(self):
        with tempfile.TemporaryDirectory() as td:
            root = self._root(td)
            journeys = [{
                "id": "launch",
                "title": "Launch",
                "steps": ["Open"],
                "expected": ["Visible"],
            }]
            first = validation_key(root, app_name="demo_app", journeys=journeys)
            (root / "lib/app.dart").write_text("void main() { print('x'); }\n")
            second = validation_key(root, app_name="demo_app", journeys=journeys)
        self.assertNotEqual(first, second)


if __name__ == "__main__":
    unittest.main()
