"""Portfolio-wide similarity scan used before every autonomous project.

Only repository metadata is inspected. Source code from other repositories is
never executed. The output is advisory context for planning/reuse.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import quote

from core import API, StudioError

TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9_+.-]{2,}")


def _tokens(value: object) -> set[str]:
    if not isinstance(value, str):
        return set()
    return set(TOKEN_RE.findall(value.lower()))


def _repo_tokens(repo: dict) -> set[str]:
    values = [
        repo.get("name", ""),
        repo.get("description", ""),
        repo.get("language", ""),
        " ".join(repo.get("topics") or []) if isinstance(repo.get("topics"), list) else "",
    ]
    out: set[str] = set()
    for value in values:
        out |= _tokens(value)
    return out


def _list_owned(api: API, owner: str) -> list[dict]:
    repos: list[dict] = []
    # User-token path includes private repositories. If unavailable, fall back to
    # the public owner endpoint.
    for page in range(1, 11):
        try:
            batch = api.call("GET", f"/user/repos?affiliation=owner&per_page=100&page={page}&sort=updated")
        except StudioError:
            repos = []
            break
        if not isinstance(batch, list):
            raise StudioError("GitHub portfolio listing returned invalid data")
        repos.extend(x for x in batch if isinstance(x, dict) and x.get("owner", {}).get("login", "").lower() == owner.lower())
        if len(batch) < 100:
            return repos
    if repos:
        return repos
    public = API("https://api.github.com", api.key)
    for page in range(1, 11):
        batch = public.call("GET", f"/users/{quote(owner)}/repos?per_page=100&page={page}&sort=updated")
        if not isinstance(batch, list):
            raise StudioError("GitHub public portfolio listing returned invalid data")
        repos.extend(x for x in batch if isinstance(x, dict))
        if len(batch) < 100:
            break
    return repos


def scan(target_repo: str, brief: str, out: Path, api: API) -> dict:
    if "/" not in target_repo:
        raise StudioError("Target repository identity invalid")
    owner = target_repo.split("/", 1)[0]
    target_name = target_repo.split("/", 1)[1]
    wanted = _tokens(target_name) | _tokens(brief)
    repos = _list_owned(api, owner)
    ranked = []
    for repo in repos:
        full = repo.get("full_name")
        if not isinstance(full, str) or full.lower() == target_repo.lower():
            continue
        tokens = _repo_tokens(repo)
        overlap = sorted(wanted & tokens)
        if not overlap:
            continue
        score = len(overlap) * 10
        if repo.get("language") and str(repo.get("language")).lower() in wanted:
            score += 8
        ranked.append({
            "repo": full,
            "description": repo.get("description"),
            "language": repo.get("language"),
            "topics": repo.get("topics") if isinstance(repo.get("topics"), list) else [],
            "updated_at": repo.get("updated_at"),
            "private": bool(repo.get("private")),
            "matched_tokens": overlap[:20],
            "score": score,
        })
    ranked.sort(key=lambda x: (-x["score"], x["repo"].lower()))
    result = {
        "status": "ok",
        "target_repo": target_repo,
        "repositories_scanned": len(repos),
        "similar": ranked[:12],
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "portfolio-research.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    return result
