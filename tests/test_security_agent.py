import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from core import StudioError
from security_agent import attempt, eligible_blockers


class FakeModel:
    def __init__(self, limit):
        self.calls = 0
        self.models_used = {"security_fix": "fake-code"}
        self.providers_used = {"security_fix": "fake-provider"}

    def ask(self, role, context, screenshots=()):
        self.calls += 1
        return {
            "files": [
                {
                    "path": "lib/app.dart",
                    "content": "const endpoint = 'https://example.com';\n",
                }
            ]
        }


class PassingSandbox:
    def __init__(self, root):
        self.root = root

    def gates(self, name, journeys):
        return True, [{"command": ["flutter", "test"], "exit_code": 0, "output": ""}]


class FailingSandbox:
    def __init__(self, root):
        self.root = root

    def gates(self, name, journeys):
        return False, [{"command": ["flutter", "test"], "exit_code": 1, "output": "failed"}]


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


class SecurityAgentTests(unittest.TestCase):
    def test_credentials_disable_external_agentic_repair(self):
        evidence = {
            "blockers": [
                "credential_material_detected",
                "cleartext_network_traffic_detected",
            ]
        }
        self.assertEqual(eligible_blockers(evidence), [])

    def test_successful_patch_passes_trusted_gates(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "lib/app.dart"
            source.parent.mkdir(parents=True)
            source.write_text("const endpoint = 'http://example.com';\n")

            result = attempt(
                root,
                STATE,
                {"blockers": ["cleartext_network_traffic_detected"]},
                "demo_app",
                model_factory=FakeModel,
                sandbox_factory=PassingSandbox,
            )

            self.assertTrue(result["attempted"])
            self.assertTrue(result["changed"])
            self.assertEqual(result["model_calls"], 1)
            self.assertIn("https://example.com", source.read_text())

    def test_failed_trusted_gates_restore_original_source(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "lib/app.dart"
            source.parent.mkdir(parents=True)
            original = "const endpoint = 'http://example.com';\n"
            source.write_text(original)

            with self.assertRaises(StudioError):
                attempt(
                    root,
                    STATE,
                    {"blockers": ["cleartext_network_traffic_detected"]},
                    "demo_app",
                    model_factory=FakeModel,
                    sandbox_factory=FailingSandbox,
                )

            self.assertEqual(source.read_text(), original)


if __name__ == "__main__":
    unittest.main()
