"""Resume explicitly selected failed managed objectives through operator controls."""
import argparse
import json
import os
import re
import urllib.request
from pathlib import Path

from core import API, canonical


INSTRUCTION = (
    "Continue the existing final goal after the Production-OS worker fixes: "
    "the optional skill_learning contract is supported, the pinned Git baseline "
    "is forwarded, and configured AI providers have passed live inference checks. "
    "Inspect the existing repository and prior evidence, fix the remaining issues, "
    "run the relevant validation, and report real artifacts and blockers."
)


class OperatorClient(API):
    def get(self, path, *, timeout_seconds=30):
        return self.call("GET", path, timeout_seconds=timeout_seconds)

    def continue_project(self, project_id):
        return self.submit("/v1/managed-projects/" + project_id + "/instructions", {"instruction": INSTRUCTION})

    def launch(self, workflow_id, repository, final_goal):
        return self.submit("/v1/dashboard/launch", {
            "repository": repository, "instruction": final_goal,
            "request_id": "worker-recovery-" + workflow_id,
        })

    def submit(self, path, payload):
        request = urllib.request.Request(
            self.base + path,
            method="POST", data=canonical(payload).encode("utf-8"),
            headers={"Authorization": "Bearer " + self.key, "Content-Type": "application/json",
                     "Accept": "application/json"})
        # One submission only: an uncertain mutation response must never be retried here.
        return self._response(request, timeout_seconds=30)


def recover_legacy(client, workflow_id, projects, *, apply):
    record = {"workflow_id": workflow_id, "status": "not_current"}
    # A previous generation of a managed objective must not become a new project.
    if any(run.get("workflow_id") == workflow_id for project in projects for run in project.get("runs", [])):
        return record
    workflow = client.get("/v1/workflows/" + workflow_id).get("workflow", {})
    if workflow.get("status") != "failed":
        return record
    tasks = workflow.get("tasks") or []
    if len(tasks) != 1 or tasks[0].get("status") != "failed":
        record["status"] = "unsupported_legacy_workflow"
        return record
    payload = tasks[0].get("payload") or {}
    handoff = payload.get("handoff") or {}
    if payload.get("managed_project_id") or handoff.get("managed_project_id"):
        return record
    repository = workflow.get("repository")
    final_goal = handoff.get("final_goal") or handoff.get("task")
    if (not isinstance(repository, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository)
            or not isinstance(final_goal, str) or not 1 <= len(final_goal.strip()) <= 24000):
        record["status"] = "legacy_goal_missing"
        return record
    if any(p.get("repository") == repository and p.get("final_goal") == final_goal for p in projects):
        record["status"] = "already_managed"
        return record
    record["status"] = "legacy_eligible"
    if apply:
        response = client.launch(workflow_id, repository, final_goal)
        project = response.get("project", {})
        record.update(status="relaunched", project_id=project.get("project_id"),
                      new_workflow_id=project.get("current_workflow_id"))
        projects.append(project)
    return record


def resume(client, workflow_ids, *, apply=False):
    if (not isinstance(workflow_ids, list) or not 1 <= len(workflow_ids) <= 5
            or any(not isinstance(x, str) or not re.fullmatch(r"[a-f0-9]{32}", x) for x in workflow_ids)
            or len(set(workflow_ids)) != len(workflow_ids)):
        raise ValueError("Expected one to five distinct failed workflow IDs")
    projects = client.get("/v1/managed-projects").get("projects", [])
    outcomes = []
    for workflow_id in workflow_ids:
        matches = [p for p in projects if p.get("current_workflow_id") == workflow_id]
        if len(matches) != 1:
            outcomes.append(recover_legacy(client, workflow_id, projects, apply=apply))
            continue
        project_id = str(matches[0].get("project_id") or "")
        if not re.fullmatch(r"[a-f0-9]{32}", project_id):
            raise ValueError("Invalid managed project ID")
        # Re-read immediately before mutation to avoid resuming stale list entries.
        current = client.get("/v1/managed-projects/" + project_id).get("project", {})
        workflow = current.get("current_workflow") or {}
        record = {"workflow_id": workflow_id, "project_id": project_id, "status": "skipped"}
        if (current.get("current_workflow_id") != workflow_id
                or current.get("status") != "NEEDS_ATTENTION" or workflow.get("status") != "failed"):
            outcomes.append(record)
            continue
        record["status"] = "eligible"
        if apply:
            response = client.continue_project(project_id)
            updated = response.get("project", {})
            record["status"] = "resumed"
            record["new_workflow_id"] = updated.get("current_workflow_id")
        outcomes.append(record)
    return {"applied": apply, "objectives": outcomes}


def retry_existing_jobs(client, entries, *, apply=False):
    """Retry an exact failed task without changing its checkpoint identity."""
    if (not isinstance(entries, list) or not 1 <= len(entries) <= 5
            or any(not isinstance(e, dict) or set(e) != {"workflow_id", "job_key"}
                   or not re.fullmatch(r"[a-f0-9]{32}", str(e.get("workflow_id") or ""))
                   or not re.fullmatch(r"[a-f0-9]{24}", str(e.get("job_key") or "")) for e in entries)
            or len({e["job_key"] for e in entries}) != len(entries)):
        raise ValueError("Expected distinct exact failed jobs")
    outcomes = []
    for entry in entries:
        job = client.get("/v1/jobs/" + entry["job_key"]).get("job", {})
        payload = job.get("payload") or {}
        if payload.get("workflow_id") != entry["workflow_id"]:
            raise ValueError("Recovery job/workflow mismatch")
        workflow = client.get("/v1/workflows/" + entry["workflow_id"]).get("workflow", {})
        tasks = [t for t in workflow.get("tasks", []) if t.get("task_id") == payload.get("workflow_task_id")]
        record = {**entry, "status": "not_eligible"}
        if (job.get("status") == "failed" and workflow.get("status") == "failed"
                and len(tasks) == 1 and tasks[0].get("status") == "failed"
                and type(payload.get("workflow_attempt")) is int
                and tasks[0].get("attempts") == payload["workflow_attempt"]
                and tasks[0]["attempts"] < tasks[0].get("max_attempts", 0)):
            record["status"] = "eligible"
            if apply:
                response = client.submit("/v1/dashboard/workers/github-actions-worker/control",
                                         {"action": "retry", "job_key": entry["job_key"]})
                if response.get("accepted") is not True or response.get("workflow_id") != entry["workflow_id"]:
                    raise RuntimeError("Exact task retry receipt unverified")
                record["status"] = "retried"
        outcomes.append(record)
    return {"applied": apply, "objectives": outcomes}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("control", type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    try:
        control = json.loads(args.control.read_text())
        token = os.environ.get("PRODUCTION_OS_OPERATOR_TOKEN", "").strip()
        if not token:
            raise ValueError("Operator secret missing")
        client = OperatorClient(os.environ["PRODUCTION_OS_URL"], token)
        from production_os_worker_canary import wait_for_readiness
        wait_for_readiness(client)
        if "retry_jobs" in control:
            if "failed_workflow_ids" in control:
                raise ValueError("Choose one recovery mode")
            result = retry_existing_jobs(client, control["retry_jobs"], apply=args.apply)
        else:
            result = resume(client, control["failed_workflow_ids"], apply=args.apply)
    except Exception as exc:
        print(canonical({"status": "unavailable", "error_type": type(exc).__name__}))
        return 1
    print("Production-OS objective recovery: " + canonical(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
