"""Deterministic repair planning from normalized diagnostics."""
from __future__ import annotations

PRIORITY = (
    ("human_or_external", "human_action"),
    ("environment", "retry_environment"),
    ("prerequisite", "satisfy_prerequisite"),
    ("code", "repair_code"),
    ("unknown", "investigate_unknown"),
)


def plan(stage: str, diagnostics: dict) -> dict:
    selected = "complete"
    blockers: list[str] = []
    for bucket, action in PRIORITY:
        values = diagnostics.get(bucket, [])
        if values:
            selected = action
            blockers = list(values)
            break
    return {
        "stage": stage,
        "action": selected,
        "blockers": blockers,
        "automatic": selected in {
            "repair_code",
            "retry_environment",
            "satisfy_prerequisite",
        },
    }


def preview_plan(stage: str, blockers: list[str], *, kind: str = "code") -> dict:
    diagnostics = {
        "code": [],
        "environment": [],
        "human_or_external": [],
        "prerequisite": [],
        "unknown": [],
    }
    if kind not in diagnostics:
        kind = "unknown"
    diagnostics[kind] = list(blockers)
    return plan(stage, diagnostics)
