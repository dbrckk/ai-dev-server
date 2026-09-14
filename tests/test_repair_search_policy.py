import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from repair_search_policy import expected_value, should_expand, should_refine


class RepairSearchPolicyTests(unittest.TestCase):
    def test_does_not_expand_when_budget_is_insufficient(self):
        row = {
            "conservative_success_rate": 0.9,
            "risk": 0.1,
            "estimated_seconds": 10,
            "estimated_model_calls": 2,
        }
        self.assertFalse(
            should_expand(
                current_winner=None,
                candidate_row=row,
                remaining_model_calls=1,
            )
        )

    def test_expands_promising_branch_without_verified_winner(self):
        row = {
            "conservative_success_rate": 0.8,
            "risk": 0.2,
            "estimated_seconds": 20,
            "estimated_model_calls": 1,
        }
        self.assertGreater(expected_value(row), 8.0)
        self.assertTrue(
            should_expand(
                current_winner=None,
                candidate_row=row,
                remaining_model_calls=2,
            )
        )

    def test_strong_verified_winner_stops_further_expansion(self):
        row = {
            "conservative_success_rate": 0.95,
            "risk": 0.1,
            "estimated_seconds": 10,
            "estimated_model_calls": 1,
        }
        self.assertFalse(
            should_expand(
                current_winner={"candidate_score": 1025.0},
                candidate_row=row,
                remaining_model_calls=4,
            )
        )

    def test_refinement_requires_value_and_budget(self):
        row = {
            "conservative_success_rate": 0.8,
            "risk": 0.2,
            "estimated_seconds": 20,
            "estimated_model_calls": 1,
        }
        self.assertTrue(
            should_refine(
                failure_present=True,
                refinement_model_calls=1,
                remaining_model_calls=1,
                strategy_row=row,
            )
        )
        self.assertFalse(
            should_refine(
                failure_present=True,
                refinement_model_calls=1,
                remaining_model_calls=0,
                strategy_row=row,
            )
        )


if __name__ == "__main__":
    unittest.main()
