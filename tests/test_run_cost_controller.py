import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from run_cost_controller import RunCostController


class RunCostControllerTests(unittest.TestCase):
    def test_model_call_budget_forces_verification(self):
        c = RunCostController(total_budget_seconds=1000, max_model_calls=2)
        c.record_model(10, phase="planning")
        self.assertEqual(c.decision()["action"], "continue")
        c.record_model(10, phase="implementation")
        self.assertEqual(c.decision()["action"], "verify")
        self.assertIn("model-call", c.decision()["reason"])

    def test_excessive_agent_time_forces_verification(self):
        c = RunCostController(total_budget_seconds=1000, max_model_calls=20)
        c.record_agent(400)
        self.assertEqual(c.decision()["action"], "verify")
        self.assertIn("agent-time", c.decision()["reason"])

    def test_too_many_fallbacks_force_verification(self):
        c = RunCostController(total_budget_seconds=2000, max_model_calls=20)
        for _ in range(4):
            c.record_agent(10, fallback=True)
        self.assertEqual(c.decision()["action"], "verify")
        self.assertIn("fallback", c.decision()["reason"])

    def test_near_total_budget_requests_stop(self):
        c = RunCostController(total_budget_seconds=1000, max_model_calls=20)
        c.model_seconds = 300
        c.agent_seconds = 250
        c.verification_seconds = 250
        c.review_seconds = 120
        self.assertEqual(c.decision()["action"], "stop")

    def test_snapshot_exposes_cumulative_costs(self):
        c = RunCostController(total_budget_seconds=1000, max_model_calls=10)
        c.record_model(12.5, phase="planning")
        c.record_verification(20)
        snap = c.snapshot()
        self.assertEqual(snap["model_calls"], 1)
        self.assertEqual(snap["verification_runs"], 1)
        self.assertEqual(snap["model_seconds"], 12.5)


if __name__ == "__main__":
    unittest.main()
