"""Bounded, model-authored source repair of explicitly operator-approved public tasks.

No generic arbitrary-file editing, test execution with secrets, implicit
provider opt-in, PR merge or synthetic fallback.
"""
from __future__ import annotations

import ast
import hashlib
import json
import re
from pathlib import Path

from core import StudioError, canonical
from execution_checkpoint import advance as advance_checkpoint, new as new_checkpoint, save as save_checkpoint
from generic_model import ask
from generic_repository import GenericRepository
from production_os_source_tasks import TASKS, SourceTask, instruction
from run import GitHub
from source_delivery_checkpoint import request_fingerprint, resume_published_source, source_operation
from target_ci_verification import wait_for_exact_commit_ci, finalize_source_delivery_evidence

_SEQUENCE = re.compile(
    r"^Production-OS approved bounded public source repair ([1-9][0-9]{0,9}) task ([a-z0-9_]+)\. "
)
_BRANCH = re.compile(r"mp-[a-f0-9]{24}\Z")


def contract(req: dict) -> tuple[int, SourceTask] | None:
    if not isinstance(req, dict) or not isinstance(req.get("brief"), str):
        return None
    match = _SEQUENCE.match(req["brief"])
    if match is None or match.group(2) not in TASKS:
        return None
    sequence, task = int(match.group(1)), TASKS[match.group(2)]
    if (sequence > 1_000_000_000 or req.get("target_repo") != task.repo
            or req["brief"] != instruction(sequence, task.task_id)
            or not _BRANCH.fullmatch(str(req.get("repository_branch_id") or ""))):
        return None
    op = req.get("production_os")
    if not isinstance(op, dict) or any(
        not isinstance(op.get(key), str) or not op[key]
        for key in ("workflow_id", "workflow_task_id")
    ):
        return None
    return sequence, task


def _line_statement(line: str) -> ast.Assign:
    try:
        node = ast.parse(line.strip()).body
    except (SyntaxError, ValueError, TypeError) as exc:
        raise StudioError("Model proposed invalid Python line") from exc
    if len(node) != 1 or not isinstance(node[0], ast.Assign):
        raise StudioError("Model must preserve one assignment")
    return node[0]


def apply_model_edit(original: str, reply: dict, task: SourceTask) -> str:
    """Verify a one-line model proposal structurally against the vetted task."""
    if not isinstance(original, str) or not isinstance(reply, dict) or set(reply) != {"replacement_line"}:
        raise StudioError("Source edit reply must contain only replacement_line")
    new = reply["replacement_line"]
    old = task.old_line
    indent = old[:len(old) - len(old.lstrip())]
    if (not isinstance(new, str) or not new or len(new) > 240
            or "\n" in new or "\r" in new or "\t" in new
            or new[:len(new) - len(new.lstrip())] != indent
            or new == old or original.count(old + "\n") != 1):
        raise StudioError("Source edit outside one unique bounded line")

    before_ast = _line_statement(old)
    after_ast = _line_statement(new)
    if (len(before_ast.targets) != 1 or len(after_ast.targets) != 1
            or ast.dump(before_ast.targets[0]) != ast.dump(after_ast.targets[0])):
        raise StudioError("Model source edit changes assignment destination")
    expected = ast.Call(
        func=ast.Attribute(value=before_ast.value, attr=task.method, ctx=ast.Load()),
        args=[ast.Constant(value=value) for value in (
            (task.argument,) if task.second_argument is None
            else (task.argument, task.second_argument)
        )], keywords=[],
    )
    if ast.dump(expected) != ast.dump(after_ast.value):
        raise StudioError("Model edit violates the operator-reviewed AST transform")

    # Require the line to remain inside the approved function, not another
    # coincidentally identical statement. No other source bytes may change.
    function = re.search(
        r"(?ms)^def " + re.escape(task.function) + r"\([^\n]*\n.*?(?=^def |^class |\Z)",
        original,
    )
    if function is None or function.group(0).count(old + "\n") != 1:
        raise StudioError("Approved source function/line missing")
    changed = original.replace(old + "\n", new + "\n", 1)
    if changed == original or changed.replace(new + "\n", old + "\n", 1) != original:
        raise StudioError("Source repair did not preserve original bytes")
    try:
        ast.parse(changed, filename=task.path)
    except SyntaxError as exc:
        raise StudioError("Model edit is not syntactically valid Python") from exc
    return changed


def run(req: dict, out: Path, work: Path, *, checkpoint_observer=None) -> dict:
    approved = contract(req)
    if approved is None:
        raise StudioError("Bounded source repair requires an exact approved operator contract")
    sequence, task = approved
    out.mkdir(parents=True, exist_ok=True)
    github = GitHub(task.repo)
    repo = GenericRepository(github, task.repo, req["repository_branch_id"])
    with source_operation("restore"):
        base_sha, restore = repo.restore_approved_source(work, task.path)
    target = work / task.path
    if not target.is_file() or target.is_symlink():
        raise StudioError("Approved source target missing or unsafe")
    before = target.read_text(encoding="utf-8")
    checkpoint_path = out / ".autonomy" / "generic-execution-checkpoint.json"
    resumed = resume_published_source(checkpoint_path, req, task.path, base_sha, before)
    if resumed is None:
        if before.count(task.old_line + "\n") != 1:
            raise StudioError("Approved source task is obsolete or ambiguous")
        # Public source only. Single provider request, caller-owned model budget,
        # and no local synthesized patch when model fails.
        start = before.index("def " + task.function + "(")
        end = before.find("\ndef ", start + 1)
        excerpt = before[start:end if end >= 0 else None][:5500]
        response, provider = ask(
            "Return JSON only: {\"replacement_line\":\"...\"}, no markdown. "
            "Change only the requested Python assignment. Keep leading spaces "
            "exactly; preserve original expression and wrap it only with "
            f".{task.method}({json.dumps(task.argument)}"
            + ("" if task.second_argument is None else ", " + json.dumps(task.second_argument))
            + "). Do not add imports, "
            "other statements or unrelated code. Model must author the new line.",
            task.objective + "\nExisting source:\n" + excerpt +
            "\nExisting exact assignment:\n" + task.old_line +
            "\nReturn the complete replacement source line including indentation.",
            code=True, role="implementation", timeout_seconds=120,
        )
        after = apply_model_edit(before, response, task)
        target.write_text(after, encoding="utf-8")
        if target.read_text(encoding="utf-8") != after:
            raise StudioError("Source edit write verification failed")
        with source_operation("publish"):
            sha = repo.publish_approved_source(base_sha, work, task.path,
                f"Source: approved model-authored repair {task.task_id} ({sequence})")
        evidence = {
            "target_repo": req["target_repo"],
            "request_fingerprint": request_fingerprint(req),
            "status": "pending", "passed": False, "source_validation": "passed", "model_authored": True,
            "target_ci": "pending_exact_commit", "source_path": task.path,
            "changed_files": [task.path],
            "model": str(provider.get("model") or "") if isinstance(provider, dict) else "",
            "base_source_sha256": hashlib.sha256(before.encode()).hexdigest(),
            "updated_source_sha256": hashlib.sha256(after.encode()).hexdigest(),
        }
        checkpoint = advance_checkpoint(new_checkpoint(req["id"], "generic", base_sha),
                                        base_sha=sha, round_index=1,
                                        phase="published", last_verification=evidence)
    else:
        checkpoint, evidence = resumed
        sha = base_sha
    save_checkpoint(checkpoint_path, checkpoint)
    if checkpoint_observer is not None:
        checkpoint_observer(dict(checkpoint))
    with source_operation("review"):
        try:
            repo.ensure_pull_request(
                title=f"{task.repo.split('/')[-1]}: model-authored {task.task_id} ({sequence})",
                body="One approved model-authored source edit. Independently validate the exact SHA; no automatic merge.",
                expected_sha=sha,
            )
            if task.task_id == "production_os_worktree_git_ref":
                # A direct PR creation may succeed with a PAT. The independent
                # qualification workflow still needs its trusted dispatch.
                handoff = repo.request_trusted_review_handoff(sha)
                if handoff.get("status") != "accepted":
                    raise StudioError("Independent source qualification handoff unavailable")
            pr = repo.await_trusted_review(sha)
        except StudioError as exc:
            denied = any(status in str(exc) for status in ("HTTP 401", "HTTP 403"))
            handoff = repo.request_trusted_review_handoff(sha) if denied else None
            pr = (repo.await_trusted_review(sha)
                  if isinstance(handoff, dict) and handoff.get("status") == "accepted"
                  else None)
    confirmed = (isinstance(pr, dict) and type(pr.get("number")) is int
                 and pr.get("url") == f"https://github.com/{task.repo}/pull/{pr['number']}")
    ci = {"status": "pending", "reason": "review_pr_not_confirmed"}
    if confirmed:
        with source_operation("target_ci"):
            ci = wait_for_exact_commit_ci(
                github, commit_sha=sha, branch=repo.branch,
                workflow_path=task.workflow_path,
                required_steps=task.required_steps,
                timeout_seconds=500,
            )
    evidence, complete = finalize_source_delivery_evidence(
        evidence, ci, pr_confirmed=confirmed,
    )
    checkpoint = advance_checkpoint(
        checkpoint, phase="complete" if complete else "published",
        last_verification=evidence,
    )
    save_checkpoint(checkpoint_path, checkpoint)
    if checkpoint_observer is not None:
        checkpoint_observer(dict(checkpoint))
    blockers = [] if complete else [str(ci.get("reason") or "exact_commit_ci_not_confirmed")]
    report = {
        "engine": "generic", "target_repo": task.repo,
        "status": "complete" if complete else "blocked",
        "rounds": [{"round": 1, "changed_files": [task.path], "verification": evidence}],
        "restore": restore, "blockers": blockers,
        "checkpoint_commit": sha, "verification": evidence,
        "pull_request": pr or {"state": "unavailable"},
        "execution_checkpoint": {
            "round": checkpoint["round"], "phase": checkpoint["phase"],
            "base_sha": checkpoint["base_sha"],
        },
        "completion": {
            "finished": complete, "next_stage": None if complete else "exact_commit_target_ci",
            "blockers": blockers,
        },
        "release_status": "source_review_pending_human_approval" if complete
                          else "source_review_pending_exact_sha_ci",
        "resume_mode": "operator_approved_bounded_source_repair",
        "delivery_resumed": resumed is not None,
    }
    (out / "generic-report.json").write_text(canonical(report), encoding="utf-8")
    return {"status": "complete" if complete else "blocked",
            "report": report, "next_stage": None if complete else "exact_commit_target_ci"}
