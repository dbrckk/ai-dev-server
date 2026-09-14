from pathlib import Path
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from task_acceptance import accepted, failure_reason


class TaskAcceptanceTests(unittest.TestCase):
    def test_requires_verification_review_and_real_changes(self):
        self.assertTrue(accepted(
            verification={"passed":True},
            review={"complete":True},
            changed_files=["src/api.py"],
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
