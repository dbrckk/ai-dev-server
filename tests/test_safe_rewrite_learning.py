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


    def test_origin_score_penalty_and_rewrite_bonus_are_asymmetric(self):
        summary = {
            "origin_rankings": [{
                "kind": "provider",
                "name": "mixed",
                "samples": 10,
                "verification_pass_rate": 0.1,
            }],
            "rewrite_rankings": [{
                "kind": "provider",
                "name": "mixed",
                "samples": 10,
                "verification_pass_rate": 0.9,
                "review_pass_rate": 0.9,
                "review_passes": 9,
            }],
        }
        penalty = srl.origin_violation_penalty(
            summary, kind="provider", name="mixed", role="implementation"
        )
        bonus = srl.rewrite_recovery_bonus(
            summary, kind="provider", name="mixed", role="implementation"
        )
        self.assertGreater(penalty, bonus)
        self.assertLessEqual(bonus, 10.0)

    def test_recovery_bonus_requires_evidence(self):
        summary = {
            "rewrite_rankings": [{
                "kind": "provider",
                "name": "good",
                "samples": srl.MIN_SAMPLES - 1,
                "verification_pass_rate": 1.0,
                "review_pass_rate": 1.0,
                "review_passes": srl.MIN_SAMPLES - 1,
            }]
        }
        self.assertEqual(
            srl.rewrite_recovery_bonus(
                summary, kind="provider", name="good", role="implementation"
            ),
            0.0,
        )


    def test_recent_events_have_more_weight_than_old_events(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "learning.json"
            for i in range(30):
                srl.record_attempt(
                    path,
                    event_id=f"e{i}",
                    engine="generic",
                    origin_kind="provider",
                    origin_name="p",
                    rewrite_kind="provider",
                    rewrite_name="r",
                    guard_passed=True,
                )
                srl.finalize(
                    path,
                    event_id=f"e{i}",
                    verification_passed=(i >= 25),
                    review_passed=(i >= 25),
                )
            row = srl.summarize(path)["origin_rankings"][0]
            self.assertGreater(
                row["decayed_verification_pass_rate"],
                row["verification_pass_rate"],
            )

    def test_recent_success_streak_marks_rehabilitation(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "learning.json"
            outcomes = [False, False, False, False, False, True, True, True]
            for i, outcome in enumerate(outcomes):
                srl.record_attempt(
                    path,
                    event_id=f"e{i}",
                    engine="generic",
                    origin_kind="agent",
                    origin_name="agent-a",
                    rewrite_kind="provider",
                    rewrite_name="r",
                    guard_passed=True,
                )
                srl.finalize(
                    path,
                    event_id=f"e{i}",
                    verification_passed=outcome,
                    review_passed=outcome,
                )
            row = srl.summarize(path)["origin_rankings"][0]
            self.assertTrue(row["rehabilitating"])
            self.assertEqual(row["recent_verification_streak"], 3)

    def test_old_failures_decay_toward_exploration_floor(self):
        events = []
        for i in range(40):
            events.append({
                "event_id": f"x{i}",
                "engine": "generic",
                "origin_kind": "provider" if i < 5 else "other",
                "origin_name": "bad" if i < 5 else "other",
                "rewrite_kind": "provider",
                "rewrite_name": "r",
                "guard_passed": True,
                "verification_passed": False if i < 5 else True,
                "review_passed": False if i < 5 else True,
                "completed": True,
            })
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "learning.json"
            path.write_text(__import__("json").dumps({"schema":1,"events":events}))
            summary = srl.summarize(path)
            penalty = srl.routing_penalty(summary, kind="provider", name="bad", role="implementation")
            self.assertLess(penalty, srl.MAX_PENALTY)


    def test_stale_actor_receives_bounded_exploration_bonus(self):
        summary = {
            "origin_rankings": [{
                "kind": "provider",
                "name": "stale",
                "samples": 10,
                "verification_pass_rate": 0.0,
                "eligible_for_routing_bias": True,
                "events_since_last_observation": srl.EXPLORATION_STALE_EVENTS + 15,
            }]
        }
        bonus = srl.exploration_bonus(
            summary,
            kind="provider",
            name="stale",
            role="implementation",
        )
        self.assertGreater(bonus, 0.0)
        self.assertLessEqual(bonus, srl.MAX_EXPLORATION_BONUS)

    def test_recent_actor_has_no_exploration_bonus(self):
        summary = {
            "origin_rankings": [{
                "kind": "agent",
                "name": "recent",
                "samples": 10,
                "verification_pass_rate": 0.0,
                "eligible_for_routing_bias": True,
                "events_since_last_observation": 2,
            }]
        }
        self.assertEqual(
            srl.exploration_bonus(
                summary,
                kind="agent",
                name="recent",
                role="implementation",
            ),
            0.0,
        )


if __name__ == "__main__":
    unittest.main()
