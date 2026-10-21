"""Launch and verify a bounded live Production-OS worker canary."""
import argparse
import base64
import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

from core import API, APIError, StudioError, NoRedirect, canonical
from production_os_resume_objectives import OperatorClient
from production_os_source_tasks import TASKS, instruction as source_instruction


_REPOSITORY = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")
_WORKFLOW_ID = re.compile(r"[a-f0-9]{32}")
_TERMINAL_FAILURES = {"failed", "cancelled", "canceled"}


def dispatch_worker_after_enqueue(*, token, repository, urlopen=None):
    """Dispatch the restricted same-repository worker after the task is queued.

    GitHub grants this canary workflow only actions:write and contents:read.
    Never accept a user-provided repository or workflow name for dispatch.
    The 204 only confirms dispatch acceptance, not worker task completion.
    """
    if repository != "dbrckk/ai-dev-server":
        raise ValueError("Canary workflow repository does not match trusted worker")
    if not token:
        raise ValueError("Canary workflow Actions token is missing")
    request = urllib.request.Request(
        "https://api.github.com/repos/dbrckk/ai-dev-server/actions/workflows/"
        "production-os-actions-worker.yml/dispatches",
        data=json.dumps({"ref": "main"}).encode("utf-8"),
        method="POST",
        headers={
            "Authorization": "Bearer " + token,
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "production-os-worker-canary",
        },
    )
    # Never follow redirects when sending the GitHub Actions bearer token.
    # Keep injectable transport for the existing isolated canary checks.
    if urlopen is None:
        urlopen = urllib.request.build_opener(NoRedirect()).open
    try:
        with urlopen(request, timeout=20) as response:
            if response.status != 204:
                raise RuntimeError("GitHub Actions worker dispatch returned unexpected status")
    except urllib.error.HTTPError as exc:
        raise RuntimeError(
            f"GitHub Actions worker dispatch rejected: HTTP {exc.code}"
        ) from None
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError("GitHub Actions worker dispatch unavailable") from None
    return "accepted"


def validate_control(payload):
    if not isinstance(payload, dict):
        raise ValueError("canary control must be an object")
    if set(payload) not in ({"sequence", "repository"}, {"sequence", "repository", "scenario"},
                        {"sequence", "repository", "scenario", "task_id"}):
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
    scenario = payload.get("scenario", "file")
    if not isinstance(scenario, str) or scenario not in {"file", "jumpy_landing_feedback", "jumpy_settings_tap_guard", "jumpy_share_clipboard_guard", "approved_source_repair"}:
        raise ValueError("canary scenario is invalid")
    if scenario in {"jumpy_landing_feedback", "jumpy_settings_tap_guard", "jumpy_share_clipboard_guard"} and repository != "dbrckk/Jumpy":
        raise ValueError("gameplay scenario requires the trusted Jumpy repository")
    if scenario == "approved_source_repair":
        task_id = payload.get("task_id")
        if not isinstance(task_id, str) or task_id not in TASKS or TASKS[task_id].repo != repository:
            raise ValueError("source repair task/repository is not approved")
    elif "task_id" in payload:
        raise ValueError("task_id requires approved_source_repair")
    return sequence, repository


def canary_instruction(sequence, scenario="file", task_id=None):
    if scenario == "approved_source_repair":
        if not isinstance(task_id, str) or task_id not in TASKS:
            raise ValueError("unknown source repair task")
        return source_instruction(sequence, task_id)
    if scenario == "jumpy_share_clipboard_guard":
        return (
            f"Production-OS verified Jumpy source qualification {sequence}. "
            "Fix ONE observable Android/share reliability defect in "
            "scripts/integrations.gd, in existing share_score(): the current "
            "unconditional DisplayServer.clipboard_set(text) is unsafe when "
            "DisplayServer.FEATURE_CLIPBOARD is unsupported. Check the capability "
            "before writing to the clipboard; on unsupported devices exit "
            "gracefully with a concise share_unavailable event instead of "
            "pretending copying worked. Preserve the existing share text, "
            "supported-device behavior, and share_score analytics. "
            "Change ONLY scripts/integrations.gd. Do not create marker files, "
            "tests, documentation, SDK dependencies, permissions, workflows "
            "or monetization changes. This must be a useful source-code edit, "
            "not a deterministic canary. Verify the real Godot 4.7.2 headless "
            "project import and input smoke, then persist a reviewed branch "
            "and draft pull request; do not merge or publish Jumpy. "
            "Report model capacity/CI failure accurately."
        )
    if scenario == "jumpy_settings_tap_guard":
        return (
            f"Production-OS verified autonomous Jumpy code-change qualification {sequence}. "
            "Fix ONE real interface bug in scripts/main.gd: when the READY screen's "
            "Settings panel is open (settings_open == true), tapping empty space "
            "currently starts a game via _unhandled_input. Prevent that accidental "
            "tap-to-start while the settings panel is open. Keep the BACK button "
            "working, preserve all settings toggles and allow normal tap-to-start "
            "from the main READY menu. Leave the PLAYING and DEAD input branches, "
            "all physics, scoring, daily seed, Profile data, and UI layout unchanged. "
            "Implement the minimal guarded condition in existing Godot 4.7 GDScript; "
            "do not generate a marker, canary text file or documentation-only change. "
            "Do not change tests, dependencies, workflows, secrets or monetization. "
            "Use actual Godot 4.7.2 headless parse validation and persist the modified "
            "source in a review branch/pull request after verification. Never merge "
            "or publish Jumpy; report failure truthfully if model capacity is insufficient."
        )
    if scenario == "jumpy_landing_feedback":
        return (
            f"Production-OS verified Jumpy gameplay qualification {sequence}. "
            "Make ONE real gameplay-UX improvement in scripts/main.gd: add a short-lived, "
            "clearly readable on-screen landing judgement for PERFECT and CLUTCH landings, "
            "and a calmer ordinary-landing cue if useful. Trigger the cue only on a newly "
            "scored landing, expire it automatically, and hide it on reset/death. "
            "Place it away from score/buttons and keep it legible on phone portrait screens. "
            "Respect reduced_motion and high_contrast settings without requiring animation. "
            "Preserve exact existing gameplay scoring, jump and pulse physics, daily seed, "
            "save data and player input. Keep the patch small and avoid new dependencies, "
            "secrets, workflows, monetization or external SDKs. Do NOT create a canary text "
            "file: this trial must modify actual source code. Use the existing Godot 4.7.2 "
            "headless project validation, fix any parse errors, then persist a verified "
            "review-branch checkpoint. Do not merge or publish the game."
        )
    if scenario != "file":
        raise ValueError("unknown canary scenario")
    path = f".production-os/worker-canary-{sequence}.txt"
    content = f"production-os-worker-canary sequence {sequence}"
    return (
        f"Production-OS worker canary {sequence}. Make exactly one intentional product-file change: "
        f"create {path} containing exactly one line: {content}. "
        "Do not change dependencies, workflows, secrets, configuration, or existing source files. "
        "Verify the file content, persist the normal autonomous checkpoint branch, and finish the task successfully."
    )


def source_canary_preflight(control, *, api=None):
    """Reject obsolete source objectives before any queue mutation or inference.

    This is a conservative applicability check, not a claim of product success.
    Marker-only canaries keep their existing path and need no source request.
    """
    _, repository = validate_control(control)
    scenario = control.get("scenario", "file")
    if scenario == "file":
        return None
    if api is None:
        api = API("https://api.github.com", os.environ.get("PRODUCTION_OS_CANARY_DISPATCH_TOKEN", ""))
    if scenario == "approved_source_repair":
        task = TASKS[control["task_id"]]
        path = task.path
    else:
        path = ("scripts/integrations.gd" if scenario == "jumpy_share_clipboard_guard"
                else "scripts/main.gd")
    response = api.call(
        "GET", "/repos/" + repository + "/contents/" + path + "?ref=main",
        timeout_seconds=15, max_attempts=1,
    )
    if (not isinstance(response, dict) or response.get("type") != "file"
            or response.get("encoding") != "base64"
            or not isinstance(response.get("content"), str)
            or not re.fullmatch(r"[a-f0-9]{40}", str(response.get("sha") or ""))
            or len(response["content"]) > 600_000):
        raise RuntimeError("Canary source preflight returned invalid content")
    source = base64.b64decode("".join(response["content"].split()), validate=True).decode("utf-8")
    if scenario == "approved_source_repair":
        applicable = source.count(task.old_line + "\n") == 1
    elif scenario == "jumpy_share_clipboard_guard":
        function = re.search(r"(?ms)^func share_score\([^\n]*\n(.*?)(?=^func |\Z)", source)
        applicable = bool(
            function
            and "DisplayServer.clipboard_set(text)" in function.group(1)
            and "DisplayServer.has_feature(" not in function.group(1)
        )
    elif scenario == "jumpy_settings_tap_guard":
        function = re.search(r"(?ms)^func _unhandled_input\([^\n]*\n(.*?)(?=^func |\Z)", source)
        applicable = bool(function and re.search(
            r'(?m)^\tif state == "READY":\n\t\tstart_run\(\)', function.group(1),
        ) and "settings_open" not in function.group(1))
    else:
        # Existing cue machinery makes the old additive task ambiguous. Select
        # a fresh verified objective instead of spending another 60k envelope.
        applicable = ("func show_landing_cue(" not in source
                      and "ui.landing" not in source
                      and 'judgement = "PERFECT"' in source
                      and 'judgement = "CLUTCH"' in source)
    return {"status": "applicable" if applicable else "scenario_no_longer_applicable",
            "source_blob_sha": response["sha"], "path": path}


def launch_canary(client, control, *, source_api=None):
    sequence, repository = validate_control(control)
    scenario = control.get("scenario", "file")
    preflight = source_canary_preflight(control, api=source_api)
    if preflight is not None and preflight["status"] != "applicable":
        return {"sequence": sequence, "scenario": scenario, "repository": repository,
                "source_preflight": preflight,
                "result": {"status": "blocked", "reason": "scenario_no_longer_applicable"},
                "succeeded": False}
    payload = {
        "repository": repository,
        "instruction": canary_instruction(sequence, scenario, control.get("task_id")),
        "request_id": f"worker-canary-{sequence}",
    }
    if scenario in {"jumpy_landing_feedback", "jumpy_settings_tap_guard", "jumpy_share_clipboard_guard", "approved_source_repair"}:
        # Actual gameplay changes need several planning, coding and validation
        # calls. The historical 30k one-tap default has failed before any
        # implementation; use the existing operator-only bounded profile.
        # This is a consumption ceiling, not additional paid provider access.
        payload.update({
            "launch_profile": "portfolio-integration",
            "token_budget": 60000,
        })
    response = client.submit("/v1/dashboard/launch", payload)
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
        "scenario": scenario,
        "repository": repository,
        "project_id": project_id,
        "workflow_id": workflow_id,
        "worker_wake": wake_status,
        **({"source_preflight": preflight} if preflight is not None else {}),
    }


def _polling_parameters(timeout_seconds, poll_seconds):
    timeout = float(timeout_seconds)
    poll = float(poll_seconds)
    if not 0 <= timeout <= 7200:
        raise ValueError("timeout must be between 0 and 7200 seconds")
    if not 1 <= poll <= 60:
        raise ValueError("poll interval must be between 1 and 60 seconds")
    return timeout, poll


def wait_for_workflow(client, workflow_id, *, timeout_seconds, poll_seconds=10.0,
                      clock=time.monotonic, sleeper=time.sleep):
    if not _WORKFLOW_ID.fullmatch(str(workflow_id or "")):
        raise ValueError("workflow id is invalid")
    timeout, poll = _polling_parameters(timeout_seconds, poll_seconds)
    deadline = float(clock()) + timeout
    last_status = "unknown"
    while True:
        remaining = deadline - float(clock())
        # API.call has a one-second minimum transport timeout. Do not start
        # another read when the remaining budget cannot contain that request.
        if remaining < 1:
            return {"status": "timed_out", "last_status": last_status}
        try:
            payload = client.get("/v1/workflows/" + workflow_id,
                                 timeout_seconds=min(30.0, remaining))
        except APIError as exc:
            if exc.status not in {502, 503, 504}:
                raise
        except StudioError as exc:
            if str(exc) != "API unavailable or timed out":
                raise
        except (TimeoutError, ConnectionError, urllib.error.URLError):
            pass
        else:
            workflow = payload.get("workflow") if isinstance(payload, dict) else None
            if not isinstance(workflow, dict):
                raise RuntimeError("canary workflow lookup returned invalid response")
            last_status = str(workflow.get("status") or "unknown").lower()
            if last_status == "succeeded":
                return {"status": "succeeded"}
            if last_status in _TERMINAL_FAILURES:
                return {"status": last_status}
        remaining = deadline - float(clock())
        if remaining <= 0:
            return {"status": "timed_out", "last_status": last_status}
        sleeper(min(poll, remaining))



def wait_for_readiness(client, *, timeout_seconds=180.0, poll_seconds=5.0,
                       clock=time.monotonic, sleeper=time.sleep):
    """Warm the Render service using *only GET* before the one-shot POST.

    A free Render instance may take longer than the 30-second operator POST
    timeout to start. Never retry an ambiguous mutation response: the
    dashboard launch is idempotent by request_id, but this probe deliberately
    uses read-only requests and leaves the actual submission exactly once.
    """
    timeout, poll = _polling_parameters(timeout_seconds, poll_seconds)
    deadline = float(clock()) + timeout
    while True:
        remaining = deadline - float(clock())
        if remaining < 1:
            raise TimeoutError("Production-OS did not become ready")
        try:
            response = client.get("/readyz", timeout_seconds=min(30.0, remaining))
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
        sleeper(min(poll, remaining))


def run_canary(client, control, *, wait_seconds=0, poll_seconds=10.0,
               clock=time.monotonic, sleeper=time.sleep, dispatch=None, source_api=None):
    # Invalid monitoring parameters must not leave a real task queued.
    wait_seconds, poll_seconds = _polling_parameters(wait_seconds, poll_seconds)
    result = launch_canary(client, control, source_api=source_api)
    if result.get("result", {}).get("status") == "blocked":
        return result
    if dispatch is not None:
        # The control plane may have dispatched the same Actions worker while
        # admitting the job. Only use the canary's privileged dispatch when
        # that wake did not happen and no persistent worker is available.
        wake = result["worker_wake"]
        if wake == "dispatched":
            result["actions_worker_wake"] = "already_dispatched"
        elif wake == "not_needed":
            result["actions_worker_wake"] = "not_needed"
        else:
            result["actions_worker_wake"] = dispatch()
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
        # An acknowledged submission is not terminal worker success.
        # Preserve the distinction for status consumers and CI receipts.
        result["result"] = {"status": "launched"}
        result["succeeded"] = None
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
        dispatch = None
        if os.environ.get("GITHUB_ACTIONS") == "true":
            dispatch = lambda: dispatch_worker_after_enqueue(
                token=os.environ.get("PRODUCTION_OS_CANARY_DISPATCH_TOKEN", "").strip(),
                repository=os.environ.get("GITHUB_REPOSITORY", ""),
            )
        result = run_canary(
            client,
            control,
            wait_seconds=args.wait_seconds,
            poll_seconds=args.poll_seconds,
            dispatch=dispatch,
        )
    except Exception as exc:
        print(canonical({"status": "unavailable", "error_type": type(exc).__name__}))
        return 1
    print("Production-OS worker canary: " + canonical(result))
    # A non-blocking CLI launch can exit successfully without claiming
    # the workflow actually finished. Blocking mode still requires success.
    launched_only = result.get("result", {}).get("status") == "launched"
    return 0 if result.get("succeeded") is True or launched_only else 1


if __name__ == "__main__":
    raise SystemExit(main())
