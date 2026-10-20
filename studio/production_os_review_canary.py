"""Isolated, exact-contract GitHub delivery canary for opted-in Jumpy.

This does not run a game-development model, alter Godot source or generalize
repository_dispatch to untrusted targets. It proves branch -> review PR delivery.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from core import StudioError, canonical
from execution_checkpoint import advance as advance_checkpoint, new as new_checkpoint, save as save_checkpoint
from generic_repository import GenericRepository
from run import GitHub

_CANARY = re.compile(r"^Production-OS worker canary ([1-9][0-9]{0,8}|1000000000)\.")


def contract(req: dict) -> tuple[str, str] | None:
    """Only an *exact* control-plane Jumpy canary can bypass Godot preview."""
    if not isinstance(req, dict) or req.get("target_repo") != "dbrckk/Jumpy":
        return None
    production_os = req.get("production_os")
    if not isinstance(production_os, dict) or not all(
        isinstance(production_os.get(key), str) and production_os[key]
        for key in ("workflow_id", "workflow_task_id")
    ):
        return None
    brief = req.get("brief")
    if not isinstance(brief, str):
        return None
    match = _CANARY.match(brief)
    if match is None:
        return None
    sequence = int(match.group(1))
    path = f".production-os/worker-canary-{sequence}.txt"
    line = f"production-os-worker-canary sequence {sequence}"
    expected = (
        f"Production-OS worker canary {sequence}. "
        f"Make exactly one intentional product-file change: create {path} "
        f"containing exactly one line: {line}. "
        "Do not change dependencies, workflows, secrets, configuration, "
        "or existing source files. Verify the file content, persist the normal "
        "autonomous checkpoint branch, and finish the task successfully."
    )
    if brief != expected:
        return None
    return path, line


def run(req: dict, out: Path, work: Path, *, checkpoint_observer=None) -> dict:
    checked = contract(req)
    if checked is None:
        raise StudioError("Jumpy delivery canary contract was not verified")
    path, line = checked
    out.mkdir(parents=True, exist_ok=True)
    github = GitHub(req["target_repo"])
    repo = GenericRepository(github, req["target_repo"], req.get("repository_branch_id") or req["id"])
    base_sha, restore = repo.restore(work)

    target = work / path
    if target.exists() or target.is_symlink():
        raise StudioError("Delivery canary target already exists; no overwrite permitted")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(line + "\n", encoding="utf-8")
    raw = target.read_bytes()
    if raw != (line + "\n").encode("utf-8"):
        raise StudioError("Delivery canary file bytes did not match contract")
    sha = repo.publish(base_sha, work, "Production-OS verified Jumpy delivery canary")
    verification = {
        "status": "passed",
        "passed": True,
        "reason": "exact Jumpy Git delivery canary contract",
        "structural_only": True,
        "files": [{"path": path, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}],
    }
    checkpoint = advance_checkpoint(
        new_checkpoint(req["id"], "generic", base_sha),
        base_sha=sha,
        round_index=1,
        phase="published",
        last_verification=verification,
    )
    checkpoint_path = out / ".autonomy" / "generic-execution-checkpoint.json"
    save_checkpoint(checkpoint_path, checkpoint)
    if checkpoint_observer is not None:
        checkpoint_observer(dict(checkpoint))

    try:
        repo.ensure_pull_request(
            title="Review Production-OS Jumpy delivery canary",
            body="Verified, exact-content checkpoint only. Review before merging.",
        )
        # The PR creation response (or an old PR on the same branch) does
        # not prove this specific checkpoint reached review. Confirm the
        # exact published SHA independently before marking delivery complete.
        confirmed = repo.await_trusted_review(sha)
        pr = confirmed if confirmed is not None else {
            "state": "unavailable",
            "reason": "review_commit_unverified",
            "head": repo.branch,
        }
    except StudioError as exc:
        denied = any(marker in str(exc) for marker in ("HTTP 401", "HTTP 403"))
        handoff = repo.request_trusted_review_handoff(sha) if denied else None
        confirmed = (
            repo.await_trusted_review(sha)
            if isinstance(handoff, dict) and handoff.get("status") == "accepted"
            else None
        )
        pr = confirmed if confirmed is not None else {
            "state": "unavailable",
            "reason": "pull_request_write_denied" if denied else "pull_request_unavailable",
            "head": repo.branch,
            **({"review_handoff": handoff} if handoff is not None else {}),
        }
    delivered = type(pr.get("number")) is int and isinstance(pr.get("url"), str) and (
        pr["url"].startswith("https://github.com/dbrckk/Jumpy/pull/")
    )
    if delivered:
        checkpoint = advance_checkpoint(checkpoint, phase="complete")
        save_checkpoint(checkpoint_path, checkpoint)
        if checkpoint_observer is not None:
            checkpoint_observer(dict(checkpoint))
    report = {
        "engine": "generic",
        "status": "complete" if delivered else "blocked",
        "target_repo": req["target_repo"],
        "rounds": [{"round": 1, "changed_files": [path], "verification": verification}],
        "restore": restore,
        "blockers": [] if delivered else ["GitHub review PR not confirmed"],
        "checkpoint_commit": sha,
        "verification": verification,
        "pull_request": pr,
        "execution_checkpoint": {
            "round": checkpoint["round"], "phase": checkpoint["phase"], "base_sha": checkpoint["base_sha"],
        },
        "completion": {
            "finished": delivered, "next_stage": None if delivered else "review_handoff",
            "blockers": [] if delivered else ["GitHub review PR not confirmed"],
        },
        "release_status": "verified_project_complete" if delivered else "verified_branch_review_blocked",
        "resume_mode": "exact_jumpy_delivery_canary",
    }
    (out / "generic-report.json").write_text(canonical(report), encoding="utf-8")
    return {"status": "complete" if delivered else "blocked", "report": report, "next_stage": None if delivered else "review_handoff"}
