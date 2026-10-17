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

        # Free-budget multipliers must fail closed on unreliable telemetry.
        # No new test functions: extend the existing low-capacity case.
        for invalid in (
            float("nan"), "NaN", float("inf"), float("-inf"),
            "Infinity", -0.01, 1.01, True, False, {}, [], object(),
        ):
            with self.subTest(quota_ratio=repr(invalid)):
                invalid_plan = cb.expanded_call_limit(
                    20,
                    {"providers": [{
                        "mode": "pooled-free",
                        "monthly_quota": {
                            "remaining_ratio": invalid,
                            "exhausted": False,
                        },
                    }]},
                    explicit_limit=False,
                )
                self.assertEqual(invalid_plan["multiplier"], 1.0)
                self.assertEqual(invalid_plan["effective_limit"], 20)

        # Invalid providers must not hide a second genuinely available pool.
        mixed = cb.expanded_call_limit(
            20,
            {"providers": [
                {"mode": "pooled-free", "monthly_quota": {
                    "remaining_ratio": "NaN", "exhausted": False,
                }},
                {"mode": "pooled-free", "monthly_quota": {
                    "remaining_ratio": "0.2", "exhausted": False,
                }},
            ]},
            explicit_limit=False,
        )
        self.assertEqual(mixed["multiplier"], cb.POOLED_MEDIUM_MULTIPLIER)
        self.assertEqual(mixed["effective_limit"], 40)

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
