import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from adaptive_role_allocator import choose_role_allocation


class AdaptiveRoleAllocatorTests(unittest.TestCase):
    def test_simple_confident_task_uses_one_model_without_extra_roles(self):
        result = choose_role_allocation(
            difficulty=0.2, route_confidence=0.9, remaining_seconds=1000,
            verification_seconds=30, free_capacity=1.0,
        )
        self.assertEqual(result.implementation_models, 1)
        self.assertFalse(result.require_planning)
        self.assertFalse(result.require_review)

    def test_difficult_uncertain_task_adds_independent_implementation(self):
        result = choose_role_allocation(
            difficulty=0.7, route_confidence=0.5, remaining_seconds=1000,
            verification_seconds=60, free_capacity=0.8,
        )
        self.assertEqual(result.implementation_models, 2)
        self.assertTrue(result.require_planning)
        self.assertTrue(result.require_review)

    def test_extreme_task_can_use_three_models(self):
        result = choose_role_allocation(
            difficulty=0.9, route_confidence=0.2, remaining_seconds=1500,
            verification_seconds=60, free_capacity=1.0,
        )
        self.assertEqual(result.implementation_models, 3)
        self.assertTrue(result.require_review)

    def test_budget_pressure_prevents_wide_orchestration(self):
        result = choose_role_allocation(
            difficulty=1.0, route_confidence=0.0, remaining_seconds=20,
            verification_seconds=120, free_capacity=1.0,
        )
        self.assertEqual(result.implementation_models, 1)
        self.assertFalse(result.require_planning)
        self.assertFalse(result.require_review)

    def test_paid_or_scarce_capacity_does_not_expand_models(self):
        result = choose_role_allocation(
            difficulty=0.9, route_confidence=0.1, remaining_seconds=1500,
            verification_seconds=30, free_capacity=0.1,
        )
        self.assertEqual(result.implementation_models, 1)
        self.assertTrue(result.require_review)


if __name__ == "__main__":
    unittest.main()
