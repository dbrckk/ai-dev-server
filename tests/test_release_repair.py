import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from core import StudioError
from release_repair import attempt


STATE = {
    "product": {
        "journeys": [
            {
                "id": "launch",
                "title": "Launch",
                "steps": ["Open the application"],
                "expected": ["Main screen is visible"],
            }
        ]
    }
}


class NeverModel:
    def __init__(self, limit):
        raise AssertionError("model must not be constructed")


class ReleaseRepairTests(unittest.TestCase):
    def test_credentials_abort_before_model_call(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "lib/app.dart"
            source.parent.mkdir(parents=True)
            source.write_text("const token = 'sk-abcdefghijklmnopqrstuvwxyz123456';\n")

            with self.assertRaises(StudioError):
                attempt(
                    root,
                    STATE,
                    {"passed": False, "blockers": ["excessive_jank"]},
                    "performance_qa",
                    "demo_app",
                    model_factory=NeverModel,
                )


if __name__ == "__main__":
    unittest.main()
