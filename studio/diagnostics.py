"""Normalize stage failures into machine, environment, and human-owned diagnostics."""
from __future__ import annotations

ENVIRONMENT_BLOCKERS = {
    "adb_unavailable",
    "emulator_boot_timeout",
    "ambiguous_android_target",
    "release_permission_inspection_unavailable",
    "notification_shade_expand_failed",
    "notification_ui_dump_failed",
    "notification_ui_dump_unreadable",
    "notification_ui_dump_invalid",
    "notification_app_label_unavailable",
    "platform_view_screenshot_failed",
}

HUMAN_OR_EXTERNAL_BLOCKERS = {
    "biometric_outcome_requires_app_contract",
    "play_billing_sandbox_purchase_not_verified",
    "billing_sandbox_evidence_invalid",
    "external_push_delivery_not_exercised",
}

PREREQUISITE_BLOCKERS = {
    "release_apk_missing",
}

CODE_PREFIXES = (
    "app_unstable_for_",
    "notification_lifecycle_unstable:",
    "notification_permission_state_control_failed:",
    "permission_state_control_failed:",
)

CODE_BLOCKERS = {
    "release_install_failed",
    "release_launch_failed",
    "runtime_crash_or_anr_detected",
    "interaction_stress_failed",
    "excessive_jank",
    "severe_frame_stall",
    "insufficient_frame_samples",
    "location_callback_unstable",
    "biometric_transport_unstable",
    "no_app_originated_notification_observed",
    "notification_runtime_crash_or_anr_detected",
    "notification_click_target_not_found",
    "notification_click_bounds_invalid",
    "notification_tap_did_not_resume_stably",
    "notification_tap_not_verified",
    "billing_integration_not_detected",
    "platform_view_dependency_not_detected",
    "platform_view_not_observable_in_native_ui_tree",
    "platform_view_unstable_after_resume",
}


def _kind(blocker: str) -> str:
    base = blocker.split(":", 1)[0]
    if blocker in HUMAN_OR_EXTERNAL_BLOCKERS or base in HUMAN_OR_EXTERNAL_BLOCKERS:
        return "human_or_external"
    if blocker in ENVIRONMENT_BLOCKERS or base in ENVIRONMENT_BLOCKERS:
        return "environment"
    if blocker in PREREQUISITE_BLOCKERS or base in PREREQUISITE_BLOCKERS:
        return "prerequisite"
    if blocker in CODE_BLOCKERS or base in CODE_BLOCKERS or blocker.startswith(CODE_PREFIXES):
        return "code"
    return "unknown"


def classify(stage: str, evidence: dict) -> dict:
    blockers = evidence.get("blockers", [])
    if not isinstance(blockers, list):
        blockers = []
    items = [
        {"stage": stage, "blocker": blocker, "kind": _kind(blocker)}
        for blocker in blockers if isinstance(blocker, str) and blocker
    ]
    return {
        "stage": stage,
        "items": items,
        "code": [x["blocker"] for x in items if x["kind"] == "code"],
        "environment": [x["blocker"] for x in items if x["kind"] == "environment"],
        "human_or_external": [x["blocker"] for x in items if x["kind"] == "human_or_external"],
        "prerequisite": [x["blocker"] for x in items if x["kind"] == "prerequisite"],
        "unknown": [x["blocker"] for x in items if x["kind"] == "unknown"],
    }


def repairable(stage: str, evidence: dict) -> list[str]:
    return classify(stage, evidence)["code"]
