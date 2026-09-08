import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "studio"))
from completion import apply_completion, completion_report, next_stage


def preview_state():
    return {
        "status": "validated_preview",
        "validation_contract": 2,
        "code_review": {"passed": True, "blockers": []},
        "visual_review": {"passed": True, "blockers": []},
        "apk_sha256": "abc",
    }


class CompletionTests(unittest.TestCase):
    def test_preview_is_not_misrepresented_as_finished(self):
        report = completion_report(preview_state())
        self.assertFalse(report["finished"])
        self.assertIn("release_build_missing", report["blockers"])
        self.assertIn("real_device_missing", report["blockers"])
        self.assertIn("capability_qa_missing", report["blockers"])
        self.assertEqual(next_stage(preview_state()), "release_build")

    def test_scheduler_advances_in_strict_order(self):
        state = preview_state()
        state["release_evidence"] = {"release_build": {"passed": True, "sha256": "abc"}}
        self.assertEqual(next_stage(state), "real_device")
        state["release_evidence"]["real_device"] = True
        self.assertEqual(next_stage(state), "capability_qa")
        state["release_evidence"]["capability_qa"] = {"passed": True, "required_qa_stages": []}
        self.assertEqual(next_stage(state), "store_metadata")
        state["release_evidence"]["store_metadata"] = True
        self.assertEqual(next_stage(state), "privacy_policy")
        state["release_evidence"]["privacy_policy"] = True
        self.assertEqual(next_stage(state), "security_scan")

    def test_failed_stage_is_retried_not_skipped(self):
        state = preview_state()
        state["release_evidence"] = {"release_build": {"passed": False}}
        self.assertEqual(next_stage(state), "release_build")

    def test_all_release_evidence_can_finish(self):
        state = preview_state()
        state["release_evidence"] = {
            "release_build": {"passed": True, "sha256": "abc"},
            "real_device": True,
            "capability_qa": {"passed": True, "required_qa_stages": []},
            "store_metadata": True,
            "privacy_policy": True,
            "security_scan": True,
        }
        report = apply_completion(state)
        self.assertTrue(report["finished"])
        self.assertIsNone(report["next_stage"])
        self.assertEqual(state["status"], "finished")
        self.assertEqual(state["release_status"], "store_ready")
        self.assertTrue(completion_report(state)["finished"])

    def test_missing_review_stays_blocked_even_with_release_evidence(self):
        state = preview_state()
        state["code_review"] = {"passed": False, "blockers": ["defect"]}
        state["release_evidence"] = {k: True for k in (
            "release_build", "real_device", "capability_qa", "store_metadata", "privacy_policy", "security_scan"
        )}
        self.assertFalse(completion_report(state)["finished"])

    def test_unvalidated_app_returns_to_preview_stage(self):
        state = preview_state()
        state["status"] = "repair_needed"
        self.assertEqual(next_stage(state), "preview")


if __name__ == "__main__":
    unittest.main()
