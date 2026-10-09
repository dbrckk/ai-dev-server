"""Launch and verify a bounded live Production-OS worker canary."""
import argparse
import json
import os
import re
import time
import urllib.error
from pathlib import Path

from core import APIError, StudioError, canonical
from production_os_resume_objectives import OperatorClient


_REPOSITORY = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")
_WORKFLOW_ID = re.compile(r"[a-f0-9]{32}")
_TERMINAL_FAILURES = {"failed", "cancelled", "canceled"}


def validate_control(payload):
    if not isinstance(payload, dict):
        raise ValueError("canary control must be an object")
    if set(payload) != {"sequence", "repository"}:
        raise ValueError("canary control fields are invalid")
    sequence = payload.get("sequence")
    if isinstance(sequence, bool) or not isinstance(sequence, int) or not 1 <= sequence <= 1_000_000_000:
        raise ValueError("canary sequence must be an integer between 1 and 1000000000")
    repository = payload.get("repository")
    if not isinstance(repository, str) or not _REPOSITORY.fullmatch(repository):
        raise ValueError("canary repository is invalid")
    owner, name = repository.split("/", 1)
    if owner in {".", ".."} or name in {".", ".."}:
        raise ValueError("canary repository is invalid")
    return sequence, repository


def canary_instruction(sequence):
    path = f".production-os/worker-canary-{sequence}.txt"
    content = f"production-os-worker-canary sequence {sequence}"
    return (
        f"Production-OS worker canary {sequence}. Make exactly one intentional product-file change: "
        f"create {path} containing exactly one line: {content}. "
        "Do not change dependencies, workflows, secrets, configuration, or existing source files. "
        "Verify the file content, persist the normal autonomous checkpoint branch, and finish the task successfully."
    )


def launch_canary(client, control):
    sequence, repository = validate_control(control)
    response = client.submit(
        "/v1/dashboard/launch",
        {
            "repository": repository,
            "instruction": canary_instruction(sequence),
            "request_id": f"worker-canary-{sequence}",
        },
    )
    if not isinstance(response, dict):
        raise RuntimeError("canary launch returned invalid response")
    project = response.get("project")
    if not isinstance(project, dict):
        raise RuntimeError("canary launch returned no project")
    workflow_id = str(project.get("current_workflow_id") or "")
    project_id = str(project.get("project_id") or "")
    if not _WORKFLOW_ID.fullmatch(workflow_id):
        raise RuntimeError("canary launch returned invalid workflow id")
    if not _WORKFLOW_ID.fullmatch(project_id):
        raise RuntimeError("canary launch returned invalid project id")
    wake = response.get("launch")
    wake = wake.get("worker_wake") if isinstance(wake, dict) else None
    wake_status = str(wake.get("status") or "unknown") if isinstance(wake, dict) else "unknown"
    return {
        "sequence": sequence,
        "repository": repository,
        "project_id": project_id,
        "workflow_id": workflow_id,
        "worker_wake": wake_status,
    }


def wait_for_workflow(client, workflow_id, *, timeout_seconds, poll_seconds=10.0,
                      clock=time.monotonic, sleeper=time.sleep):
    if not _WORKFLOW_ID.fullmatch(str(workflow_id or "")):
        raise ValueError("workflow id is invalid")
    timeout = float(timeout_seconds)
    poll = float(poll_seconds)
    if not 0 <= timeout <= 7200:
        raise ValueError("timeout must be between 0 and 7200 seconds")
    if not 1 <= poll <= 60:
        raise ValueError("poll interval must be between 1 and 60 seconds")
    deadline = float(clock()) + timeout
    last_status = "unknown"
    while True:
        payload = client.get("/v1/workflows/" + workflow_id)
        workflow = payload.get("workflow") if isinstance(payload, dict) else None
        if not isinstance(workflow, dict):
            raise RuntimeError("canary workflow lookup returned invalid response")
        last_status = str(workflow.get("status") or "unknown").lower()
        if last_status == "succeeded":
            return {"status": "succeeded"}
        if last_status in _TERMINAL_FAILURES:
            return {"status": last_status}
        if float(clock()) >= deadline:
            return {"status": "timed_out", "last_status": last_status}
        sleeper(min(poll, max(0.0, deadline - float(clock()))))



def wait_for_readiness(client, *, timeout_seconds=180.0, poll_seconds=5.0,
                       clock=time.monotonic, sleeper=time.sleep):
    """Warm the Render service using *only GET* before the one-shot POST.

    A free Render instance may take longer than the 30-second operator POST
    timeout to start. Never retry an ambiguous mutation response: the
    dashboard launch is idempotent by request_id, but this probe deliberately
    uses read-only requests and leaves the actual submission exactly once.
    """
    deadline = float(clock()) + max(0.0, float(timeout_seconds))
    while True:
        try:
            response = client.get("/readyz")
            if isinstance(response, dict) and response.get("status") == "ready":
                return
            if not isinstance(response, dict) or response.get("status") != "not_ready":
                raise RuntimeError("Production-OS readiness returned invalid response")
        except APIError as exc:
            if exc.status not in {502, 503, 504}:
                raise
        except StudioError as exc:
            if str(exc) != "API unavailable or timed out":
                raise
        except (TimeoutError, ConnectionError, urllib.error.URLError):
            pass
        remaining = deadline - float(clock())
        if remaining <= 0:
            raise TimeoutError("Production-OS did not become ready")
        sleeper(min(max(1.0, float(poll_seconds)), remaining))


def run_canary(client, control, *, wait_seconds=0, poll_seconds=10.0,
               clock=time.monotonic, sleeper=time.sleep):
    result = launch_canary(client, control)
    if wait_seconds:
        outcome = wait_for_workflow(
            client,
            result["workflow_id"],
            timeout_seconds=wait_seconds,
            poll_seconds=poll_seconds,
            clock=clock,
            sleeper=sleeper,
        )
        result["result"] = outcome
        result["succeeded"] = outcome.get("status") == "succeeded"
    else:
        result["result"] = {"status": "launched"}
        result["succeeded"] = True
    return result


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("control", type=Path)
    parser.add_argument("--wait-seconds", type=float, default=0)
    parser.add_argument("--poll-seconds", type=float, default=10)
    args = parser.parse_args(argv)
    try:
        control = json.loads(args.control.read_text(encoding="utf-8"))
        token = os.environ.get("PRODUCTION_OS_OPERATOR_TOKEN", "").strip()
        base = os.environ.get("PRODUCTION_OS_URL", "").strip()
        if not token:
            raise ValueError("Operator secret missing")
        if not base:
            raise ValueError("Production-OS URL missing")
        client = OperatorClient(base, token)
        wait_for_readiness(client)
        result = run_canary(
            client,
            control,
            wait_seconds=args.wait_seconds,
            poll_seconds=args.poll_seconds,
        )
    except Exception as exc:
        print(canonical({"status": "unavailable", "error_type": type(exc).__name__}))
        return 1
    print("Production-OS worker canary: " + canonical(result))
    return 0 if result.get("succeeded") else 1


if __name__ == "__main__":
    raise SystemExit(main())
