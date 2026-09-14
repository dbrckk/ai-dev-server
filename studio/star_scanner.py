"""Query the structured star-list catalog and rank repositories for a project need."""
from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.request import Request, urlopen

DEFAULT_SOURCE = "https://raw.githubusercontent.com/dbrckk/star-list/main/catalog.json"
FALLBACK_SOURCE = "https://raw.githubusercontent.com/dbrckk/star-list/main/text/star-list.md"

_TIER_BONUS = {"core": 1.0, "recommended": 0.6, "specialized": 0.25, "audit": -0.4}

def _read_source(source: str) -> str:
    local = Path(source)
    if local.is_file():
        return local.read_text(encoding="utf-8")
    req = Request(source, headers={"User-Agent": "ai-dev-server"})
    with urlopen(req, timeout=10) as response:
        return response.read().decode("utf-8")

def _tokens(value: str) -> set[str]:
    return {t for t in re.sub(r"[^a-z0-9+.#_-]+", " ", (value or "").lower()).split() if len(t) > 1}

def parse_catalog(text: str) -> list[dict]:
    value = json.loads(text)
    rows = value.get("repositories")
    if not isinstance(rows, list):
        raise ValueError("catalog repositories missing")
    out = []
    for row in rows:
        if isinstance(row, dict) and isinstance(row.get("repo"), str):
            out.append(row)
    return out

def parse_repositories(text: str) -> list[str]:
    repos, seen = [], set()
    for match in re.finditer(r"(?m)^-\s+([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)(?:\s+—.*)?$", text):
        repo = match.group(1)
        if repo not in seen:
            seen.add(repo)
            repos.append(repo)
    return repos

def _catalog_rank(rows: list[dict], needs: list[str], *, domain: str | None = None,
                  capabilities: list[str] | None = None, platform: str | None = None,
                  language: str | None = None, self_hosted: bool = False,
                  top: int = 12) -> list[dict]:
    wanted = _tokens(" ".join(needs))
    required = {x.lower() for x in (capabilities or [])}
    ranked = []
    for row in rows:
        caps = set(row.get("capabilities", [])) | set(row.get("roles", []))
        if domain and row.get("domain") != domain:
            continue
        if required and not required.issubset(caps):
            continue
        if platform and platform not in row.get("platforms", []):
            continue
        if language and language not in row.get("languages", []):
            continue
        if self_hosted and row.get("selfHosted") is not True:
            continue

        text = " ".join([
            row.get("repo", ""), row.get("category", ""), row.get("domain", ""),
            " ".join(caps), " ".join(row.get("bestFor", []))
        ])
        rtoks = _tokens(text)
        lexical = len(wanted & rtoks) / max(1, len(wanted))
        quality = float(row.get("score", 0.0)) / 10.0
        tier = _TIER_BONUS.get(row.get("tier"), 0.0)
        best = _tokens(" ".join(row.get("bestFor", [])))
        best_match = len(wanted & best) / max(1, len(wanted)) if best else 0.0
        score = 55 * lexical + 15 * best_match + 20 * quality + 10 * max(0.0, tier)

        avoid = _tokens(" ".join(row.get("avoidWhen", [])))
        if wanted & avoid:
            score -= 20

        if score > 0:
            ranked.append({
                "repo": row["repo"],
                "score": round(score, 3),
                "quality_score": row.get("score"),
                "tier": row.get("tier"),
                "domain": row.get("domain"),
                "capabilities": sorted(caps),
                "best_for": row.get("bestFor", []),
                "avoid_when": row.get("avoidWhen", []),
                "alternatives": row.get("alternatives", []),
                "complements": row.get("complements", []),
            })
    ranked.sort(key=lambda x: (-x["score"], -(x["quality_score"] or 0), x["repo"].lower()))
    return ranked[:top]

def rank_repositories(repositories: list[str], needs: list[str]) -> list[dict]:
    wanted = _tokens(" ".join(needs))
    rows = []
    for repo in repositories:
        rtoks = _tokens(repo)
        matched = sorted(wanted & rtoks)
        if matched:
            rows.append({"repo": repo, "matched": matched, "score": len(matched)})
    return sorted(rows, key=lambda x: (-x["score"], x["repo"].lower()))

def scan(needs: list[str], source: str = DEFAULT_SOURCE, **constraints) -> dict:
    try:
        text = _read_source(source)
        rows = parse_catalog(text)
        matches = _catalog_rank(rows, needs, **constraints)
        return {
            "source": source,
            "source_format": "catalog-v1",
            "repository_count": len(rows),
            "needs": sorted(set(needs)),
            "constraints": constraints,
            "matches": matches,
        }
    except Exception:
        fallback = FALLBACK_SOURCE if source == DEFAULT_SOURCE else source
        text = _read_source(fallback)
        repos = parse_repositories(text)
        return {
            "source": fallback,
            "source_format": "markdown-fallback",
            "repository_count": len(repos),
            "needs": sorted(set(needs)),
            "constraints": constraints,
            "matches": rank_repositories(repos, needs)[:12],
        }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("needs", nargs="+")
    parser.add_argument("--source", default=DEFAULT_SOURCE)
    parser.add_argument("--domain")
    parser.add_argument("--capability", action="append", default=[])
    parser.add_argument("--platform")
    parser.add_argument("--language")
    parser.add_argument("--self-hosted", action="store_true")
    parser.add_argument("--top", type=int, default=12)
    args = parser.parse_args()
    print(json.dumps(scan(
        args.needs, args.source, domain=args.domain,
        capabilities=args.capability, platform=args.platform,
        language=args.language, self_hosted=args.self_hosted, top=args.top
    ), indent=2))
