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
