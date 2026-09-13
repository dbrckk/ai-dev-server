"""Topological batch scheduling for generic repository edits."""
from __future__ import annotations

from collections import defaultdict, deque


def schedule(graph: dict, files: list[str], *, max_batch_files: int = 4) -> dict:
    if max_batch_files < 1:
        raise ValueError("batch size must be positive")
    unique = sorted(set(str(f) for f in files if f))
    if not unique:
        return {"batches": [], "cyclic": [], "ordered_files": [], "batch_count": 0}

    edges = graph.get("edges", {}) if isinstance(graph, dict) else {}
    selected = set(unique)

    # Dependency orientation: if A imports B, B must be scheduled before A.
    outgoing: dict[str, set[str]] = {f: set() for f in unique}
    indegree: dict[str, int] = {f: 0 for f in unique}
    for consumer in unique:
        for dependency in edges.get(consumer, []):
            if dependency not in selected or dependency == consumer:
                continue
            if consumer not in outgoing[dependency]:
                outgoing[dependency].add(consumer)
                indegree[consumer] += 1

    ready = deque(sorted(f for f in unique if indegree[f] == 0))
    ordered = []
    levels: list[list[str]] = []
    current_ready = list(ready)

    while current_ready:
        level = sorted(current_ready)
        levels.append(level)
        next_ready = []
        for node in level:
            ordered.append(node)
            for consumer in sorted(outgoing[node]):
                indegree[consumer] -= 1
                if indegree[consumer] == 0:
                    next_ready.append(consumer)
        current_ready = sorted(set(next_ready))

    cyclic = sorted(selected - set(ordered))
    if cyclic:
        # Cycles are intentionally isolated into singleton batches so verification
        # happens after every edit rather than applying the cycle atomically.
        ordered.extend(cyclic)
        levels.extend([[item] for item in cyclic])

    batches = []
    for level in levels:
        for start in range(0, len(level), max_batch_files):
            batches.append(level[start:start + max_batch_files])

    return {
        "batches": batches,
        "batch_count": len(batches),
        "ordered_files": ordered,
        "cyclic": cyclic,
    }


def patch_batch_guard(graph: dict, files: list[str], *, max_batch_files: int = 4) -> dict:
    result = schedule(graph, files, max_batch_files=max_batch_files)
    reject = result["batch_count"] > 1
    return {
        **result,
        "reject": reject,
        "reason": (
            "patch spans multiple dependency batches; submit one batch and verify before continuing"
            if reject
            else "patch fits a single dependency batch"
        ),
    }


def hotspot_plan(graph: dict, *, max_batch_files: int = 4, limit: int = 12) -> dict:
    edges = graph.get("edges", {}) if isinstance(graph, dict) else {}
    reverse = graph.get("reverse", {}) if isinstance(graph, dict) else {}
    hotspots = sorted(
        set(edges) | set(reverse),
        key=lambda rel: (-(len(edges.get(rel, [])) + len(reverse.get(rel, []))), rel),
    )[:limit]
    return {
        "hotspots": [
            {
                "path": rel,
                "coupling": len(edges.get(rel, [])) + len(reverse.get(rel, [])),
                "dependencies": list(edges.get(rel, []))[:20],
                "dependents": list(reverse.get(rel, []))[:20],
            }
            for rel in hotspots
        ],
        "recommended_batch_files": max_batch_files,
    }
