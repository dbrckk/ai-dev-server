from pathlib import Path
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from task_acceptance import accepted, criteria_evidence, failure_reason


class TaskAcceptanceTests(unittest.TestCase):
    def test_requires_verification_review_and_real_changes(self):
        task={"title":"api","done_when":["endpoint returns 200"]}
        review={
            "complete":True,
            "criteria":[{"criterion":"endpoint returns 200","passed":True,"evidence":"integration test passed"}],
        }
        self.assertTrue(accepted(
            verification={"passed":True},
            review=review,
            changed_files=["src/api.py"],
            active_task=task,
        ))

    def test_green_tests_without_task_review_do_not_verify_task(self):
        self.assertFalse(accepted(
            verification={"passed":True},
            review={"complete":False,"reason":"behavior still missing"},
            changed_files=["src/api.py"],
        ))
        self.assertEqual(
            failure_reason(
                verification={"passed":True},
                review={"complete":False,"reason":"behavior still missing"},
            ),
            "behavior still missing",
        )

    def test_missing_criterion_evidence_rejects_task(self):
        task={"title":"api","done_when":["returns 200","rejects invalid input"]}
        review={
            "complete":True,
            "criteria":[{"criterion":"returns 200","passed":True,"evidence":"test passed"}],
        }
        evidence=criteria_evidence(task,review)
        self.assertEqual(evidence["missing"],["rejects invalid input"])
        self.assertFalse(accepted(
            verification={"passed":True},
            review=review,
            changed_files=["src/api.py"],
            active_task=task,
        ))
        self.assertIn("missing evidence",failure_reason(
            verification={"passed":True},
            review=review,
            active_task=task,
        ))

    def test_failed_criterion_rejects_task(self):
        task={"title":"api","done_when":["returns 200"]}
        review={
            "complete":True,
            "criteria":[{"criterion":"returns 200","passed":False,"evidence":"still returns 500"}],
        }
        self.assertFalse(accepted(
            verification={"passed":True},
            review=review,
            changed_files=["src/api.py"],
            active_task=task,
        ))
        self.assertIn("criteria failed",failure_reason(
            verification={"passed":True},
            review=review,
            active_task=task,
        ))

    def test_review_cannot_override_failed_verification(self):
        self.assertFalse(accepted(
            verification={"passed":False},
            review={"complete":True},
            changed_files=["src/api.py"],
        ))
        self.assertEqual(
            failure_reason(verification={"passed":False},review={"complete":True}),
            "trusted verification failed",
        )

    def test_no_change_cannot_verify_task(self):
        self.assertFalse(accepted(
            verification={"passed":True},
            review={"complete":True},
            changed_files=[],
        ))


if __name__=="__main__":
    unittest.main()
