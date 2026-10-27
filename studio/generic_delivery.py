"""Resume managed review delivery after implementation, without another model call."""
from pathlib import Path
from copy import deepcopy
import time

from core import APIError, StudioError, canonical
from execution_checkpoint import advance, save
from source_delivery_checkpoint import request_fingerprint, SourceCheckpointError
from generic_target_ci import inspect as inspect_ci, dispatch as dispatch_ci


def _fingerprint(request: dict) -> str:
    objective = (request.get("production_os") or {}).get("objective_sha256")
    return request_fingerprint({**request, "brief": objective}) if objective else request_fingerprint(request)


def resumable(checkpoint: dict, request: dict, commit_sha: str) -> bool:
    verification = checkpoint.get("last_verification") or {}
    receipt = verification.get("managed_review_delivery")
    if receipt is None:
        return False
    if (not isinstance(receipt, dict)
            or checkpoint.get("project_id") != request["id"]
            or checkpoint.get("engine") != "generic"
            or checkpoint.get("phase") not in {"published", "complete"}
            or checkpoint.get("base_sha") != commit_sha
            or (verification.get("passed") is not True and receipt.get("repair_required") is not True)
            or receipt.get("implementation_complete") is not True
            or receipt.get("request_fingerprint") != _fingerprint(request)):
        raise SourceCheckpointError("Managed review delivery checkpoint identity changed")
    return receipt.get("repair_required") is not True


def deliver(request: dict, repo, checkpoint: dict, state: dict, out: Path,
            observer=None) -> dict:
    sha = checkpoint["base_sha"]
    verification = dict(checkpoint.get("last_verification") or {})
    if verification.get("passed") is not True:
        raise StudioError("Managed review delivery requires verified implementation")
    previous = verification.get("managed_review_delivery") or {}
    changed = previous.get("changed_files", [])
    if state.get("rounds"):
        changed = sorted({name for row in state["rounds"] if isinstance(row, dict)
                          for name in row.get("changed_files", []) if isinstance(name, str)})[:100]
    verification["managed_review_delivery"] = {
        "request_fingerprint": _fingerprint(request),
        "implementation_complete": True,
        "changed_files": changed,
        "review_wait_started": previous.get("review_wait_started", previous.get("ci_wait_started", time.time())),
        "review_handoff_attempted": previous.get("review_handoff_attempted", False),
        "review_confirmed": previous.get("review_confirmed", False),
        "ci_wait_started": previous.get("ci_wait_started") if previous.get("review_confirmed") else None,
        "ci_dispatch_attempted": previous.get("ci_dispatch_attempted", False),
    }
    checkpoint = advance(checkpoint, phase="published", last_verification=deepcopy(verification))
    path = out / ".autonomy/generic-execution-checkpoint.json"
    # Persist before contacting GitHub: a failed POST must not erase completed work.
    save(path, checkpoint)
    if observer is not None:
        observer(dict(checkpoint))
    pr_error = None
    receipt = verification["managed_review_delivery"]
    try:
        pr = repo.ensure_pull_request(
            title="Autonomous managed project: " + str(request.get("app_name") or request["id"]),
            body="Verified implementation checkpoint. Review independent checks before merging.",
            expected_sha=sha,
        )
    except StudioError as exc:
        denied = any(marker in str(exc) for marker in ("HTTP 401", "HTTP 403"))
        pr = None
        if denied:
            if not receipt["review_handoff_attempted"]:
                receipt["review_handoff_attempted"] = True
                receipt["review_wait_started"] = time.time()
                checkpoint = advance(checkpoint, last_verification=deepcopy(verification))
                save(path, checkpoint)
                if observer is not None:
                    observer(dict(checkpoint))
                handoff = repo.request_trusted_review_handoff(sha)
                outcome = handoff.get("status") if isinstance(handoff, dict) else "invalid_response"
                if outcome == "accepted":
                    pr = repo.await_trusted_review(sha)
                elif outcome != "unavailable":
                    receipt["review_handoff_attempted"] = False
                    pr_error = "review_handoff_" + str(outcome)
            # An ambiguous POST is observed through ensure_pull_request on
            # subsequent resumes; never redispatch it automatically.
        elif not ((isinstance(exc, APIError) and exc.status in {408, 429, 500, 502, 503, 504})
                  or str(exc) == "API unavailable or timed out"):
            pr_error = "review_creation_unavailable"
    confirmed = (isinstance(pr, dict) and type(pr.get("number")) is int
                 and pr["number"] > 0 and pr.get("state") == "open"
                 and pr.get("url") == f"https://github.com/{request['target_repo']}/pull/{pr['number']}")
    ci = {"status": "unavailable" if pr_error else "pending", "reason": pr_error or "review_pr_not_confirmed"}
    if not confirmed and not pr_error and time.time() - receipt["review_wait_started"] > 3600:
        ci = {"status": "unavailable", "reason": "review_handoff_wait_expired"}
    if confirmed:
        receipt["review_confirmed"] = True
        if receipt["ci_wait_started"] is None:
            receipt["ci_wait_started"] = time.time()
        try:
            ci = inspect_ci(repo, sha)
        except StudioError as exc:
            transient = ((isinstance(exc, APIError) and exc.status in {408, 429, 500, 502, 503, 504})
                         or str(exc) == "API unavailable or timed out")
            ci = {"status": "pending" if transient else "unavailable",
                  "reason": "independent_CI_temporarily_unavailable" if transient else "independent_CI_evidence_unavailable"}
        receipt = verification["managed_review_delivery"]
        if ci.get("reason") == "exact_commit_ci_not_started" and not receipt["ci_dispatch_attempted"]:
            # Seal intent first. Never replay an ambiguous mutation on restart.
            receipt["ci_dispatch_attempted"] = True
            checkpoint = advance(checkpoint, last_verification=deepcopy(verification))
            save(path, checkpoint)
            if observer is not None:
                observer(dict(checkpoint))
            dispatch = dispatch_ci(repo, ci["workflow_id"])
            if dispatch["status"] == "unavailable":
                receipt["ci_dispatch_attempted"] = False
                ci = {**ci, "status": "unavailable", "reason": dispatch["reason"]}
        if ci.get("status") == "pending" and time.time() - receipt["ci_wait_started"] > 3600:
            ci = {**ci, "status": "unavailable", "reason": "independent_CI_wait_expired"}
        if ci.get("status") == "passed" and repo._find_open_pull_request(expected_sha=sha) is None:
            ci = {**ci, "status": "pending", "reason": "review_commit_changed_during_CI"}
    complete = confirmed and ci.get("status") == "passed"
    repair = ci.get("status") == "failed"
    verification["independent_ci"] = ci
    if repair:
        verification["passed"] = False
        verification["managed_review_delivery"]["repair_required"] = True
    checkpoint = advance(checkpoint, phase="complete" if complete else "published", last_verification=verification)
    save(path, checkpoint)
    if observer is not None:
        observer(dict(checkpoint))
    status = ("complete" if complete else "blocked" if repair else
              "human_action_required" if ci.get("status") == "unavailable" else "deferred")
    next_stage = (None if complete else "generic_ci_repair" if repair else
                  "independent_target_ci" if confirmed else "review_handoff")
    blockers = [] if complete else [ci["reason"]]
    report = {
        **state, "engine": "generic", "target_repo": request["target_repo"],
        "rounds": state.get("rounds") or [{"round": checkpoint["round"],
                                          "changed_files": changed, "verification": verification}],
        "status": status, "checkpoint_commit": sha,
        "verification": verification,
        "ci": ci,
        "pull_request": pr if confirmed else {"state": "unavailable", "reason": "review_commit_unverified"},
        "resume_mode": "managed_generic_review_delivery",
        "execution_checkpoint": {key: checkpoint[key] for key in ("round", "phase", "base_sha")},
        "completion": {"finished": complete, "next_stage": next_stage, "blockers": blockers},
        "release_status": "source_review_pending_human_approval" if complete else "verified_branch_review_blocked",
        "blockers": blockers,
    }
    (out / "generic-report.json").write_text(canonical(report), encoding="utf-8")
    return {"status": status, "report": report, "next_stage": next_stage}
