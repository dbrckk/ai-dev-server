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

    def test_component_breakdown_sums_to_score(self):
        result = score(provider=Provider(priority=70, free_preferred=True), role="tests", model="m")
        self.assertAlmostEqual(result["score"], sum(result["components"].values()))


if __name__ == "__main__":
    unittest.main()
