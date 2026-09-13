import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from strategy_efficiency import best_strategy, exploration_cadence, load, metrics, record, select_strategy


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

    def test_exploration_is_more_frequent_when_strategies_are_close(self):
        data={
            "model_only":{"samples":8,"successes":8,"ema_cost_seconds":100.0},
            "dual":{"samples":8,"successes":8,"ema_cost_seconds":105.0},
        }
        self.assertEqual(exploration_cadence(data,allowed={"model_only","dual"}),4)

    def test_exploration_decays_for_durable_dominant_strategy(self):
        data={
            "model_only":{"samples":24,"successes":24,"ema_cost_seconds":50.0},
            "dual":{"samples":24,"successes":12,"ema_cost_seconds":200.0},
        }
        self.assertEqual(exploration_cadence(data,allowed={"model_only","dual"}),12)

    def test_exploration_never_disappears(self):
        data={
            "model_only":{"samples":100,"successes":100,"ema_cost_seconds":20.0},
            "dual":{"samples":100,"successes":1,"ema_cost_seconds":500.0},
        }
        cadence=exploration_cadence(data,allowed={"model_only","dual"})
        self.assertLessEqual(cadence,12)
        selected=select_strategy(
            {
                "model_only":{"samples":6,"successes":6,"ema_cost_seconds":20.0},
                "dual":{"samples":6,"successes":1,"ema_cost_seconds":500.0},
            },
            allowed={"model_only","dual"},
            exploration_every=12,
        )
        self.assertEqual(selected[1]["exploration_cadence"],12)

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

    def test_recent_failures_can_dethrone_historical_winner(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"strategy-efficiency.json"
            for _ in range(20):
                record(path,"model_only",success=True,cost_seconds=60)
            for _ in range(4):
                record(path,"dual",success=True,cost_seconds=90)
            for _ in range(8):
                record(path,"model_only",success=False,cost_seconds=60)
            best=best_strategy(load(path))
            self.assertEqual(best[0],"dual")

    def test_regime_shift_increases_exploration_frequency(self):
        data={
            "model_only":{
                "samples":20,
                "successes":18,
                "ema_cost_seconds":60.0,
                "ema_success_rate":0.45,
            },
            "dual":{
                "samples":20,
                "successes":15,
                "ema_cost_seconds":80.0,
                "ema_success_rate":0.75,
            },
        }
        self.assertEqual(
            exploration_cadence(data,allowed={"model_only","dual"}),
            4,
        )

    def test_legacy_strategy_rows_migrate_recent_success_from_cumulative_rate(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"strategy-efficiency.json"
            path.write_text(
                '{"model_only":{"samples":4,"successes":3,"ema_cost_seconds":50.0}}'
            )
            row=load(path)["model_only"]
            self.assertAlmostEqual(row["ema_success_rate"],0.75)

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
