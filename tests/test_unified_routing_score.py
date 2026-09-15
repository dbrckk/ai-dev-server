import unittest
from dataclasses import dataclass
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from unified_routing_score import score


@dataclass
class Provider:
    name: str = "p"
    priority: int = 50
    free_preferred: bool = False
    unmetered: bool = False
    monthly_token_quota: int = 0


class UnifiedRoutingScoreTests(unittest.TestCase):
    def test_free_unmetered_provider_gets_bounded_resource_bonus(self):
        result = score(provider=Provider(free_preferred=True, unmetered=True), role="implementation", model="m")
        self.assertEqual(result["components"]["free"], 8.0)
        self.assertEqual(result["components"]["unmetered"], 10.0)

    def test_runtime_and_latency_are_combined(self):
        runtime = {"routes": {"p::m": {"reliability_score": 0.9, "confidence": 1.0}}}
        metrics = {"p:implementation": {"calls": 5, "ema_latency_seconds": 1.0}}
        result = score(provider=Provider(), role="implementation", model="m", runtime=runtime, metrics=metrics)
        self.assertGreater(result["components"]["runtime_reliability"], 0)
        self.assertGreater(result["components"]["latency"], 0)

    def test_context_and_exploration_are_strictly_bounded(self):
        result = score(
            provider=Provider(), role="implementation", model="m",
            contextual_adjustment=-999, exploration_bonus=999,
        )
        self.assertEqual(result["components"]["context"], -18.0)
        self.assertEqual(result["components"]["exploration"], 8.0)

    def test_specialized_health_changes_score_by_role(self):
        health = {
            "p": {"successes": 5, "failures": 5},
            "p|model=m|role=implementation": {"successes": 9, "failures": 1},
            "p|model=m|role=review": {"successes": 1, "failures": 9},
        }
        implementation = score(
            provider=Provider(), role="implementation", model="m", health=health,
        )
        review = score(
            provider=Provider(), role="review", model="m", health=health,
        )
        self.assertGreater(
            implementation["components"]["specialized_health"], 0,
        )
        self.assertLess(review["components"]["specialized_health"], 0)
        self.assertGreater(implementation["score"], review["score"])

    def test_missing_specialization_is_neutral_with_no_health(self):
        result = score(
            provider=Provider(), role="planning", model="m", health={},
        )
        self.assertEqual(result["components"]["specialized_health"], 0.0)

    def test_sparse_specialization_has_limited_influence(self):
        sparse = score(
            provider=Provider(),
            role="implementation",
            model="m",
            health={"p|model=m|role=implementation": {"successes": 1, "failures": 0}},
        )
        mature = score(
            provider=Provider(),
            role="implementation",
            model="m",
            health={"p|model=m|role=implementation": {"successes": 95, "failures": 5}},
        )
        self.assertLess(
            sparse["components"]["specialized_confidence"],
            mature["components"]["specialized_confidence"],
        )
        self.assertLess(
            sparse["components"]["specialized_health"],
            mature["components"]["specialized_health"],
        )

    def test_no_observations_have_zero_specialized_confidence(self):
        result = score(provider=Provider(), role="review", model="m", health={})
        self.assertEqual(result["components"]["specialized_confidence"], 0.0)
        self.assertEqual(result["components"]["specialized_observations"], 0)
        self.assertEqual(result["components"]["specialized_health"], 0.0)

    def test_component_breakdown_sums_to_score(self):
        result = score(provider=Provider(priority=70, free_preferred=True), role="tests", model="m")
        additive_keys = {
            "priority", "free", "unmetered", "quota", "health",
            "specialized_health", "latency", "runtime_reliability",
            "context", "exploration", "verified_outcome_calibration",
        }
        self.assertAlmostEqual(
            result["score"],
            sum(result["components"][key] for key in additive_keys),
        )


if __name__ == "__main__":
    unittest.main()
