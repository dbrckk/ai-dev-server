from pathlib import Path
import tempfile
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from recovery_learning import adapt, load, record


class RecoveryLearningTests(unittest.TestCase):
    def test_records_success_rate_by_toolchain_category_and_action(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "recovery.json"
            for success in (False, True, False):
                row = record(
                    path,
                    toolchain={"stacks": ["python"]},
                    category="test_failure",
                    action="repair_behavior",
                    success=success,
                    duration_seconds=10,
                )
            self.assertEqual(row["attempts"], 3)
            self.assertEqual(row["successes"], 1)
            self.assertAlmostEqual(row["success_rate"], 1 / 3, places=3)

    def test_low_success_rate_escalates_provider_switch(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "recovery.json"
            for _ in range(3):
                record(
                    path,
                    toolchain={"stacks": ["node"]},
                    category="compile_failure",
                    action="repair_compile",
                    success=False,
                    duration_seconds=5,
                )
            result = adapt(
                {"action": "repair_compile", "priority": "high", "provider_switch": False},
                load(path),
                toolchain={"stacks": ["node"]},
                category="compile_failure",
            )
            self.assertTrue(result["provider_switch"])
            self.assertEqual(result["priority"], "critical")
            self.assertTrue(result["learning"]["escalated"])

    def test_five_zero_successes_override_strategy(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "recovery.json"
            for _ in range(5):
                record(
                    path,
                    toolchain={"stacks": ["python"]},
                    category="test_failure",
                    action="repair_behavior",
                    success=False,
                    duration_seconds=3,
                )
            result = adapt(
                {"action": "repair_behavior", "priority": "high", "provider_switch": False},
                load(path),
                toolchain={"stacks": ["python"]},
                category="test_failure",
            )
            self.assertEqual(result["action"], "switch_strategy")
            self.assertTrue(result["provider_switch"])

    def test_dependency_repair_is_not_overridden_to_generic_switch(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "recovery.json"
            for _ in range(5):
                record(
                    path,
                    toolchain={"stacks": ["python"]},
                    category="dependency_failure",
                    action="repair_dependencies",
                    success=False,
                    duration_seconds=3,
                )
            result = adapt(
                {"action": "repair_dependencies", "priority": "high", "provider_switch": False},
                load(path),
                toolchain={"stacks": ["python"]},
                category="dependency_failure",
            )
            self.assertEqual(result["action"], "repair_dependencies")
            self.assertTrue(result["provider_switch"])


if __name__ == "__main__":
    unittest.main()
