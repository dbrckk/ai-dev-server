"""Single-source, model-authored Jumpy repair with exact review handoff.

This path is deliberately limited to an operator-launched public Jumpy canary.
It bypasses full game generation but never substitutes a deterministic patch.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from core import StudioError, canonical
from execution_checkpoint import advance as advance_checkpoint, new as new_checkpoint, save as save_checkpoint
from generic_model import ask
from generic_repository import GenericRepository
from production_os_worker_canary import canary_instruction
from run import GitHub
from source_delivery_checkpoint import request_fingerprint, resume_published_source, source_operation
from target_ci_verification import wait_for_exact_commit_ci, finalize_source_delivery_evidence

_TARGET = "dbrckk/Jumpy"
_FILE = "scripts/integrations.gd"
_SEQUENCE = re.compile(r"^Production-OS verified Jumpy source qualification ([1-9][0-9]{0,8})\.")
_FUNCTION = re.compile(r"(?ms)^func share_score\([^\n]*\n.*?(?=^func |\Z)")
_CLIPBOARD = "\tDisplayServer.clipboard_set(text)\n"
_SHARE_EVENT = re.compile(r'(?m)^\tevent\("share_score",\s*\{')
_UNAVAILABLE_EVENT = re.compile(
    r'^event\("share_unavailable", \{"reason": "(clipboard_unsupported|clipboard_unavailable)"\}\)$'
)


def contract(req: dict) -> int | None:
    """Fail closed unless the full trusted control-plane instruction matches."""
    if not isinstance(req, dict) or req.get("target_repo") != _TARGET:
        return None
    op = req.get("production_os")
    if not isinstance(op, dict) or not all(
        isinstance(op.get(key), str) and op[key]
        for key in ("workflow_id", "workflow_task_id")
    ):
        return None
    if not re.fullmatch(r"mp-[a-f0-9]{24}", str(req.get("repository_branch_id") or "")):
        return None
    brief = req.get("brief")
    if not isinstance(brief, str):
        return None
    matched = _SEQUENCE.match(brief)
    if matched is None:
        return None
    sequence = int(matched.group(1))
    if brief != canary_instruction(sequence, "jumpy_share_clipboard_guard"):
        return None
    return sequence


def apply_model_guard(original: str, answer: dict) -> str:
    """Validate model-authored GDScript before touching the on-disk project."""
    if not isinstance(original, str) or not isinstance(answer, dict):
        raise StudioError("Source repair has invalid data")
    if set(answer) != {"guard_lines"}:
        raise StudioError("Source repair response has unexpected keys")
    lines = answer["guard_lines"]
    if not isinstance(lines, list) or len(lines) != 3 or not all(
        isinstance(line, str) and 0 < len(line) < 140
        and line == line.strip() and "\n" not in line and "\r" not in line
        and "\t" not in line for line in lines
    ):
        raise StudioError("Source repair guard is not three bounded statements")
    if lines[0] != "if not DisplayServer.has_feature(DisplayServer.FEATURE_CLIPBOARD):":
        raise StudioError("Source repair must guard unsupported clipboard capability")
    if not _UNAVAILABLE_EVENT.fullmatch(lines[1]):
        raise StudioError("Source repair has an unsupported failure event")
    if lines[2] != "return":
        raise StudioError("Source repair must exit the unavailable branch")
    if original.count(_CLIPBOARD) != 1:
        raise StudioError("Source repair clipboard anchor missing or ambiguous")
    match = _FUNCTION.search(original)
    if match is None:
        raise StudioError("Source repair share_score function missing")
    original_function = match.group(0)
    if _CLIPBOARD not in original_function or not _SHARE_EVENT.search(original_function):
        raise StudioError("Source repair must preserve existing successful-share analytics")
    if "DisplayServer.has_feature(DisplayServer.FEATURE_CLIPBOARD)" in original_function:
        raise StudioError("Source repair already applied")
    inserted = "\t" + lines[0] + "\n\t\t" + lines[1] + "\n\t\t" + lines[2] + "\n"
    changed = original.replace(_CLIPBOARD, inserted + _CLIPBOARD, 1)
    if changed == original or changed.replace(inserted, "", 1) != original:
        raise StudioError("Source repair did not produce exactly one source insertion")
    return changed


def run(req: dict, out: Path, work: Path, *, checkpoint_observer=None) -> dict:
    sequence = contract(req)
    if sequence is None:
        raise StudioError("Model-authored Jumpy repair requires exact operator contract")
    out.mkdir(parents=True, exist_ok=True)
    github = GitHub(_TARGET)
    repo = GenericRepository(github, _TARGET, req["repository_branch_id"])
    with source_operation("restore"):
        base_sha, restore = repo.restore(work)
    target = work / _FILE
    if not target.is_file() or target.is_symlink():
        raise StudioError("Source repair target missing or unsafe")
    before = target.read_text(encoding="utf-8")
    checkpoint_path = out / ".autonomy" / "generic-execution-checkpoint.json"
    resumed = resume_published_source(checkpoint_path, req, _FILE, base_sha, before)
    if resumed is None:
        match = _FUNCTION.search(before)
        if match is None:
            raise StudioError("Source repair target function not found")
        # One genuine bounded provider inference instead of fifteen full-game
        # product/design/implementation/review calls. Never synthesize a patch
        # locally if the model fails or its proposal violates the code contract.
        response, provider = ask(
            "Return only a JSON object with one key guard_lines: three short GDScript "
            "statement strings without indentation. No Markdown or extra fields. "
            "The three lines must check DisplayServer.FEATURE_CLIPBOARD with "
            "DisplayServer.has_feature, emit event(\"share_unavailable\", "
            "{\"reason\": \"clipboard_unsupported\"}) or reason "
            "clipboard_unavailable when unsupported, then return. Preserve the "
            "original supported clipboard and share_score event path unchanged.",
            "Review this public source function:\n" + match.group(0)
            + "\nSupply only the three model-authored lines inserted immediately "
            "before DisplayServer.clipboard_set(text). Do not rewrite the function.",
            code=True,
            role="implementation",
            timeout_seconds=120,
        )
        after = apply_model_guard(before, response)
        target.write_text(after, encoding="utf-8")
        if target.read_text(encoding="utf-8") != after:
            raise StudioError("Source repair write verification failed")
        with source_operation("publish"):
            sha = repo.publish(base_sha, work, f"Jumpy: model-authored clipboard guard (canary {sequence})")
        verification = {
            "target_repo": req["target_repo"],
            "request_fingerprint": request_fingerprint(req),
            "status": "pending",
            "passed": False,
            "source_validation": "passed",
            "model_authored": True,
            "structural_only": False,
            "target_ci": "pending_exact_commit",
            "model": str(provider.get("model") or "") if isinstance(provider, dict) else "",
            "source_path": _FILE,
            "base_source_sha256": hashlib.sha256(before.encode()).hexdigest(),
            "updated_source_sha256": hashlib.sha256(after.encode()).hexdigest(),
            "changed_files": [_FILE],
        }
        checkpoint = advance_checkpoint(
            new_checkpoint(req["id"], "generic", base_sha),
            base_sha=sha,
            round_index=1,
            phase="published",
            last_verification=verification,
        )
    else:
        checkpoint, verification = resumed
        sha = base_sha
    save_checkpoint(checkpoint_path, checkpoint)
    if checkpoint_observer is not None:
        checkpoint_observer(dict(checkpoint))
    with source_operation("review"):
        try:
            repo.ensure_pull_request(
                title="Jumpy: guard clipboard sharing when unavailable",
                body="One model-authored source-only repair; requires independent exact-SHA Godot CI and human review.",
                expected_sha=sha,
            )
            confirmed = repo.await_trusted_review(sha)
            pr = confirmed if confirmed is not None else {"state": "unavailable", "reason": "review_commit_unverified"}
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
                **({"review_handoff": handoff} if handoff is not None else {}),
            }
    pr_confirmed = (type(pr.get("number")) is int
                    and pr.get("url") == f"https://github.com/dbrckk/Jumpy/pull/{pr['number']}")
    ci = {"status": "pending", "reason": "review_pr_not_confirmed"}
    if pr_confirmed:
        with source_operation("target_ci"):
            ci = wait_for_exact_commit_ci(
                github, commit_sha=sha, branch=repo.branch,
                workflow_path=".github/workflows/validate.yml",
                required_steps=(
                    "Verify dispatched checkpoint identity",
                    "Import and parse project",
                    "Smoke-test touch routing and HUD input passthrough",
                ),
            )
    verification, qualified = finalize_source_delivery_evidence(
        verification, ci, pr_confirmed=pr_confirmed,
    )
    checkpoint = advance_checkpoint(
        checkpoint, phase="complete" if qualified else "published",
        last_verification=verification,
    )
    save_checkpoint(checkpoint_path, checkpoint)
    if checkpoint_observer is not None:
        checkpoint_observer(dict(checkpoint))
    blockers = [] if qualified else [
        str(ci.get("reason") or "Target CI is incomplete") if pr_confirmed
        else "Source review PR not confirmed"
    ]
    report = {
        "engine": "generic",
        "status": "complete" if qualified else "blocked",
        "target_repo": _TARGET,
        "rounds": [{"round": 1, "changed_files": [_FILE], "verification": verification}],
        "restore": restore,
        "blockers": blockers,
        "checkpoint_commit": sha,
        "verification": verification,
        "pull_request": pr,
        "execution_checkpoint": {
            "round": checkpoint["round"], "phase": checkpoint["phase"], "base_sha": checkpoint["base_sha"],
        },
        "completion": {
            "finished": qualified, "next_stage": None if qualified else "exact_commit_target_ci",
            "blockers": blockers,
        },
        "release_status": "source_review_pending_human_approval" if qualified else "source_review_pending_exact_sha_ci",
        "resume_mode": "model_authored_jumpy_source_repair",
        "delivery_resumed": resumed is not None,
    }
    (out / "generic-report.json").write_text(canonical(report), encoding="utf-8")
    return {"status": "complete" if qualified else "blocked", "report": report, "next_stage": None if qualified else "exact_commit_target_ci"}
