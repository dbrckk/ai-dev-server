import sys
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


def test_preview_is_not_misrepresented_as_finished():
    report = completion_report(preview_state())
    assert report["finished"] is False
    assert "release_build_missing" in report["blockers"]
    assert "real_device_missing" in report["blockers"]
    assert next_stage(preview_state()) == "release_build"


def test_scheduler_advances_in_strict_order():
    state = preview_state()
    state["release_evidence"] = {"release_build": {"passed": True, "sha256": "abc"}}
    assert next_stage(state) == "real_device"
    state["release_evidence"]["real_device"] = True
    assert next_stage(state) == "store_metadata"
    state["release_evidence"]["store_metadata"] = True
    assert next_stage(state) == "privacy_policy"
    state["release_evidence"]["privacy_policy"] = True
    assert next_stage(state) == "security_scan"


def test_failed_stage_is_retried_not_skipped():
    state = preview_state()
    state["release_evidence"] = {"release_build": {"passed": False}}
    assert next_stage(state) == "release_build"


def test_all_release_evidence_can_finish():
    state = preview_state()
    state["release_evidence"] = {
        "release_build": {"passed": True, "sha256": "abc"},
        "real_device": True,
        "store_metadata": True,
        "privacy_policy": True,
        "security_scan": True,
    }
    report = apply_completion(state)
    assert report["finished"] is True
    assert report["next_stage"] is None
    assert state["status"] == "finished"
    assert state["release_status"] == "store_ready"
    assert completion_report(state)["finished"] is True


def test_missing_review_stays_blocked_even_with_release_evidence():
    state = preview_state()
    state["code_review"] = {"passed": False, "blockers": ["defect"]}
    state["release_evidence"] = {k: True for k in (
        "release_build", "real_device", "store_metadata", "privacy_policy", "security_scan"
    )}
    assert completion_report(state)["finished"] is False


def test_unvalidated_app_returns_to_preview_stage():
    state = preview_state()
    state["status"] = "repair_needed"
    assert next_stage(state) == "preview"
