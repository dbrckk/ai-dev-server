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
    def get(self, path):
        return self.call("GET", path, timeout_seconds=30)

    def continue_project(self, project_id):
        request = urllib.request.Request(
            self.base + "/v1/managed-projects/" + project_id + "/instructions",
            method="POST", data=canonical({"instruction": INSTRUCTION}).encode("utf-8"),
            headers={"Authorization": "Bearer " + self.key, "Content-Type": "application/json",
                     "Accept": "application/json"})
        # One submission only: an uncertain mutation response must never be retried here.
        return self._response(request, timeout_seconds=30)


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
            outcomes.append({"workflow_id": workflow_id, "status": "not_current"})
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
        result = resume(OperatorClient(os.environ["PRODUCTION_OS_URL"], token),
                        control["failed_workflow_ids"], apply=args.apply)
    except Exception as exc:
        print(canonical({"status": "unavailable", "error_type": type(exc).__name__}))
        return 1
    print("Production-OS objective recovery: " + canonical(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
