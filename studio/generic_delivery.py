"""Resume managed review delivery after implementation, without another model call."""
from pathlib import Path

from core import StudioError, canonical
from execution_checkpoint import advance, save
from source_delivery_checkpoint import request_fingerprint, SourceCheckpointError


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
            or verification.get("passed") is not True
            or receipt.get("implementation_complete") is not True
            or receipt.get("request_fingerprint") != _fingerprint(request)):
        raise SourceCheckpointError("Managed review delivery checkpoint identity changed")
    return True


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
    }
    checkpoint = advance(checkpoint, phase="published", last_verification=verification)
    path = out / ".autonomy/generic-execution-checkpoint.json"
    # Persist before contacting GitHub: a failed POST must not erase completed work.
    save(path, checkpoint)
    if observer is not None:
        observer(dict(checkpoint))
    try:
        pr = repo.ensure_pull_request(
            title="Autonomous managed project: " + str(request.get("app_name") or request["id"]),
            body="Verified implementation checkpoint. Review independent checks before merging.",
            expected_sha=sha,
        )
    except StudioError as exc:
        denied = any(marker in str(exc) for marker in ("HTTP 401", "HTTP 403"))
        handoff = repo.request_trusted_review_handoff(sha) if denied else None
        pr = (repo.await_trusted_review(sha)
              if isinstance(handoff, dict) and handoff.get("status") == "accepted" else None)
    confirmed = (isinstance(pr, dict) and type(pr.get("number")) is int
                 and pr["number"] > 0 and pr.get("state") == "open"
                 and pr.get("url") == f"https://github.com/{request['target_repo']}/pull/{pr['number']}")
    checkpoint = advance(checkpoint, phase="complete" if confirmed else "published")
    save(path, checkpoint)
    if observer is not None:
        observer(dict(checkpoint))
    status = "complete" if confirmed else "deferred"
    next_stage = None if confirmed else "review_handoff"
    blockers = [] if confirmed else ["Exact-commit review PR not confirmed"]
    report = {
        **state, "engine": "generic", "target_repo": request["target_repo"],
        "rounds": state.get("rounds") or [{"round": checkpoint["round"],
                                          "changed_files": changed, "verification": verification}],
        "status": status, "checkpoint_commit": sha,
        "verification": verification,
        "pull_request": pr if confirmed else {"state": "unavailable", "reason": "review_commit_unverified"},
        "resume_mode": "managed_generic_review_delivery",
        "execution_checkpoint": {key: checkpoint[key] for key in ("round", "phase", "base_sha")},
        "completion": {"finished": confirmed, "next_stage": next_stage, "blockers": blockers},
        "release_status": "source_review_pending_human_approval" if confirmed else "verified_branch_review_blocked",
        "blockers": blockers,
    }
    (out / "generic-report.json").write_text(canonical(report), encoding="utf-8")
    return {"status": status, "report": report, "next_stage": next_stage}
