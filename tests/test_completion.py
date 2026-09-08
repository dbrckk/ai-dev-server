import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "studio"))
from completion import apply_completion, completion_report


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


def test_all_release_evidence_can_finish():
    state = preview_state()
    state["release_evidence"] = {
        "release_build": True,
        "real_device": True,
        "store_metadata": True,
        "privacy_policy": True,
        "security_scan": True,
    }
    report = apply_completion(state)
    assert report["finished"] is True
    assert state["status"] == "finished"
    assert state["release_status"] == "store_ready"


def test_missing_review_stays_blocked_even_with_release_evidence():
    state = preview_state()
    state["code_review"] = {"passed": False, "blockers": ["defect"]}
    state["release_evidence"] = {k: True for k in (
        "release_build", "real_device", "store_metadata", "privacy_policy", "security_scan"
    )}
    assert completion_report(state)["finished"] is False
