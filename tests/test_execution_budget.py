import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from execution_budget import choose_budget


class ExecutionBudgetTests(unittest.TestCase):
    def test_normal_budget_allows_two_passes_and_two_agents(self):
        budget = choose_budget(
            remaining_seconds=1800,
            previous_verification={"passed": False},
            bootstrap_passed=True,
            meta_agent_limit=2,
        )
        self.assertEqual(budget.mode, "normal")
        self.assertEqual(budget.max_work_passes, 2)
        self.assertEqual(budget.agent_limit, 2)

    def test_deadline_guard_collapses_exploration(self):
        budget = choose_budget(
            remaining_seconds=120,
            previous_verification={"passed": False},
            bootstrap_passed=True,
            meta_agent_limit=2,
        )
        self.assertEqual(budget.mode, "deadline_guard")
        self.assertEqual(budget.max_work_passes, 1)
        self.assertEqual(budget.agent_limit, 1)

    def test_recent_success_reduces_new_work(self):
        budget = choose_budget(
            remaining_seconds=1800,
            previous_verification={"passed": True},
            bootstrap_passed=True,
            meta_agent_limit=2,
        )
        self.assertEqual(budget.mode, "verification_close")
        self.assertEqual(budget.max_work_passes, 1)
        self.assertEqual(budget.agent_limit, 1)

    def test_predictive_inputs_bound_normal_budget(self):
        budget = choose_budget(
            remaining_seconds=1800,
            previous_verification={"passed": False},
            bootstrap_passed=True,
            meta_agent_limit=2,
            predicted_work_passes=1,
            predicted_agent_limit=1,
            predicted_reserve_seconds=240,
        )
        self.assertEqual(budget.mode, "normal")
        self.assertEqual(budget.max_work_passes, 1)
        self.assertEqual(budget.agent_limit, 1)
        self.assertEqual(budget.reserve_seconds, 240)

    def test_bootstrap_failure_prioritizes_recovery(self):
        budget = choose_budget(
            remaining_seconds=1800,
            previous_verification=None,
            bootstrap_passed=False,
            meta_agent_limit=2,
        )
        self.assertEqual(budget.mode, "bootstrap_recovery")
        self.assertEqual(budget.max_work_passes, 1)
        self.assertEqual(budget.agent_limit, 1)


if __name__ == "__main__":
    unittest.main()
