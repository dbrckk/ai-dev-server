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



def _deep_profile(api: API, repo: dict) -> dict:
    full=repo.get("full_name")
    default=repo.get("default_branch")
    if not isinstance(full,str) or not isinstance(default,str) or not default:
        return {}
    try:
        branch=api.call("GET","/repos/"+full+"/branches/"+quote(default))
        sha=branch.get("commit",{}).get("sha") if isinstance(branch,dict) else None
        if not isinstance(sha,str):
            return {}
        tree=api.call("GET","/repos/"+full+"/git/trees/"+sha+"?recursive=1")
        if not isinstance(tree,dict) or tree.get("truncated") or not isinstance(tree.get("tree"),list):
            return {}
        paths=[item.get("path") for item in tree["tree"] if isinstance(item,dict) and item.get("type")=="blob" and isinstance(item.get("path"),str)]
        markers=[x for x in ("pubspec.yaml","project.godot","package.json","pyproject.toml","requirements.txt","Cargo.toml","go.mod","pom.xml","build.gradle","build.gradle.kts") if x in paths]
        readme=next((item for item in tree["tree"] if isinstance(item,dict) and str(item.get("path","")).lower()=="readme.md" and item.get("type")=="blob"),None)
        excerpt=""
        if isinstance(readme,dict) and isinstance(readme.get("sha"),str):
            blob=api.call("GET","/repos/"+full+"/git/blobs/"+readme["sha"])
            if isinstance(blob,dict) and blob.get("encoding")=="base64":
                import base64
                try: excerpt=base64.b64decode(blob.get("content","")).decode("utf-8")[:3000]
                except Exception: excerpt=""
        return {"default_branch":default,"head_sha":sha,"markers":markers,"file_count":len(paths),"readme_excerpt":excerpt}
    except StudioError:
        return {}

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
    by_name={repo.get("full_name"):repo for repo in repos if isinstance(repo,dict)}
    selected=ranked[:12]
    for item in selected[:6]:
        source=by_name.get(item["repo"])
        if isinstance(source,dict):
            item["deep_profile"]=_deep_profile(api,source)
    result = {
        "status": "ok",
        "target_repo": target_repo,
        "repositories_scanned": len(repos),
        "similar": selected,
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "portfolio-research.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    return result
