"""Build a bounded task-local repository context from semantic history."""
from __future__ import annotations

from pathlib import Path


def _read_text(path: Path, *, remaining: int) -> tuple[str | None, int]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return None, remaining
    size = len(text.encode("utf-8"))
    if size > remaining:
        return None, remaining
    return text, remaining - size


def build(
    root: Path,
    *,
    semantic_context: dict | None,
    dependency_graph: dict | None,
    max_files: int = 24,
    max_bytes: int = 180_000,
) -> dict | None:
    if max_files < 1 or max_bytes < 1:
        raise ValueError("task context bounds invalid")
    if not isinstance(semantic_context, dict):
        return None

    seeds: list[str] = []
    for attempt in semantic_context.get("recent_attempts", []):
        if not isinstance(attempt, dict):
            continue
        for rel in attempt.get("changed_files", []):
            if isinstance(rel, str) and rel:
                seeds.append(rel)
        for rel in attempt.get("impacted_tests", []):
            if isinstance(rel, str) and rel:
                seeds.append(rel)

    seeds = list(dict.fromkeys(seeds))
    if not seeds:
        return None

    edges = dependency_graph.get("edges", {}) if isinstance(dependency_graph, dict) else {}
    reverse = dependency_graph.get("reverse", {}) if isinstance(dependency_graph, dict) else {}

    ordered: list[str] = []
    seen: set[str] = set()

    def add(rel: str) -> None:
        if not rel or rel in seen:
            return
        seen.add(rel)
        ordered.append(rel)

    for rel in seeds:
        add(rel)
    for rel in list(ordered):
        for dep in edges.get(rel, []):
            add(dep)
        for parent in reverse.get(rel, []):
            add(parent)

    files = {}
    remaining = max_bytes
    root = Path(root).resolve()
    for rel in ordered[: max_files * 2]:
        if len(files) >= max_files:
            break
        target = (root / rel).resolve()
        if not target.is_relative_to(root) or not target.is_file() or target.is_symlink():
            continue
        text, remaining = _read_text(target, remaining=remaining)
        if text is None:
            continue
        files[rel] = text

    if not files:
        return None

    return {
        "files": files,
        "bytes": max_bytes - remaining,
        "seed_files": seeds[:max_files],
        "selected_files": sorted(files),
        "mode": "task_local_semantic",
    }
