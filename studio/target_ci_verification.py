"""Read-only exact-commit CI proof for trusted source repair."""
from __future__ import annotations
import re
import time
from core import StudioError

_SHA = re.compile(r"[a-f0-9]{40}\Z")
_BRANCH = re.compile(r"studio/mp-[a-f0-9]{24}\Z")
_WORKFLOW = re.compile(r"\.github/workflows/[A-Za-z0-9_.-]+\.ya?ml\Z")

def inspect_exact_commit_ci(github, *, commit_sha: str, branch: str,
                            workflow_path: str, required_steps: tuple[str, ...]) -> dict:
    if not isinstance(commit_sha, str) or not _SHA.fullmatch(commit_sha):
        raise StudioError("Target CI commit SHA invalid")
    if not isinstance(branch, str) or not _BRANCH.fullmatch(branch):
        raise StudioError("Target CI review branch invalid")
    if not isinstance(workflow_path, str) or not _WORKFLOW.fullmatch(workflow_path):
        raise StudioError("Target CI workflow path invalid")
    if (not isinstance(required_steps, tuple) or not 1 <= len(required_steps) <= 12
            or any(not isinstance(s, str) or not 1 <= len(s) <= 120 for s in required_steps)):
        raise StudioError("Target CI required steps invalid")
    listing = github.get("/actions/runs?head_sha=" + commit_sha
                         + "&event=workflow_dispatch&per_page=100")
    runs = listing.get("workflow_runs") if isinstance(listing, dict) else None
    if not isinstance(runs, list) or len(runs) > 100:
        raise StudioError("Target CI workflow inventory invalid")
    eligible = [r for r in runs if isinstance(r, dict)
                and r.get("head_sha") == commit_sha
                and r.get("head_branch") == branch
                and r.get("event") == "workflow_dispatch"
                and r.get("path") == workflow_path
                and type(r.get("id")) is int and r["id"] > 0]
    if not eligible:
        return {"status": "pending", "reason": "exact_commit_ci_not_dispatched"}
    run = max(eligible, key=lambda r: r["id"])
    rid = run["id"]
    if run.get("status") != "completed":
        return {"status": "pending", "run_id": rid, "reason": "exact_commit_ci_in_progress"}
    if run.get("conclusion") != "success":
        return {"status": "failed", "run_id": rid, "reason": "exact_commit_ci_not_successful"}
    response = github.get("/actions/runs/" + str(rid) + "/jobs?per_page=100")
    jobs = response.get("jobs") if isinstance(response, dict) else None
    if (not isinstance(jobs, list) or not jobs
            or type(response.get("total_count")) is not int
            or response["total_count"] != len(jobs) or len(jobs) > 100):
        raise StudioError("Target CI job evidence incomplete")
    passed = set()
    for job in jobs:
        if not isinstance(job, dict) or job.get("status") != "completed" or job.get("conclusion") != "success":
            return {"status": "failed", "run_id": rid, "reason": "exact_commit_ci_job_not_successful"}
        steps = job.get("steps")
        if not isinstance(steps, list):
            raise StudioError("Target CI job steps unavailable")
        passed.update(step["name"] for step in steps if isinstance(step, dict)
                      and isinstance(step.get("name"), str)
                      and step.get("status") == "completed"
                      and step.get("conclusion") == "success")
    if not set(required_steps).issubset(passed):
        return {"status": "failed", "run_id": rid, "reason": "exact_commit_ci_required_steps_not_passed"}
    return {"status": "passed", "run_id": rid, "commit_sha": commit_sha}

def wait_for_exact_commit_ci(github, *, commit_sha: str, branch: str,
                             workflow_path: str, required_steps: tuple[str, ...],
                             timeout_seconds: float = 240, poll_seconds: float = 10,
                             clock=time.monotonic, sleeper=time.sleep) -> dict:
    if (type(timeout_seconds) not in (int, float) or not 0 <= timeout_seconds <= 600
            or type(poll_seconds) not in (int, float) or not 1 <= poll_seconds <= 60):
        raise StudioError("Target CI polling bounds invalid")
    deadline = clock() + timeout_seconds
    while True:
        result = inspect_exact_commit_ci(github, commit_sha=commit_sha, branch=branch,
                                         workflow_path=workflow_path, required_steps=required_steps)
        if result["status"] != "pending" or clock() >= deadline:
            return result
        sleeper(min(poll_seconds, max(0, deadline - clock())))


def finalize_source_delivery_evidence(
    provisional: dict, ci: dict, *, pr_confirmed: bool
) -> tuple[dict, bool]:
    """Distinguish verified code edit from independently accepted delivery.

    A draft PR, published commit, or in-progress workflow does not make a
    source repair complete. Keep the pending/failed gate in sealed checkpoints.
    """
    if (not isinstance(provisional, dict) or not isinstance(ci, dict)
            or type(pr_confirmed) is not bool
            or ci.get("status") not in {"pending", "failed", "passed"}):
        raise StudioError("Target source delivery evidence invalid")
    validated = dict(provisional)
    complete = pr_confirmed and ci["status"] == "passed"
    validated["source_validation"] = "passed"
    validated["target_ci"] = ci["status"]
    validated["status"] = (
        "passed" if complete else
        "failed" if ci["status"] == "failed" else
        "pending"
    )
    validated["passed"] = complete
    validated.pop("target_ci_run_id", None)
    if type(ci.get("run_id")) is int and ci["run_id"] > 0:
        validated["target_ci_run_id"] = ci["run_id"]
    return validated, complete
