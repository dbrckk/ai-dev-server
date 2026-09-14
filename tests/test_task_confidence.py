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
            acceptance_review={"complete":True,"criteria":[]},
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
            acceptance_review={"complete":True,"criteria":[]},
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
            acceptance_review={"complete":True,"criteria":[]},
        )
        self.assertEqual(result.score,0)
        self.assertEqual(result.level,"unverified")

    def test_unaccepted_task_has_zero_confidence(self):
        result=score(
            verification={"passed":True},
            semantic_context=None,
            fragility={"max_risk":0.0,"level":"low"},
            dependency={"max_coupling":0},
            task_attempts=1,
            acceptance_review={"complete":False,"criteria":[]},
        )
        self.assertEqual(result.score,0)
        self.assertEqual(result.level,"unaccepted")

    def test_deterministic_acceptance_evidence_increases_confidence(self):
        semantic=score(
            verification={"passed":True,"stability_confirmed":True},
            semantic_context=None,
            fragility={"max_risk":0.0,"level":"low"},
            dependency={"max_coupling":0},
            task_attempts=1,
            acceptance_review={
                "complete":True,
                "criteria":[{
                    "criterion":"manual behavior review",
                    "passed":True,
                    "evidence_refs":["src/api.py"],
                }],
            },
        )
        deterministic=score(
            verification={"passed":True,"stability_confirmed":True},
            semantic_context=None,
            fragility={"max_risk":0.0,"level":"low"},
            dependency={"max_coupling":0},
            task_attempts=1,
            acceptance_review={
                "complete":True,
                "criteria":[{
                    "criterion":"test:tests/test_api.py::test_ok",
                    "passed":True,
                    "evidence_refs":["tests/test_api.py"],
                    "source":"deterministic",
                }],
            },
        )
        self.assertGreater(deterministic.score,semantic.score)
        self.assertEqual(deterministic.factors["deterministic_criteria_count"],1)

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
            acceptance_review={"complete":True,"criteria":[]},
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
            acceptance_review={"complete":True,"criteria":[]},
        )
        self.assertLess(penalized.score,base.score)


if __name__=="__main__":
    unittest.main()
