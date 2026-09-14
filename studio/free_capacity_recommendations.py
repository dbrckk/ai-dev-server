"""Discover self-hosted/open-source capacity sources from star-list."""
from __future__ import annotations

import json
from pathlib import Path

from atomic_file import write_text as atomic_write_text
from star_scanner import scan

_NEEDS = [
    "local model serving",
    "offline inference",
    "self-hosted ai",
    "coding agent",
    "model routing",
]

_PREFERRED_REPOS = {
    "ollama/ollama",
    "hiyouga/LlamaFactory",
    "OpenHands/OpenHands",
    "anomalyco/opencode",
    "BerriAI/litellm",
    "mudler/LocalAI",
    "vllm-project/vllm",
    "ggerganov/llama.cpp",
    "Alisharvr1/free-claude-code",
}


def discover(out: Path) -> dict:
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    try:
        result = scan(_NEEDS, self_hosted=True, top=24)
        matches = result.get("matches") if isinstance(result, dict) else []
        matches = matches if isinstance(matches, list) else []
        ranked = []
        for item in matches:
            if not isinstance(item, dict):
                continue
            row = dict(item)
            repo = row.get("repo")
            row["preferred_capacity_source"] = repo in _PREFERRED_REPOS
            ranked.append(row)
        ranked.sort(
            key=lambda row: (
                not row.get("preferred_capacity_source", False),
                -float(row.get("quality_score") or 0.0),
                -float(row.get("score") or 0.0),
                str(row.get("repo") or ""),
            )
        )
        payload = {
            "status": "ok",
            "policy": {
                "self_hosted_only": True,
                "purpose": "increase unmetered or effectively-free AI capacity",
                "does_not_assume_external_unlimited_quota": True,
            },
            "matches": ranked[:12],
            "source": result.get("source") if isinstance(result, dict) else None,
        }
    except Exception as exc:
        payload = {
            "status": "unavailable",
            "error": type(exc).__name__,
            "matches": [],
            "policy": {
                "self_hosted_only": True,
                "does_not_assume_external_unlimited_quota": True,
            },
        }

    atomic_write_text(
        out / "free-capacity-recommendations.json",
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return payload
