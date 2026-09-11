"""Bounded autonomous research with explicit source provenance."""
from __future__ import annotations

import hashlib
import re
from urllib.parse import urlsplit, urlunsplit

try:
    from .memory_bridge import remember_research
except ImportError:
    from memory_bridge import remember_research


MAX_QUERIES = 6
MAX_RESULTS_PER_QUERY = 8
MAX_CONTENT_BYTES = 200_000
SHA_RE = re.compile(r"[0-9a-f]{64}")


class ResearchError(ValueError):
    pass


def _clean_url(value):
    if not isinstance(value, str) or not value.strip():
        raise ResearchError("research source invalid")
    parsed = urlsplit(value.strip())
    if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
        raise ResearchError("research source must be credential-free HTTPS")
    if parsed.port is not None and not 1 <= parsed.port <= 65535:
        raise ResearchError("research source port invalid")
    return urlunsplit((parsed.scheme.lower(), parsed.netloc.lower(), parsed.path or "/", parsed.query, ""))


def _queries(objective):
    if not isinstance(objective, str) or not objective.strip() or len(objective) > 2000:
        raise ResearchError("research objective invalid")
    base = " ".join(objective.split())
    candidates = [
        base,
        base + " official documentation",
        base + " implementation",
        base + " security limitations",
    ]
    out = []
    for item in candidates:
        if item not in out:
            out.append(item)
    return out[:MAX_QUERIES]


def _content_bytes(value):
    if isinstance(value, str):
        try:
            raw = value.encode("utf-8")
        except UnicodeEncodeError:
            raise ResearchError("research content invalid UTF-8") from None
    elif isinstance(value, bytes):
        raw = value
        try:
            raw.decode("utf-8")
        except UnicodeDecodeError:
            raise ResearchError("research content invalid UTF-8") from None
    else:
        raise ResearchError("research content invalid")
    if not raw or len(raw) > MAX_CONTENT_BYTES:
        raise ResearchError("research content size invalid")
    return raw


def run_research(candidate_id, objective, search_provider, fetch_provider, *, min_sources=2):
    if not isinstance(candidate_id, str) or not candidate_id.strip() or len(candidate_id) > 120:
        raise ResearchError("candidate id invalid")
    if not callable(search_provider) or not callable(fetch_provider):
        raise ResearchError("research provider invalid")
    if not isinstance(min_sources, int) or isinstance(min_sources, bool) or not 1 <= min_sources <= 8:
        raise ResearchError("minimum source count invalid")

    selected = {}
    for query in _queries(objective):
        results = search_provider(query)
        if not isinstance(results, list):
            raise ResearchError("search provider result invalid")
        if len(results) > MAX_RESULTS_PER_QUERY:
            results = results[:MAX_RESULTS_PER_QUERY]
        for result in results:
            if not isinstance(result, dict):
                raise ResearchError("search result invalid")
            url = _clean_url(result.get("url"))
            title = result.get("title")
            kind = result.get("kind", "web")
            if not isinstance(title, str) or not title.strip() or len(title) > 500:
                raise ResearchError("research title invalid")
            if not isinstance(kind, str) or not re.fullmatch(r"[a-z][a-z0-9_.-]{1,40}", kind):
                raise ResearchError("research kind invalid")
            selected.setdefault(url, {"title": title.strip(), "kind": kind, "query": query})
        if len(selected) >= min_sources:
            break

    if len(selected) < min_sources:
        return {
            "status": "research_incomplete",
            "candidate_id": candidate_id,
            "reason": "insufficient_sources",
            "items": [],
        }

    items = []
    for url in sorted(selected)[:MAX_RESULTS_PER_QUERY]:
        meta = selected[url]
        raw = _content_bytes(fetch_provider(url))
        digest = hashlib.sha256(raw).hexdigest()
        if not SHA_RE.fullmatch(digest):
            raise ResearchError("research digest invalid")
        text = raw.decode("utf-8")
        notes = " ".join(text.split())
        if not notes:
            raise ResearchError("research content empty")
        items.append({
            "kind": meta["kind"],
            "source": url,
            "title": meta["title"],
            "query": meta["query"],
            "notes": notes[:4000],
            "content_sha256": digest,
            "content_bytes": len(raw),
        })

    if len(items) < min_sources:
        return {
            "status": "research_incomplete",
            "candidate_id": candidate_id,
            "reason": "insufficient_valid_sources",
            "items": [],
        }
    return {"status": "research_complete", "candidate_id": candidate_id, "items": items}


def run_and_remember(memory, project_id, candidate_id, objective, search_provider, fetch_provider, *, min_sources=2):
    research = run_research(
        candidate_id,
        objective,
        search_provider,
        fetch_provider,
        min_sources=min_sources,
    )
    if research["status"] != "research_complete":
        return memory, research
    return remember_research(memory, project_id, research), research
