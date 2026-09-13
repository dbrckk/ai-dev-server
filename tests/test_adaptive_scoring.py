import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from adaptive_scoring import score_agent, score_provider


class AdaptiveScoringTests(unittest.TestCase):
    def test_provider_trace_sums_components(self):
        trace = score_provider(
            name="p",
            priority=50,
            free_preferred=True,
            reliability=12,
            latency=-6,
        )
        self.assertEqual(trace.total, 76.0)
        self.assertEqual(trace.as_dict()["components"]["free"], 20.0)

    def test_agent_trace_is_explainable(self):
        trace = score_agent(
            name="a",
            capability_fit=90,
            priority=40,
            free_adjustment=30,
            long_task_adjustment=20,
            reliability=5,
        )
        data = trace.as_dict()
        self.assertEqual(data["total"], 185.0)
        self.assertEqual(
            set(data["components"]),
            {"capability_fit", "priority", "free", "long_task", "reliability"},
        )


if __name__ == "__main__":
    unittest.main()
