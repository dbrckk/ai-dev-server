import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from phase_budget import allocate, reallocate_unused, phase_remaining, bounded_timeout


class PhaseBudgetTests(unittest.TestCase):
    def test_allocation_reserves_verification(self):
        quotas = allocate(
            available_seconds=1200,
            verification_reserve_seconds=240,
            difficulty_band="medium",
        )
        self.assertGreaterEqual(quotas.verification, 240)
        self.assertLessEqual(quotas.total, 1200)

    def test_high_difficulty_keeps_more_fallback_capacity(self):
        low = allocate(
            available_seconds=1200,
            verification_reserve_seconds=180,
            difficulty_band="low",
        )
        high = allocate(
            available_seconds=1200,
            verification_reserve_seconds=180,
            difficulty_band="high",
        )
        self.assertGreater(high.fallback, low.fallback)

    def test_unused_planning_is_reallocated_without_changing_total(self):
        quotas = allocate(
            available_seconds=900,
            verification_reserve_seconds=180,
            difficulty_band="medium",
        )
        updated = reallocate_unused(quotas, phase="planning", unused_seconds=30)
        self.assertEqual(updated.total, quotas.total)
        self.assertEqual(updated.planning, quotas.planning - 30)
        self.assertGreater(updated.implementation, quotas.implementation)
        self.assertGreater(updated.verification, quotas.verification)

    def test_phase_remaining_never_goes_negative(self):
        quotas = allocate(
            available_seconds=900,
            verification_reserve_seconds=180,
            difficulty_band="medium",
        )
        self.assertEqual(
            phase_remaining(quotas, phase="implementation", elapsed_seconds=10),
            max(0, quotas.implementation - 10),
        )
        self.assertEqual(
            phase_remaining(quotas, phase="implementation", elapsed_seconds=10_000),
            0,
        )

    def test_bounded_timeout_respects_remaining_quota(self):
        self.assertEqual(bounded_timeout(0, minimum=30, maximum=1200), 0)
        self.assertEqual(bounded_timeout(20, minimum=30, maximum=1200), 30)
        self.assertEqual(bounded_timeout(3000, minimum=30, maximum=1200), 1200)
        self.assertEqual(bounded_timeout(180, minimum=30, maximum=1200), 180)

    def test_unknown_phase_is_rejected(self):
        quotas = allocate(
            available_seconds=900,
            verification_reserve_seconds=180,
            difficulty_band="medium",
        )
        with self.assertRaisesRegex(ValueError, "unknown phase"):
            reallocate_unused(quotas, phase="other", unused_seconds=10)


if __name__ == "__main__":
    unittest.main()
