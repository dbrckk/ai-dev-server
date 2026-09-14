"""Create non-blocking structured star-list recommendations for the current project phase."""
from __future__ import annotations

import json
from pathlib import Path

from star_scanner import scan

_PHASE_NEEDS = {
    "planning": ["agent", "research", "memory", "architecture"],
    "implementation": ["code", "agent", "testing", "backend", "frontend"],
    "testing": ["testing", "code-quality", "security", "browser"],
    "browser": ["browser", "web-retrieval", "testing"],
    "adaptation": ["agent", "research", "routing", "memory", "observability"],
}

_PHASE_CAPABILITIES = {
    "testing": [],
    "browser": ["web-retrieval"],
}

def recommend(phase: str, out: Path, *, domain: str | None = None,
              platform: str | None = None, language: str | None = None,
              self_hosted: bool = False) -> dict:
    needs = _PHASE_NEEDS.get(phase, ["agent", "code"])
    out.mkdir(parents=True, exist_ok=True)
    try:
        result = scan(
            needs,
            domain=domain,
            capabilities=_PHASE_CAPABILITIES.get(phase, []),
            platform=platform,
            language=language,
            self_hosted=self_hosted,
            top=12,
        )
        result["phase"] = phase
        result["status"] = "ok"
    except Exception as exc:
        result = {
            "phase": phase,
            "needs": needs,
            "status": "unavailable",
            "error": type(exc).__name__,
            "matches": [],
        }
    (out / "star-recommendations.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return result
