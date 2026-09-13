"""Trusted selection of prior autonomous-run artifacts for release handoff."""
from __future__ import annotations

import re

PROJECT_RE = re.compile(r"[a-z0-9][a-z0-9-]{0,47}")


class ArtifactHandoffError(ValueError):
    pass


def select_latest_project_artifact(payload: dict, project_id: str) -> dict | None:
    if not isinstance(project_id, str) or not PROJECT_RE.fullmatch(project_id):
        raise ArtifactHandoffError("project id invalid")
    if not isinstance(payload, dict) or not isinstance(payload.get("artifacts"), list):
        raise ArtifactHandoffError("artifact listing invalid")

    prefix = "mobile-" + project_id + "-"
    candidates = []
    for item in payload["artifacts"]:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        expired = item.get("expired")
        workflow_run = item.get("workflow_run")
        created_at = item.get("created_at")
        artifact_id = item.get("id")
        if (
            not isinstance(name, str)
            or not name.startswith(prefix)
            or expired is not False
            or not isinstance(workflow_run, dict)
            or type(workflow_run.get("id")) is not int
            or workflow_run["id"] <= 0
            or type(artifact_id) is not int
            or artifact_id <= 0
            or not isinstance(created_at, str)
            or not created_at
        ):
            continue
        suffix = name[len(prefix):]
        if not suffix.isdigit():
            continue
        candidates.append({
            "name": name,
            "run_id": workflow_run["id"],
            "artifact_id": artifact_id,
            "created_at": created_at,
        })

    if not candidates:
        return None

    candidates.sort(
        key=lambda item: (item["created_at"], item["artifact_id"]),
        reverse=True,
    )
    latest = candidates[0]
    if len(candidates) > 1 and candidates[1]["created_at"] == latest["created_at"]:
        if candidates[1]["artifact_id"] == latest["artifact_id"]:
            raise ArtifactHandoffError("artifact listing ambiguous")
    return latest
