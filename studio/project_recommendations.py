"""Create non-blocking star-list recommendations for the current project phase."""
from __future__ import annotations

import json
from pathlib import Path

from star_scanner import scan

_PHASE_NEEDS = {
    "planning": ["agent", "research", "skills", "memory"],
    "implementation": ["agent", "code", "skills", "mcp"],
    "testing": ["agent", "code", "security", "mcp"],
    "browser": ["browser", "agent", "mcp"],
    "adaptation": ["agent", "research", "routing", "memory"],
}


def recommend(phase: str, out: Path) -> dict:
    needs = _PHASE_NEEDS.get(phase, ["agent", "code"])
    out.mkdir(parents=True, exist_ok=True)
    try:
        result = scan(needs)
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
