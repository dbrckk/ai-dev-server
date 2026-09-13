"""Bounded selective rollback for generic-project regressions."""
from __future__ import annotations

from pathlib import Path
from typing import Callable

from agents.workspace import restore as restore_workspace, snapshot as snapshot_workspace

MAX_DIAGNOSTIC_RUNS = 6
MAX_CHANGED_FILES = 24


def _delta(before: dict[str, str], current: dict[str, str]) -> list[str]:
    return sorted(
        rel for rel in set(before) | set(current)
        if before.get(rel) != current.get(rel)
    )


def _materialize(
    root: Path,
    *,
    before: dict[str, str],
    current: dict[str, str],
    reverted: set[str],
) -> None:
    restore_workspace(root, before)
    for rel, text in current.items():
        if rel in reverted:
            continue
        if before.get(rel) == text:
            continue
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")


def isolate(
    root: Path,
    *,
    before: dict[str, str],
    verify: Callable[[], dict],
    max_runs: int = MAX_DIAGNOSTIC_RUNS,
) -> dict:
    """Try to preserve a passing subset of a regressive round.

    Starts from the current regressed workspace and cumulatively reverts changed
    files until verification passes. It then greedily re-applies reverted files
    while preserving a passing state. The result is bounded and deterministic.
    """
    if not 1 <= max_runs <= MAX_DIAGNOSTIC_RUNS:
        raise ValueError("selective rollback run budget invalid")

    current = snapshot_workspace(root)
    changed = _delta(before, current)
    if not changed:
        return {
            "status": "no_delta",
            "attempted": False,
            "diagnostic_runs": 0,
            "changed_files": [],
            "reverted_files": [],
            "kept_files": [],
            "verification": None,
        }
    if len(changed) > MAX_CHANGED_FILES:
        return {
            "status": "too_many_changes",
            "attempted": False,
            "diagnostic_runs": 0,
            "changed_files": changed,
            "reverted_files": changed,
            "kept_files": [],
            "verification": None,
        }

    reverted: set[str] = set()
    runs = 0
    last = None

    # Find a passing state by cumulatively reverting files.
    for rel in changed:
        if runs >= max_runs:
            break
        reverted.add(rel)
        _materialize(root, before=before, current=current, reverted=reverted)
        last = verify()
        runs += 1
        if isinstance(last, dict) and last.get("passed") is True:
            break

    if not isinstance(last, dict) or last.get("passed") is not True:
        restore_workspace(root, before)
        return {
            "status": "full_rollback_required",
            "attempted": True,
            "diagnostic_runs": runs,
            "changed_files": changed,
            "reverted_files": changed,
            "kept_files": [],
            "verification": last,
        }

    # Minimize the rollback set: re-apply each reverted file if tests stay green.
    for rel in list(sorted(reverted)):
        if runs >= max_runs:
            break
        candidate = set(reverted)
        candidate.remove(rel)
        _materialize(root, before=before, current=current, reverted=candidate)
        probe = verify()
        runs += 1
        if isinstance(probe, dict) and probe.get("passed") is True:
            reverted = candidate
            last = probe
        else:
            _materialize(root, before=before, current=current, reverted=reverted)

    kept = sorted(set(changed) - reverted)
    _materialize(root, before=before, current=current, reverted=reverted)
    return {
        "status": "partial_rollback_passed",
        "attempted": True,
        "diagnostic_runs": runs,
        "changed_files": changed,
        "reverted_files": sorted(reverted),
        "kept_files": kept,
        "verification": last,
    }
