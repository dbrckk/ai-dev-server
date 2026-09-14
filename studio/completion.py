"""Definition-of-done contract for autonomous mobile generation.

A green preview is evidence, not a finished application. This module keeps the
orchestrator honest and gives CI a machine-readable list of work that remains.
"""
from __future__ import annotations

from task_scheduler import dispatch as scheduler_dispatch, pipeline_stage_for_task, select as select_repair_task

PREVIEW_STATUS = "validated_preview"
FINISHED_STATUS = "finished"
HUMAN_ACTION_STATUS = "human_action_required"

BASE_RELEASE_STAGES = (
    "release_build",
    "real_device",
    "capability_qa",
)
POST_QA_STAGES = (
    "store_metadata",
    "artwork_qa",
    "privacy_policy",
    "security_scan",
)
ALLOWED_DYNAMIC_QA = {
    "performance_qa",
    "native_qa",
    "notification_qa",
    "billing_qa",
    "platform_view_qa",
}


def required_release_stages(state: dict) -> tuple[str, ...]:
    """Return trusted stages in order, including capability-derived QA gates."""
    release = state.get("release_evidence", {})
    capability = release.get("capability_qa")
    dynamic: list[str] = []
    if isinstance(capability, dict) and capability.get("passed"):
        requested = capability.get("required_qa_stages", [])
        if isinstance(requested, list):
            for stage in requested:
                if stage in ALLOWED_DYNAMIC_QA and stage not in dynamic:
                    dynamic.append(stage)
    stages = BASE_RELEASE_STAGES + tuple(dynamic) + POST_QA_STAGES
    publication = state.get("publication_request", {})
    if isinstance(publication, dict) and publication.get("enabled") is True:
        stages += ("play_publish",)
    return stages


def completion_report(state: dict) -> dict:
    """Return a deterministic completion assessment without inventing evidence."""
    blockers: list[str] = []
    if state.get("status") not in (PREVIEW_STATUS, FINISHED_STATUS, HUMAN_ACTION_STATUS):
        blockers.append("preview_not_validated")
    if state.get("validation_contract") != 2:
        blockers.append("acceptance_journeys_not_validated")
    if not state.get("code_review", {}).get("passed"):
        blockers.append("independent_code_review_not_passed")
    if not state.get("visual_review", {}).get("passed"):
        blockers.append("visual_review_not_passed")
    if not state.get("apk_sha256"):
        blockers.append("validated_apk_not_exported")

    release = state.get("release_evidence", {})
    for key in required_release_stages(state):
        evidence = release.get(key)
        if not evidence or (isinstance(evidence, dict) and evidence.get("passed") is False):
            blockers.append(key + "_missing")

    return {
        "finished": not blockers,
        "status": FINISHED_STATUS if not blockers else "work_remaining",
        "blockers": blockers,
    }


def next_stage(state: dict) -> str | None:
    """Select the globally scheduled repair stage, then fall back to pipeline order."""
    report = completion_report(state)
    if report["finished"]:
        return None

    scheduled = select_repair_task(state)
    scheduled_stage = pipeline_stage_for_task(scheduled)
    if scheduled_stage is not None:
        return scheduled_stage

    if "preview_not_validated" in report["blockers"]:
        return "preview"
    release = state.get("release_evidence", {})
    for stage in required_release_stages(state):
        evidence = release.get(stage)
        if not evidence or (isinstance(evidence, dict) and evidence.get("passed") is False):
            return stage
    return "preview"


def apply_completion(state: dict) -> dict:
    report = completion_report(state)
    report["required_stages"] = list(required_release_stages(state))
    report["next_stage"] = next_stage(state)
    state["completion"] = report
    state["scheduler"] = scheduler_dispatch(state)
    state["release_status"] = "store_ready" if report["finished"] else "not_store_ready"
    if report["finished"]:
        state["status"] = FINISHED_STATUS
    return report
