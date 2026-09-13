import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from strategy_efficiency import best_strategy, load, metrics, record, select_strategy


class StrategyEfficiencyTests(unittest.TestCase):
    def test_strategy_requires_four_samples(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"strategy-efficiency.json"
            for _ in range(3):
                record(path,"model_only",success=True,cost_seconds=100)
            self.assertIsNone(metrics(load(path),"model_only"))
            record(path,"model_only",success=True,cost_seconds=100)
            self.assertIsNotNone(metrics(load(path),"model_only"))

    def test_best_strategy_prefers_verified_success_per_cost(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"strategy-efficiency.json"
            for _ in range(4):
                record(path,"model_only",success=True,cost_seconds=100)
                record(path,"dual",success=True,cost_seconds=300)
            best=best_strategy(load(path))
            self.assertEqual(best[0],"model_only")
            self.assertGreater(best[1]["efficiency"],0)

    def test_bandit_exploits_best_strategy_outside_exploration_window(self):
        data={
            "model_only":{"samples":5,"successes":5,"ema_cost_seconds":80.0},
            "dual":{"samples":4,"successes":4,"ema_cost_seconds":240.0},
        }
        selected=select_strategy(data,allowed={"model_only","dual"},exploration_every=6)
        self.assertEqual(selected[0],"model_only")
        self.assertEqual(selected[1]["selection_mode"],"exploit")

    def test_bandit_explores_least_sampled_alternative_on_cadence(self):
        data={
            "model_only":{"samples":6,"successes":6,"ema_cost_seconds":80.0},
            "dual":{"samples":0,"successes":0,"ema_cost_seconds":0.0},
            "agent_only":{"samples":0,"successes":0,"ema_cost_seconds":0.0},
        }
        selected=select_strategy(
            data,
            allowed={"model_only","dual","agent_only"},
            exploration_every=6,
        )
        self.assertEqual(selected[0],"agent_only")
        self.assertEqual(selected[1]["selection_mode"],"explore")
        self.assertEqual(selected[1]["exploited_strategy"],"model_only")

    def test_bandit_requires_mature_strategy_before_exploration(self):
        data={
            "model_only":{"samples":3,"successes":3,"ema_cost_seconds":80.0},
            "dual":{"samples":3,"successes":3,"ema_cost_seconds":240.0},
        }
        self.assertIsNone(select_strategy(data,allowed={"model_only","dual"}))

    def test_failure_rate_reduces_efficiency(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"strategy-efficiency.json"
            for i in range(4):
                record(path,"agent_only",success=(i==0),cost_seconds=50)
                record(path,"model_to_agent",success=True,cost_seconds=80)
            best=best_strategy(load(path))
            self.assertEqual(best[0],"model_to_agent")


if __name__=="__main__":
    unittest.main()
