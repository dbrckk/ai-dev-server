import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import capacity_budget as cb


class CapacityBudgetTests(unittest.TestCase):
    def test_unmetered_capacity_expands_budget_most(self):
        plan = cb.expanded_call_limit(
            20,
            {"unmetered_available": True, "providers": []},
            explicit_limit=False,
        )
        self.assertEqual(plan["multiplier"], cb.UNMETERED_MULTIPLIER)
        self.assertEqual(plan["effective_limit"], 80)

    def test_large_pooled_quota_expands_budget(self):
        plan = cb.expanded_call_limit(
            20,
            {
                "unmetered_available": False,
                "providers": [{
                    "mode": "pooled-free",
                    "monthly_quota": {
                        "remaining_ratio": 0.8,
                        "exhausted": False,
                    },
                }],
            },
            explicit_limit=False,
        )
        self.assertEqual(plan["multiplier"], cb.POOLED_HIGH_MULTIPLIER)
        self.assertEqual(plan["effective_limit"], 60)

    def test_low_remaining_pool_does_not_expand_budget(self):
        plan = cb.expanded_call_limit(
            20,
            {
                "providers": [{
                    "mode": "pooled-free",
                    "monthly_quota": {
                        "remaining_ratio": 0.05,
                        "exhausted": False,
                    },
                }],
            },
            explicit_limit=False,
        )
        self.assertEqual(plan["multiplier"], 1.0)
        self.assertEqual(plan["effective_limit"], 20)

        # Keep the existing test function: corrupted/ambiguous provider
        # metadata cannot falsely unlock a larger autonomous call budget.
        for invalid_ratio in (
            float("nan"), float("inf"), float("-inf"),
            "NaN", "Infinity", -0.01, 1.01, True, False, {},
        ):
            with self.subTest(ratio=repr(invalid_ratio)):
                corrupt_plan = cb.expanded_call_limit(
                    20,
                    {"providers": [{
                        "mode": "pooled-free",
                        "monthly_quota": {
                            "remaining_ratio": invalid_ratio,
                            "exhausted": False,
                        },
                    }]},
                    explicit_limit=False,
                )
                self.assertEqual(corrupt_plan["multiplier"], 1.0)
                self.assertEqual(corrupt_plan["effective_limit"], 20)

        # A single malformed provider must not hide a second genuine,
        # finite pool. Valid fractional numeric-string telemetry stays usable.
        mixed_plan = cb.expanded_call_limit(
            20,
            {"providers": [
                {"mode": "pooled-free", "monthly_quota": {"remaining_ratio": "NaN"}},
                {"mode": "pooled-free", "monthly_quota": {"remaining_ratio": "0.2"}},
            ]},
            explicit_limit=False,
        )
        self.assertEqual(mixed_plan["multiplier"], cb.POOLED_MEDIUM_MULTIPLIER)
        self.assertEqual(mixed_plan["effective_limit"], 40)

    def test_explicit_user_limit_is_never_expanded(self):
        plan = cb.expanded_call_limit(
            20,
            {"unmetered_available": True},
            explicit_limit=True,
        )
        self.assertEqual(plan["effective_limit"], 20)
        self.assertEqual(plan["reason"], "explicit_user_limit")

    def test_automatic_limit_is_absolutely_capped(self):
        plan = cb.expanded_call_limit(
            100,
            {"unmetered_available": True},
            explicit_limit=False,
        )
        self.assertEqual(plan["effective_limit"], cb.ABSOLUTE_AUTO_CALL_CAP)


if __name__ == "__main__":
    unittest.main()
