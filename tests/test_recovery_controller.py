import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from recovery_controller import evaluate


class RecoveryControllerTests(unittest.TestCase):
    def test_first_pause_registers_context_without_immediate_retry(self):
        with tempfile.TemporaryDirectory() as td:
            result = evaluate(
                Path(td) / "recovery.json",
                project_id="a",
                paused=True,
                context={"sha": "1", "providers": ["p"]},
            )
            self.assertFalse(result["recover"])
            self.assertEqual(result["reason"], "pause_context_registered")

    def test_material_context_change_grants_single_bounded_recovery(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "recovery.json"
            evaluate(path, project_id="a", paused=True, context={"sha": "1"})
            first = evaluate(path, project_id="a", paused=True, context={"sha": "2"})
            repeated = evaluate(path, project_id="a", paused=True, context={"sha": "2"})
            self.assertTrue(first["recover"])
            self.assertEqual(first["capacity_multiplier"], 0.15)
            self.assertTrue(first["force_diversify"])
            self.assertFalse(repeated["recover"])

    def test_successful_unpause_resets_recovery_memory(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "recovery.json"
            evaluate(path, project_id="a", paused=True, context={"sha": "1"})
            evaluate(path, project_id="a", paused=True, context={"sha": "2"})
            reset = evaluate(path, project_id="a", paused=False, context={"sha": "2"})
            self.assertFalse(reset["recover"])
            again = evaluate(path, project_id="a", paused=True, context={"sha": "3"})
            self.assertFalse(again["recover"])
            self.assertEqual(again["reason"], "pause_context_registered")


if __name__ == "__main__":
    unittest.main()
