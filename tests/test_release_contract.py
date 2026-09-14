import json
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import release_contract


class ReleaseContractTests(unittest.TestCase):
    def _root(self, td, version="1.2.0", gates=None):
        root = Path(td)
        (root / "control").mkdir(parents=True)
        (root / ".github/workflows").mkdir(parents=True)
        (root / "VERSION").write_text(version + "\n", encoding="utf-8")
        gates = gates or list(release_contract.WORKFLOW_NAMES)
        manifest = {
            "schema": 1,
            "version": version,
            "channel": "stable-candidate",
            "required_gates": gates,
            "operational_commands": ["python studio/v1_gate.py"],
            "safety": {"supervisor_default": "dry-run"},
        }
        (root / "control/release.json").write_text(
            json.dumps(manifest),
            encoding="utf-8",
        )
        for rel in release_contract.WORKFLOW_NAMES.values():
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("name: test\n", encoding="utf-8")
        return root

    def test_valid_release_contract_passes(self):
        with tempfile.TemporaryDirectory() as td:
            root = self._root(td)
            report = release_contract.validate(root)
            self.assertTrue(report["valid"])
            self.assertEqual(report["failures"], [])

    def test_version_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = self._root(td)
            path = root / "control/release.json"
            manifest = json.loads(path.read_text(encoding="utf-8"))
            manifest["version"] = "1.1.0"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            report = release_contract.validate(root)
            self.assertFalse(report["valid"])
            self.assertIn("version_mismatch", report["failures"])

    def test_missing_required_workflow_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = self._root(td)
            missing = root / release_contract.WORKFLOW_NAMES["CI"]
            missing.unlink()
            report = release_contract.validate(root)
            self.assertFalse(report["valid"])
            self.assertIn("workflow_missing:CI", report["failures"])

    def test_missing_gate_from_manifest_fails(self):
        with tempfile.TemporaryDirectory() as td:
            gates = [
                gate for gate in release_contract.WORKFLOW_NAMES
                if gate != "Resilience Soak"
            ]
            root = self._root(td, gates=gates)
            report = release_contract.validate(root)
            self.assertFalse(report["valid"])
            self.assertTrue(
                any(item.startswith("required_gates_missing:") for item in report["failures"])
            )


if __name__ == "__main__":
    unittest.main()
