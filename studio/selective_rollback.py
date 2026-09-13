"""Bounded delta-debugging for regressive generic-project rounds."""
from __future__ import annotations

from pathlib import Path
from typing import Callable

from agents.workspace import restore as restore_workspace, snapshot as snapshot_workspace

MAX_DIAGNOSTIC_RUNS = 8
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


def _passed(value: dict | None) -> bool:
    return isinstance(value, dict) and value.get("passed") is True


def _halves(items: list[str]) -> tuple[list[str], list[str]]:
    pivot = max(1, len(items) // 2)
    return items[:pivot], items[pivot:]


def isolate(
    root: Path,
    *,
    before: dict[str, str],
    verify: Callable[[], dict],
    max_runs: int = MAX_DIAGNOSTIC_RUNS,
) -> dict:
    """Preserve the largest proven-safe portion of a regressive round.

    The original published baseline is re-verified first. A passing baseline is
    required before attributing the regression to current changes. The rollback
    set is then reduced by partition tests followed by greedy minimization.
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
            "strategy": "none",
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
            "strategy": "full_rollback",
        }

    runs = 0

    # Establish causality: the authoritative pre-round workspace must still pass.
    reverted = set(changed)
    _materialize(root, before=before, current=current, reverted=reverted)
    baseline = verify()
    runs += 1
    if not _passed(baseline):
        restore_workspace(root, before)
        return {
            "status": "baseline_not_reproducible",
            "attempted": True,
            "diagnostic_runs": runs,
            "changed_files": changed,
            "reverted_files": changed,
            "kept_files": [],
            "verification": baseline,
            "strategy": "full_rollback",
        }

    last = baseline

    # Delta-debugging: if reverting only one half still passes, the culprit set is
    # entirely contained in that half. Recurse while the budget permits.
    while len(reverted) > 1 and runs < max_runs:
        ordered = sorted(reverted)
        left, right = _halves(ordered)
        narrowed = False
        for part in (left, right):
            if not part or runs >= max_runs:
                break
            candidate = set(part)
            _materialize(root, before=before, current=current, reverted=candidate)
            probe = verify()
            runs += 1
            if _passed(probe):
                reverted = candidate
                last = probe
                narrowed = True
                break
        if not narrowed:
            # Culprits likely span partitions; greedy minimization below can still
            # remove unrelated files from the rollback set.
            _materialize(root, before=before, current=current, reverted=reverted)
            break

    # Minimize the proven passing rollback set one file at a time.
    for rel in list(sorted(reverted)):
        if runs >= max_runs or len(reverted) <= 1:
            break
        candidate = set(reverted)
        candidate.remove(rel)
        _materialize(root, before=before, current=current, reverted=candidate)
        probe = verify()
        runs += 1
        if _passed(probe):
            reverted = candidate
            last = probe
        else:
            _materialize(root, before=before, current=current, reverted=reverted)

    kept = sorted(set(changed) - reverted)
    if not kept:
        restore_workspace(root, before)
        return {
            "status": "full_rollback_required",
            "attempted": True,
            "diagnostic_runs": runs,
            "changed_files": changed,
            "reverted_files": changed,
            "kept_files": [],
            "verification": last,
            "strategy": "full_rollback",
        }

    _materialize(root, before=before, current=current, reverted=reverted)
    return {
        "status": "partial_rollback_passed",
        "attempted": True,
        "diagnostic_runs": runs,
        "changed_files": changed,
        "reverted_files": sorted(reverted),
        "kept_files": kept,
        "verification": last,
        "strategy": "partition_then_minimize",
    }
