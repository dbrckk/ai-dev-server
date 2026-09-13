"""Deterministic task-context classification for strategy routing."""
from __future__ import annotations

VALID_CONTEXTS = {
    "frontend",
    "backend",
    "tests",
    "refactor",
    "bugfix",
    "mobile",
    "devops",
    "data",
    "general",
}


def classify(brief: str, toolchain: dict | None = None) -> str:
    text = (brief or "").lower()
    stacks = set(toolchain.get("stacks", [])) if isinstance(toolchain, dict) else set()

    rules = (
        ("tests", ("test", "coverage", "pytest", "jest", "spec", "regression")),
        ("bugfix", ("bug", "fix", "crash", "error", "broken", "regression", "issue")),
        ("refactor", ("refactor", "cleanup", "clean up", "restructure", "architecture", "technical debt")),
        ("mobile", ("android", "ios", "flutter", "react native", "mobile", "swift")),
        ("frontend", ("frontend", "ui", "ux", "css", "html", "react", "vue", "svelte", "component")),
        ("backend", ("backend", "api", "server", "endpoint", "database", "sql", "auth")),
        ("devops", ("ci", "cd", "docker", "deployment", "deploy", "kubernetes", "workflow", "github actions")),
        ("data", ("data", "etl", "pandas", "analytics", "pipeline", "dataset")),
    )
    for context, keywords in rules:
        if any(keyword in text for keyword in keywords):
            return context

    if {"swift"} & stacks:
        return "mobile"
    if {"node", "deno", "bun"} & stacks and any(x in text for x in ("page", "browser", "web")):
        return "frontend"
    if {"python", "go", "rust", "maven", "gradle", "dotnet", "php", "ruby", "elixir"} & stacks:
        return "backend"
    return "general"


def hierarchy(brief: str, toolchain: dict | None = None) -> list[str]:
    primary = classify(brief, toolchain)
    stacks = []
    if isinstance(toolchain, dict) and isinstance(toolchain.get("stacks"), list):
        stacks = sorted({str(x).strip().lower() for x in toolchain["stacks"] if str(x).strip()})
    contexts = [primary]
    contexts.extend("stack:" + stack for stack in stacks)
    contexts.append("general")
    result = []
    for item in contexts:
        if item not in result:
            result.append(item)
    return result


def weighted_contexts(brief: str, toolchain: dict | None = None) -> list[tuple[str, float]]:
    """Return deterministic multi-label task contexts with normalized weights."""
    text = (brief or "").lower()
    stacks = []
    if isinstance(toolchain, dict) and isinstance(toolchain.get("stacks"), list):
        stacks = sorted({str(x).strip().lower() for x in toolchain["stacks"] if str(x).strip()})

    rules = (
        ("tests", ("test", "coverage", "pytest", "jest", "spec", "regression")),
        ("bugfix", ("bug", "fix", "crash", "error", "broken", "regression", "issue")),
        ("refactor", ("refactor", "cleanup", "clean up", "restructure", "architecture", "technical debt")),
        ("mobile", ("android", "ios", "flutter", "react native", "mobile", "swift")),
        ("frontend", ("frontend", "ui", "ux", "css", "html", "react", "vue", "svelte", "component")),
        ("backend", ("backend", "api", "server", "endpoint", "database", "sql", "auth")),
        ("devops", ("ci", "cd", "docker", "deployment", "deploy", "kubernetes", "workflow", "github actions")),
        ("data", ("data", "etl", "pandas", "analytics", "pipeline", "dataset")),
    )
    scores = {}
    for context, keywords in rules:
        hits = sum(1 for keyword in keywords if keyword in text)
        if hits:
            scores[context] = min(1.0, 0.55 + 0.15 * (hits - 1))

    if not scores:
        primary = classify(brief, toolchain)
        scores[primary] = 0.75 if primary != "general" else 0.50

    for stack in stacks:
        scores["stack:" + stack] = max(scores.get("stack:" + stack, 0.0), 0.35)

    scores["general"] = max(scores.get("general", 0.0), 0.15)
    total = sum(scores.values())
    if total <= 0:
        return [("general", 1.0)]
    ordered = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
    return [(name, weight / total) for name, weight in ordered]
