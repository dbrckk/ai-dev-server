"""Bounded GitHub repository maintenance probe for architecture evidence."""
from __future__ import annotations

import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

MAX_REPOS = 8
TIMEOUT_SECONDS = 4
ACTIVE_DAYS = 180
STALE_DAYS = 365

def _epoch(value: str | None) -> float | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None

def classify(metadata: dict, *, now: float | None = None) -> dict:
    now_value = time.time() if now is None else float(now)
    if not isinstance(metadata, dict):
        return {"status": "unknown", "reason": "invalid_metadata"}

    if metadata.get("archived") is True:
        return {"status": "archived", "reason": "github_archived"}

    pushed_at = metadata.get("pushed_at")
    pushed_epoch = _epoch(pushed_at)
    if pushed_epoch is None:
        return {
            "status": "unknown",
            "reason": "missing_push_timestamp",
            "pushed_at": pushed_at,
        }

    age_days = max(0.0, (now_value - pushed_epoch) / 86400.0)
    if age_days > STALE_DAYS:
        status = "stale"
    elif age_days > ACTIVE_DAYS:
        status = "aging"
    else:
        status = "active"

    return {
        "status": status,
        "reason": "push_recency",
        "pushed_at": pushed_at,
        "age_days": round(age_days, 1),
        "archived": False,
    }

def _fetch(repo: str, token: str | None) -> dict:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "ai-dev-server-maintenance-probe",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = Request(f"https://api.github.com/repos/{repo}", headers=headers)
    try:
        with urlopen(req, timeout=TIMEOUT_SECONDS) as response:
            value = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, UnicodeError) as exc:
        return {"repo": repo, "status": "unknown", "reason": type(exc).__name__}
    result = classify(value)
    result["repo"] = repo
    return result

def probe(repositories: list[str], *, token: str | None = None) -> dict[str, dict]:
    unique = []
    seen = set()
    for repo in repositories:
        if isinstance(repo, str) and "/" in repo and repo not in seen:
            seen.add(repo)
            unique.append(repo)
        if len(unique) >= MAX_REPOS:
            break

    token = token if token is not None else os.environ.get("GITHUB_TOKEN")
    results = {}
    with ThreadPoolExecutor(max_workers=min(4, max(1, len(unique)))) as pool:
        futures = {pool.submit(_fetch, repo, token): repo for repo in unique}
        for future in as_completed(futures):
            repo = futures[future]
            try:
                results[repo] = future.result()
            except Exception as exc:  # bounded evidence collection must not block pipeline
                results[repo] = {"repo": repo, "status": "unknown", "reason": type(exc).__name__}
    return results
