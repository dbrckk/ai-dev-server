from pathlib import Path
import tempfile
import unittest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from verification_cost import estimate_seconds, load, record, stack_key


class VerificationCostTests(unittest.TestCase):
    def test_stack_key_is_stable_for_multi_stack_repo(self):
        self.assertEqual(stack_key({"stacks":["python","node","python"]}), "node+python")

    def test_ema_is_learned_per_toolchain(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"verification-cost.json"
            record(path,{"stacks":["python"]},elapsed_seconds=100,success=True)
            record(path,{"stacks":["python"]},elapsed_seconds=60,success=False)
            record(path,{"stacks":["node"]},elapsed_seconds=20,success=True)
            data=load(path)
            self.assertAlmostEqual(data["python"]["ema_seconds"],90.0)
            self.assertEqual(data["python"]["runs"],2)
            self.assertEqual(data["node"]["runs"],1)
            self.assertAlmostEqual(estimate_seconds(data,{"stacks":["python"]},fallback=30),90.0)
            self.assertEqual(estimate_seconds(data,{"stacks":["node"]},fallback=30),30)

    def test_unknown_toolchain_uses_fallback_until_two_runs(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"verification-cost.json"
            record(path,{},elapsed_seconds=45,success=True)
            data=load(path)
            self.assertEqual(estimate_seconds(data,{},fallback=20),20)


if __name__=="__main__":
    unittest.main()
