"""Repository-native research providers with immutable Git provenance."""
from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

MAX_SOURCE_BYTES=160_000
MAX_RESULTS=8
TOKEN_RE=re.compile(r"[a-z0-9_]{3,}")


class RepositoryResearchError(ValueError):
    pass


def _tokens(value):
    if not isinstance(value,str):
        return set()
    return set(TOKEN_RE.findall(value.lower().replace(".","_").replace("-","_")))


def _trusted_files(root):
    root=Path(root).resolve()
    files=[]
    for dirname in ("studio","tests"):
        base=root/dirname
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if path.suffix not in {".py",".json",".md"} or not path.is_file() or path.is_symlink():
                continue
            resolved=path.resolve()
            if not resolved.is_relative_to(root):
                continue
            try:
                size=resolved.stat().st_size
            except OSError:
                continue
            if 0 < size <= MAX_SOURCE_BYTES:
                files.append(resolved)
    return files


def build_repository_providers(repo_root, repo_full_name, commit_sha, capability):
    root=Path(repo_root).resolve()
    if not isinstance(repo_full_name,str) or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+",repo_full_name):
        raise RepositoryResearchError("repository identity invalid")
    if not isinstance(commit_sha,str) or not re.fullmatch(r"[0-9a-f]{40}",commit_sha):
        raise RepositoryResearchError("repository commit invalid")
    if not isinstance(capability,str) or not capability.strip():
        raise RepositoryResearchError("capability invalid")

    indexed=[]
    capability_tokens=_tokens(capability)
    for path in _trusted_files(root):
        try:
            text=path.read_text(encoding="utf-8")
        except (OSError,UnicodeError):
            continue
        rel=path.relative_to(root).as_posix()
        haystack=(rel+"\n"+text).lower()
        indexed.append((path,rel,text,haystack))

    prefix=f"https://github.com/{repo_full_name}/blob/{commit_sha}/"

    def search_provider(query):
        wanted=_tokens(query)|capability_tokens
        scored=[]
        for path,rel,text,haystack in indexed:
            score=sum(haystack.count(token) for token in wanted)
            if score<=0:
                continue
            scored.append((-score,rel,{
                "url":prefix+quote(rel,safe="/"),
                "title":"Repository source: "+rel,
                "kind":"repository_source",
            }))
        scored.sort(key=lambda item:(item[0],item[1]))
        return [item[2] for item in scored[:MAX_RESULTS]]

    def fetch_provider(url):
        if not isinstance(url,str) or not url.startswith(prefix):
            raise RepositoryResearchError("research URL outside pinned repository")
        parsed=urlsplit(url)
        if parsed.scheme!="https" or parsed.netloc.lower()!="github.com" or parsed.query or parsed.fragment:
            raise RepositoryResearchError("research URL invalid")
        encoded_path=url[len(prefix):]
        rel=unquote(encoded_path)
        if not rel or "\" in rel:
            raise RepositoryResearchError("research path invalid")
        target=(root/rel).resolve()
        if not target.is_relative_to(root):
            raise RepositoryResearchError("research path escaped repository")
        if not target.is_file() or target.is_symlink():
            raise RepositoryResearchError("research source unavailable")
        if target.suffix not in {".py",".json",".md"}:
            raise RepositoryResearchError("research source type invalid")
        raw=target.read_bytes()
        if not raw or len(raw)>MAX_SOURCE_BYTES:
            raise RepositoryResearchError("research source size invalid")
        return raw

    return search_provider,fetch_provider
