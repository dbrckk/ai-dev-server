from pathlib import Path
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from task_confidence import can_unlock_critical, score


class TaskConfidenceTests(unittest.TestCase):
    def test_high_confidence_verified_stable_task(self):
        result=score(
            verification={
                "passed":True,
                "stability_confirmed":True,
                "targeted_precheck":{"passed":True},
                "targeted_impact":{"impacted_tests":["tests/test_api.py"]},
            },
            semantic_context={"last_status":"verified","recent_attempts":[{"status":"verified"}]},
            fragility={"max_risk":0.1,"level":"low"},
            dependency={"max_coupling":1},
            task_attempts=1,
        )
        self.assertEqual(result.level,"high")
        self.assertGreaterEqual(result.score,85)
        self.assertTrue(can_unlock_critical(result))

    def test_retries_fragility_and_coupling_reduce_confidence(self):
        result=score(
            verification={"passed":True,"stability_confirmed":False},
            semantic_context={
                "last_status":"verified",
                "recent_attempts":[
                    {"status":"failed"},
                    {"status":"failed"},
                    {"status":"verified"},
                ],
            },
            fragility={"max_risk":0.9,"level":"high"},
            dependency={"max_coupling":9},
            task_attempts=3,
        )
        self.assertEqual(result.level,"low")
        self.assertFalse(can_unlock_critical(result))

    def test_unverified_task_scores_zero(self):
        result=score(
            verification={"passed":False},
            semantic_context=None,
            fragility=None,
            dependency=None,
            task_attempts=1,
        )
        self.assertEqual(result.score,0)
        self.assertEqual(result.level,"unverified")

    def test_targeted_failure_penalizes_confidence(self):
        base=score(
            verification={
                "passed":True,
                "stability_confirmed":True,
                "targeted_precheck":{"passed":True},
                "targeted_impact":{"impacted_tests":["tests/test_api.py"]},
            },
            semantic_context={"last_status":"verified","recent_attempts":[]},
            fragility={"max_risk":0.0,"level":"low"},
            dependency={"max_coupling":0},
            task_attempts=1,
        )
        penalized=score(
            verification={
                "passed":True,
                "stability_confirmed":True,
                "targeted_precheck":{"passed":False},
                "targeted_impact":{"impacted_tests":["tests/test_api.py"]},
            },
            semantic_context={"last_status":"verified","recent_attempts":[]},
            fragility={"max_risk":0.0,"level":"low"},
            dependency={"max_coupling":0},
            task_attempts=1,
        )
        self.assertLess(penalized.score,base.score)


if __name__=="__main__":
    unittest.main()
