import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from routing_calibration import build, adjustment


class RoutingCalibrationTests(unittest.TestCase):
    def test_verified_high_quality_route_gets_positive_adjustment(self):
        audit = {"events": [{"winner": "p", "winner_model": "m"} for _ in range(12)]}
        outcomes = [{"outcome": {"quality_score": 100, "successful": True}} for _ in range(12)]
        report = build(audit, outcomes)
        self.assertGreater(adjustment(report, "p", "m"), 0)
        self.assertLessEqual(adjustment(report, "p", "m"), 10)

    def test_bad_verified_outcomes_reduce_route_score(self):
        audit = {"events": [{"winner": "p", "winner_model": "m"} for _ in range(12)]}
        outcomes = [{"outcome": {"quality_score": 0, "successful": False}} for _ in range(12)]
        report = build(audit, outcomes)
        self.assertLess(adjustment(report, "p", "m"), 0)

    def test_sparse_evidence_stays_near_neutral(self):
        report = build(
            {"events": [{"winner": "p", "winner_model": "m"}]},
            [{"outcome": {"quality_score": 0, "successful": False}}],
        )
        self.assertGreater(adjustment(report, "p", "m"), -1.0)

    def test_unknown_route_is_neutral(self):
        self.assertEqual(adjustment({"routes": {}}, "x", "y"), 0.0)


if __name__ == "__main__":
    unittest.main()
