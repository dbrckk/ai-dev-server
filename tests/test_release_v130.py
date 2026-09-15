import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_GATES = [
    "CI",
    "Validate AI Dev Server",
    "Fault Injection Gate",
    "Resilience Soak",
    "Mobile Studio Real Build",
    "Multi-Engine E2E Benchmark",
]


class ReleaseV130Tests(unittest.TestCase):
    def test_version_and_manifest_are_final_stable_v130(self):
        self.assertEqual((ROOT / "VERSION").read_text(encoding="utf-8").strip(), "1.3.0")
        manifest = json.loads((ROOT / "control" / "release.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], "1.3.0")
        self.assertEqual(manifest["channel"], "stable")
        self.assertEqual(manifest["branch"], "main")
        self.assertEqual(manifest["required_gates"], EXPECTED_GATES)

    def test_final_release_notes_document_stability_contract(self):
        notes = (ROOT / "docs" / "RELEASE_V1.3.0.md").read_text(encoding="utf-8")
        self.assertIn("v1.3.0", notes)
        self.assertIn("6/6", notes)
        self.assertIn("release/validated-v1.3.0", notes)
        self.assertIn("USER_INPUT_REQUIRED.txt", notes)
        self.assertIn("work-conserving", notes)

    def test_readme_exposes_safe_handoff_and_read_only_status(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("studio.project_status", readme)
        self.assertIn("USER_INPUT_REQUIRED.txt", readme)
        self.assertIn("user-input-required.json", readme)
        self.assertIn("Do not put secret values", readme)


if __name__ == "__main__":
    unittest.main()
