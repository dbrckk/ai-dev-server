from pathlib import Path
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from release_confidence import assess


class ReleaseConfidenceTests(unittest.TestCase):
    def test_high_confidence_release_is_ready(self):
        dag={
            "complete":True,
            "tasks":[
                {"id":"core","title":"core","critical":False,"confidence":88},
                {"id":"release","title":"release","critical":True,"confidence":92},
            ],
        }
        result=assess(dag,{"passed":True})
        self.assertTrue(result["ready_for_final_review"])
        self.assertEqual(result["weak_tasks"],[])
        self.assertGreaterEqual(result["score"],75)

    def test_low_confidence_normal_task_blocks_final_review(self):
        dag={
            "complete":True,
            "tasks":[
                {"id":"core","title":"core","critical":False,"confidence":60},
                {"id":"release","title":"release","critical":True,"confidence":90},
            ],
        }
        result=assess(dag,{"passed":True})
        self.assertFalse(result["ready_for_final_review"])
        self.assertEqual(result["weak_tasks"][0]["id"],"core")
        self.assertEqual(result["weak_tasks"][0]["minimum"],65)

    def test_critical_task_uses_higher_threshold(self):
        dag={
            "complete":True,
            "tasks":[
                {"id":"release","title":"release","critical":True,"confidence":84},
            ],
        }
        result=assess(dag,{"passed":True})
        self.assertFalse(result["ready_for_final_review"])
        self.assertEqual(result["weak_tasks"][0]["minimum"],85)

    def test_missing_confidence_is_treated_as_stale(self):
        dag={
            "complete":True,
            "tasks":[{"id":"legacy","title":"legacy","critical":False,"confidence":None}],
        }
        result=assess(dag,{"passed":True})
        self.assertFalse(result["ready_for_final_review"])
        self.assertEqual(result["weak_tasks"][0]["confidence"],None)

    def test_failed_full_verification_blocks_release_confidence(self):
        dag={
            "complete":True,
            "tasks":[{"id":"core","title":"core","critical":False,"confidence":100}],
        }
        result=assess(dag,{"passed":False})
        self.assertFalse(result["ready_for_final_review"])
        self.assertEqual(result["level"],"unverified")


if __name__=="__main__":
    unittest.main()
