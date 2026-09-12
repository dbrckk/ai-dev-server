"""Scan the curated GitHub star list and rank potentially useful repositories."""
from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.request import Request, urlopen

DEFAULT_SOURCE = "https://raw.githubusercontent.com/dbrckk/star-list/main/text/star-list.md"

_CAPABILITIES = {
    "agent": {"agent", "agents", "openhands", "hermes", "opencode", "ruflo", "agency"},
    "browser": {"browser", "skyvern", "pydoll", "chrome", "web"},
    "memory": {"memory", "context", "openviking", "khoj"},
    "mcp": {"mcp", "modelcontextprotocol"},
    "routing": {"route", "router", "omniroute", "provider"},
    "skills": {"skills", "superpowers", "ecc", "fabric"},
    "code": {"code", "coding", "opencode", "openhands", "codex", "claude"},
    "research": {"research", "fabric", "khoj", "hermes"},
    "security": {"strix", "hexstrike", "cve", "payloads", "security"},
}


def _read_source(source: str) -> str:
    local = Path(source)
    if local.is_file():
        return local.read_text(encoding="utf-8")
    req = Request(source, headers={"User-Agent": "ai-dev-server"})
    with urlopen(req, timeout=10) as response:
        return response.read().decode("utf-8")


def parse_repositories(text: str) -> list[str]:
    repos = []
    seen = set()
    for match in re.finditer(r"(?m)^-\s+([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)\s*$", text):
        repo = match.group(1)
        if repo not in seen:
            seen.add(repo)
            repos.append(repo)
    return repos


def rank_repositories(repositories: list[str], needs: list[str]) -> list[dict]:
    wanted = {n.lower().strip() for n in needs if n.strip()}
    rows = []
    for repo in repositories:
        haystack = repo.lower()
        matched = set()
        for need in wanted:
            terms = _CAPABILITIES.get(need, {need})
            if any(term in haystack for term in terms):
                matched.add(need)
        if matched:
            rows.append({"repo": repo, "matched": sorted(matched), "score": len(matched)})
    return sorted(rows, key=lambda x: (-x["score"], x["repo"].lower()))


def scan(needs: list[str], source: str = DEFAULT_SOURCE) -> dict:
    text = _read_source(source)
    repos = parse_repositories(text)
    return {
        "source": source,
        "repository_count": len(repos),
        "needs": sorted(set(needs)),
        "matches": rank_repositories(repos, needs),
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("needs", nargs="+")
    parser.add_argument("--source", default=DEFAULT_SOURCE)
    args = parser.parse_args()
    print(json.dumps(scan(args.needs, args.source), indent=2))
