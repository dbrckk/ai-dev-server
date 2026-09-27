"""Fail-closed readiness evaluation for an exact GitHub pull-request head."""
from __future__ import annotations

_FAILURES = {"failure", "cancelled", "timed_out", "action_required", "startup_failure"}
_RUNNING = {"queued", "in_progress", "pending", "requested", "waiting"}


def evaluate(github, commit_sha: str) -> dict:
    runs_payload = github.get("/actions/runs?head_sha=" + commit_sha + "&per_page=100")
    runs = (
        runs_payload.get("workflow_runs", [])
        if isinstance(runs_payload, dict)
        else []
    )
    statuses_payload = github.get("/commits/" + commit_sha + "/status")
    statuses = (
        statuses_payload.get("statuses", [])
        if isinstance(statuses_payload, dict)
        else []
    )

    failures = []
    pending = []
    for run in runs if isinstance(runs, list) else []:
        if not isinstance(run, dict):
            continue
        name = str(run.get("name") or "workflow")
        status = str(run.get("status") or "").lower()
        conclusion = str(run.get("conclusion") or "").lower()
        if conclusion in _FAILURES:
            failures.append(name)
        elif status in _RUNNING or not conclusion:
            pending.append(name)
        elif status != "completed" or conclusion != "success":
            pending.append(name)

    for item in statuses if isinstance(statuses, list) else []:
        if not isinstance(item, dict):
            continue
        name = str(item.get("context") or "status")
        state = str(item.get("state") or "").lower()
        if state in {"failure", "error"}:
            failures.append(name)
        elif state in {"pending", "expected"}:
            pending.append(name)
        elif state != "success":
            pending.append(name)

    if failures:
        state = "failed"
    elif pending:
        state = "pending"
    elif runs or statuses:
        state = "ready"
    else:
        state = "unknown"

    return {
        "state": state,
        "failures": sorted(set(failures))[:50],
        "pending": sorted(set(pending))[:50],
    }
