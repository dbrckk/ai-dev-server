import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from project_budget import (
    branch_efficiency,
    branch_should_stop,
    budget_status,
    can_spend,
    configure,
    record_calls,
    record_repair_outcome,
)


class ProjectBudgetTests(unittest.TestCase):
    def test_default_budget_is_derived_from_existing_limits(self):
        state = {}
        budget = configure(state, {"max_calls": 12, "max_cycles": 5})
        self.assertEqual(budget["model_call_limit"], 72)
        self.assertEqual(budget["repair_call_limit"], 12)
        self.assertEqual(budget_status(state)["model_calls_remaining"], 72)

    def test_repair_budget_is_independently_enforced(self):
        state = {}
        configure(
            state,
            {
                "max_calls": 12,
                "max_cycles": 5,
                "max_project_model_calls": 20,
                "max_project_repair_calls": 2,
            },
        )
        record_calls(state, 2, repair=True)
        self.assertFalse(can_spend(state, 1, repair=True))
        self.assertTrue(can_spend(state, 1, repair=False))

    def test_repair_outcome_tracks_gain_and_cost(self):
        state = {}
        configure(state, {"max_calls": 12, "max_cycles": 5})
        record_repair_outcome(
            state,
            success=True,
            calls=2,
            blockers_before=3,
            blockers_after=1,
        )
        status = budget_status(state)
        self.assertEqual(status["model_calls_spent"], 2)
        self.assertEqual(status["repair_calls_spent"], 2)
        self.assertEqual(status["diagnostic_gain"], 2.0)
        self.assertEqual(status["successful_repairs"], 1)

    def test_low_yield_branch_is_stopped_after_enough_calls(self):
        task = {
            "model_calls_spent": 4,
            "improvement_count": 0,
        }
        self.assertEqual(branch_efficiency(task), 0.0)
        self.assertTrue(branch_should_stop(task))

    def test_small_branch_is_not_stopped_too_early(self):
        task = {
            "model_calls_spent": 2,
            "improvement_count": 0,
        }
        self.assertFalse(branch_should_stop(task))


if __name__ == "__main__":
    unittest.main()
