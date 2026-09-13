import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from phase_cost_baseline import baseline, load, record


class PhaseCostBaselineTests(unittest.TestCase):
    def test_baseline_requires_four_samples(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"phase-cost-baselines.json"
            toolchain={"stacks":["python"]}
            for value in (100,110,90):
                record(path,toolchain,"verification",value)
            self.assertIsNone(baseline(load(path),toolchain,"verification"))
            record(path,toolchain,"verification",105)
            b=baseline(load(path),toolchain,"verification")
            self.assertIsNotNone(b)
            self.assertEqual(b["samples"],4)
            self.assertGreaterEqual(b["ema_abs_deviation"],0)

    def test_baselines_are_separated_by_toolchain_and_phase(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"phase-cost-baselines.json"
            for _ in range(4):
                record(path,{"stacks":["python"]},"verification",100)
                record(path,{"stacks":["node"]},"verification",20)
                record(path,{"stacks":["python"]},"planning",10)
            data=load(path)
            self.assertAlmostEqual(baseline(data,{"stacks":["python"]},"verification")["ema_seconds"],100)
            self.assertAlmostEqual(baseline(data,{"stacks":["node"]},"verification")["ema_seconds"],20)
            self.assertAlmostEqual(baseline(data,{"stacks":["python"]},"planning")["ema_seconds"],10)


if __name__=="__main__":
    unittest.main()
