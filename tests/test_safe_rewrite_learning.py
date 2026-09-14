import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import safe_rewrite_learning as srl


class SafeRewriteLearningTests(unittest.TestCase):
    def test_attempt_and_finalize_round_trip(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "learning.json"
            srl.record_attempt(
                path,
                event_id="e1",
                engine="flutter",
                origin_kind="provider",
                origin_name="origin",
                rewrite_kind="provider",
                rewrite_name="rewrite",
                guard_passed=True,
            )
            event = srl.finalize(
                path,
                event_id="e1",
                verification_passed=True,
                review_passed=True,
            )
            self.assertTrue(event["completed"])
            summary = srl.summarize(path)
            self.assertEqual(summary["completed_events"], 1)
            self.assertEqual(summary["origin_rankings"][0]["samples"], 1)
            self.assertEqual(summary["rewrite_rankings"][0]["verification_pass_rate"], 1.0)

    def test_penalty_requires_minimum_samples(self):
        summary = {
            "origin_rankings": [{
                "kind": "provider",
                "name": "bad",
                "samples": srl.MIN_SAMPLES - 1,
                "verification_pass_rate": 0.0,
            }]
        }
        self.assertEqual(
            srl.routing_penalty(summary, kind="provider", name="bad", role="implementation"),
            0.0,
        )

    def test_repeated_poor_origin_gets_bounded_penalty(self):
        summary = {
            "origin_rankings": [{
                "kind": "provider",
                "name": "bad",
                "samples": 10,
                "verification_pass_rate": 0.1,
            }]
        }
        penalty = srl.routing_penalty(
            summary,
            kind="provider",
            name="bad",
            role="implementation",
        )
        self.assertGreater(penalty, 0.0)
        self.assertLessEqual(penalty, srl.MAX_PENALTY)

    def test_non_implementation_roles_are_not_penalized(self):
        summary = {
            "origin_rankings": [{
                "kind": "provider",
                "name": "bad",
                "samples": 10,
                "verification_pass_rate": 0.0,
            }]
        }
        self.assertEqual(
            srl.routing_penalty(summary, kind="provider", name="bad", role="review"),
            0.0,
        )


if __name__ == "__main__":
    unittest.main()
