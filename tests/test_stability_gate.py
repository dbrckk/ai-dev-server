from pathlib import Path
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from stability_gate import combine, should_recheck


class StabilityGateTests(unittest.TestCase):
    def test_rechecks_only_passing_fragile_rounds(self):
        self.assertTrue(should_recheck(
            {"extra_verification": True},
            {"passed": True},
        ))
        self.assertFalse(should_recheck(
            {"extra_verification": False},
            {"passed": True},
        ))
        self.assertFalse(should_recheck(
            {"extra_verification": True},
            {"passed": False},
        ))

    def test_failed_recheck_turns_round_red(self):
        primary={"status":"passed","passed":True,"results":[{"passed":True}]}
        second={"status":"failed","passed":False,"results":[{"passed":False}]}
        result=combine(primary,second)
        self.assertFalse(result["passed"])
        self.assertEqual(result["status"],"failed")
        self.assertFalse(result["stability_confirmed"])
        self.assertEqual(len(result["results"]),2)

    def test_passing_recheck_confirms_stability(self):
        primary={"status":"passed","passed":True,"results":[]}
        second={"status":"passed","passed":True,"results":[]}
        result=combine(primary,second)
        self.assertTrue(result["passed"])
        self.assertTrue(result["stability_confirmed"])


if __name__=="__main__":
    unittest.main()
