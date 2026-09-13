import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from cost_drift import CostDriftDetector


class CostDriftDetectorTests(unittest.TestCase):
    def test_normal_phase_cost_keeps_execution(self):
        d = CostDriftDetector()
        sample = d.record(phase="planning", expected_seconds=100, observed_seconds=120)
        self.assertEqual(sample["level"], "normal")
        self.assertEqual(d.decision()["action"], "continue")
        self.assertEqual(d.exploration_multiplier(), 1.0)

    def test_elevated_drift_reduces_exploration(self):
        d = CostDriftDetector()
        sample = d.record(phase="implementation", expected_seconds=100, observed_seconds=160)
        self.assertEqual(sample["level"], "elevated")
        self.assertEqual(d.decision()["action"], "reduce_exploration")
        self.assertEqual(d.exploration_multiplier(), 0.5)

    def test_single_severe_drift_requests_replan(self):
        d = CostDriftDetector()
        d.record(phase="fallback", expected_seconds=100, observed_seconds=220)
        self.assertEqual(d.decision()["action"], "replan")
        self.assertEqual(d.exploration_multiplier(), 0.0)

    def test_multiple_severe_drifts_request_stop(self):
        d = CostDriftDetector()
        d.record(phase="implementation", expected_seconds=100, observed_seconds=210)
        d.record(phase="verification", expected_seconds=100, observed_seconds=250)
        self.assertEqual(d.decision()["action"], "stop")

    def test_historical_baseline_overrides_fixed_ratio_threshold(self):
        d = CostDriftDetector()
        baseline = {"samples": 10, "ema_seconds": 100.0, "ema_abs_deviation": 5.0}
        sample = d.record(
            phase="verification",
            expected_seconds=200,
            observed_seconds=120,
            baseline=baseline,
        )
        self.assertEqual(sample["source"], "historical")
        self.assertEqual(sample["level"], "severe")
        self.assertGreaterEqual(sample["normalized_deviation"], 4.0)

    def test_historical_normal_range_is_not_flagged(self):
        d = CostDriftDetector()
        baseline = {"samples": 10, "ema_seconds": 100.0, "ema_abs_deviation": 20.0}
        sample = d.record(
            phase="verification",
            expected_seconds=50,
            observed_seconds=120,
            baseline=baseline,
        )
        self.assertEqual(sample["source"], "historical")
        self.assertEqual(sample["level"], "normal")

    def test_snapshot_is_bounded(self):
        d = CostDriftDetector()
        for i in range(30):
            d.record(phase="planning", expected_seconds=100, observed_seconds=100 + i)
        self.assertEqual(len(d.snapshot()["samples"]), 20)


if __name__ == "__main__":
    unittest.main()
