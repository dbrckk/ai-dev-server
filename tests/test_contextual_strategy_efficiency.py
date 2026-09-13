import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from contextual_strategy_efficiency import load, record, rows_for, blend_rows
from strategy_efficiency import best_strategy


class ContextualStrategyEfficiencyTests(unittest.TestCase):
    def test_contexts_learn_independently(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"contextual.json"
            for _ in range(4):
                record(path,"frontend","model_only",success=True,cost_seconds=60)
                record(path,"frontend","agent_only",success=False,cost_seconds=60)
                record(path,"backend","agent_only",success=True,cost_seconds=60)
                record(path,"backend","model_only",success=False,cost_seconds=60)
            data=load(path)
            self.assertEqual(best_strategy(rows_for(data,"frontend"))[0],"model_only")
            self.assertEqual(best_strategy(rows_for(data,"backend"))[0],"agent_only")

    def test_weighted_blend_can_combine_bugfix_backend_and_tests(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"contextual.json"
            for _ in range(4):
                record(path,"bugfix","model_only",success=True,cost_seconds=40)
                record(path,"backend","model_only",success=True,cost_seconds=60)
                record(path,"tests","agent_only",success=True,cost_seconds=30)
            data=load(path)
            blended=blend_rows(data,[("bugfix",0.5),("backend",0.3),("tests",0.2)])
            self.assertIn("model_only",blended)
            self.assertIn("agent_only",blended)
            self.assertGreater(blended["model_only"]["samples"],blended["agent_only"]["samples"])
            self.assertGreater(blended["model_only"]["ema_success_rate"],0.9)

    def test_unknown_context_returns_empty_rows(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"contextual.json"
            record(path,"frontend","model_only",success=True,cost_seconds=60)
            self.assertEqual(rows_for(load(path),"mobile"),{})

    def test_recent_success_is_tracked_per_context(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"contextual.json"
            for _ in range(4):
                record(path,"bugfix","model_only",success=True,cost_seconds=40)
            data=load(path)
            row=rows_for(data,"bugfix")["model_only"]
            self.assertAlmostEqual(row["ema_success_rate"],1.0)


if __name__=="__main__":
    unittest.main()
