import json
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from capacity_runtime import project_envelope


class CapacityRuntimeTests(unittest.TestCase):
    def test_reads_project_envelope(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "plan.json"
            path.write_text(json.dumps({
                "projects": [
                    {"id": "a", "token_envelope": 1234},
                    {"id": "b", "token_envelope": 999},
                ]
            }), encoding="utf-8")
            self.assertEqual(project_envelope(path, "a"), 1234)

    def test_missing_or_invalid_plan_returns_none(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "missing.json"
            self.assertIsNone(project_envelope(path, "a"))
            path.write_text("not-json", encoding="utf-8")
            self.assertIsNone(project_envelope(path, "a"))


    def test_reads_full_project_state_for_recovery(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "plan.json"
            path.write_text(json.dumps({
                "projects": [
                    {
                        "id": "a",
                        "token_envelope": 1500,
                        "recovery_active": True,
                        "recovery_reason": "material_context_change",
                    }
                ]
            }), encoding="utf-8")
            from capacity_runtime import project_state
            row = project_state(path, "a")
            self.assertTrue(row["recovery_active"])
            self.assertEqual(row["token_envelope"], 1500)



if __name__ == "__main__":
    unittest.main()
