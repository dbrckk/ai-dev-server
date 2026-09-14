import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from repair_planner import plan, preview_plan


class RepairPlannerTests(unittest.TestCase):
    def test_human_action_has_priority_over_code(self):
        result = plan(
            "billing_qa",
            {
                "human_or_external": ["play_billing_sandbox_purchase_not_verified"],
                "environment": [],
                "prerequisite": [],
                "code": ["billing_integration_not_detected"],
                "unknown": [],
            },
        )
        self.assertEqual(result["action"], "human_action")
        self.assertFalse(result["automatic"])

    def test_environment_prevents_blind_code_repair(self):
        result = plan(
            "performance_qa",
            {
                "human_or_external": [],
                "environment": ["adb_unavailable"],
                "prerequisite": [],
                "code": ["excessive_jank"],
                "unknown": [],
            },
        )
        self.assertEqual(result["action"], "retry_environment")
        self.assertTrue(result["automatic"])

    def test_preview_failure_becomes_code_repair_task(self):
        result = preview_plan("code_review", ["Missing persistence"])
        self.assertEqual(result["action"], "repair_code")
        self.assertEqual(result["blockers"], ["Missing persistence"])

    def test_empty_diagnostics_are_complete(self):
        result = preview_plan("preview", [])
        self.assertEqual(result["action"], "complete")
        self.assertFalse(result["automatic"])


if __name__ == "__main__":
    unittest.main()
