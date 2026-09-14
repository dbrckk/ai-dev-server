"""Persist a safe inventory of discovered local/free AI capacity."""
from __future__ import annotations

import json
from pathlib import Path

from atomic_file import write_text as atomic_write_text
from local_capacity import discover


def write(out: Path) -> dict:
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for item in discover():
        if not isinstance(item, dict):
            continue
        rows.append({
            "name": item.get("name"),
            "base": item.get("base"),
            "model": item.get("model"),
            "code_model": item.get("code_model"),
            "vision_model": item.get("vision_model"),
            "model_count": len(item.get("models") or []),
            "models": list(item.get("models") or [])[:64],
            "mode": (
                "unmetered"
                if item.get("unmetered") is True
                else "pooled-free"
                if int(item.get("monthly_token_quota", 0) or 0) > 0
                else "metered"
            ),
            "monthly_token_quota": int(item.get("monthly_token_quota", 0) or 0) or None,
        })
    payload = {
        "status": "ok",
        "gateways": rows,
        "gateway_count": len(rows),
        "model_count": sum(int(row.get("model_count", 0) or 0) for row in rows),
        "unmetered_gateways": sum(row.get("mode") == "unmetered" for row in rows),
        "pooled_free_gateways": sum(row.get("mode") == "pooled-free" for row in rows),
    }
    atomic_write_text(
        out / "local-capacity-inventory.json",
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return payload
