import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import contextual_routing_memory as crm


class ContextualRoutingMemoryTests(unittest.TestCase):
    def test_contextual_adjustment_requires_evidence(self):
        data = {"backend": {"provider:p": {"samples": 2, "successes": 2, "ema_success_rate": 1.0}}}
        self.assertEqual(
            crm.contextual_adjustment(
                data,
                weighted_contexts=[("backend", 1.0)],
                kind="provider",
                name="p",
            ),
            0.0,
        )

    def test_positive_context_history_adds_bonus(self):
        data = {"backend": {"provider:p": {"samples": 8, "successes": 7, "ema_success_rate": 0.9}}}
        bonus = crm.contextual_adjustment(
            data,
            weighted_contexts=[("backend", 1.0)],
            kind="provider",
            name="p",
        )
        self.assertGreater(bonus, 0.0)
        self.assertLessEqual(bonus, crm.MAX_CONTEXT_BONUS)

    def test_negative_context_history_applies_larger_bounded_penalty(self):
        data = {"stack:rust": {"agent:a": {"samples": 8, "successes": 1, "ema_success_rate": 0.1}}}
        penalty = crm.contextual_adjustment(
            data,
            weighted_contexts=[("stack:rust", 1.0)],
            kind="agent",
            name="a",
        )
        self.assertLess(penalty, 0.0)
        self.assertGreaterEqual(penalty, -crm.MAX_CONTEXT_PENALTY)

    def test_record_uses_ema(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "memory.json"
            for outcome in [False, False, True, True, True]:
                crm.record(
                    path,
                    context="bugfix",
                    kind="provider",
                    name="p",
                    success=outcome,
                )
            row = crm.load(path)["bugfix"]["provider:p"]
            self.assertEqual(row["samples"], 5)
            self.assertGreater(row["ema_success_rate"], 0.5)


    def test_bandit_bonus_is_higher_with_less_evidence(self):
        sparse = {
            "backend": {
                "provider:p": {
                    "samples": 1,
                    "successes": 1,
                    "ema_success_rate": 0.8,
                }
            }
        }
        dense = {
            "backend": {
                "provider:p": {
                    "samples": 20,
                    "successes": 16,
                    "ema_success_rate": 0.8,
                }
            }
        }
        sparse_score = crm.contextual_bandit_score(
            sparse,
            weighted_contexts=[("backend", 1.0)],
            kind="provider",
            name="p",
        )
        dense_score = crm.contextual_bandit_score(
            dense,
            weighted_contexts=[("backend", 1.0)],
            kind="provider",
            name="p",
        )
        self.assertGreater(
            sparse_score["exploration_bonus"],
            dense_score["exploration_bonus"],
        )

    def test_architecture_hold_reduces_exploration(self):
        data = {
            "backend": {
                "agent:a": {
                    "samples": 1,
                    "successes": 1,
                    "ema_success_rate": 0.8,
                }
            },
            "architecture-risk:hold": {
                "agent:a": {
                    "samples": 1,
                    "successes": 1,
                    "ema_success_rate": 0.8,
                }
            },
        }
        normal = crm.contextual_bandit_score(
            data,
            weighted_contexts=[("backend", 1.0)],
            kind="agent",
            name="a",
        )
        risky = crm.contextual_bandit_score(
            data,
            weighted_contexts=[("backend", 0.7), ("architecture-risk:hold", 0.3)],
            kind="agent",
            name="a",
        )
        self.assertLess(
            risky["exploration_bonus"],
            normal["exploration_bonus"],
        )


if __name__ == "__main__":
    unittest.main()
