"""Definition-of-done contract for autonomous mobile generation.

A green preview is evidence, not a finished application.  This module keeps the
orchestrator honest and gives CI a machine-readable list of work that remains.
"""
from __future__ import annotations

PREVIEW_STATUS = "validated_preview"
FINISHED_STATUS = "finished"


def completion_report(state: dict) -> dict:
    """Return a deterministic completion assessment without inventing evidence."""
    blockers: list[str] = []
    if state.get("status") != PREVIEW_STATUS:
        blockers.append("preview_not_validated")
    if state.get("validation_contract") != 2:
        blockers.append("acceptance_journeys_not_validated")
    if not state.get("code_review", {}).get("passed"):
        blockers.append("independent_code_review_not_passed")
    if not state.get("visual_review", {}).get("passed"):
        blockers.append("visual_review_not_passed")
    if not state.get("apk_sha256"):
        blockers.append("validated_apk_not_exported")

    # These require later trusted release stages. They deliberately cannot be
    # asserted by a coding model or inferred from a successful debug build.
    release = state.get("release_evidence", {})
    for key in ("release_build", "real_device", "store_metadata", "privacy_policy", "security_scan"):
        if not release.get(key):
            blockers.append(key + "_missing")

    return {
        "finished": not blockers,
        "status": FINISHED_STATUS if not blockers else "work_remaining",
        "blockers": blockers,
    }


def apply_completion(state: dict) -> dict:
    report = completion_report(state)
    state["completion"] = report
    state["release_status"] = "store_ready" if report["finished"] else "not_store_ready"
    if report["finished"]:
        state["status"] = FINISHED_STATUS
    return report
