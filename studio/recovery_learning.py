"""Learn whether generic recovery policies work for a given toolchain."""
from __future__ import annotations

import json
from pathlib import Path

VERSION = 1


def _toolchain_key(toolchain: dict | None) -> str:
    stacks = []
    if isinstance(toolchain, dict) and isinstance(toolchain.get("stacks"), list):
        stacks = sorted(str(item) for item in toolchain["stacks"] if item)
    return "+".join(stacks) if stacks else "unknown"


def load(path: Path) -> dict:
    path = Path(path)
    if not path.is_file():
        return {"version": VERSION, "rows": {}}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"version": VERSION, "rows": {}}
    if not isinstance(value, dict) or value.get("version") != VERSION or not isinstance(value.get("rows"), dict):
        return {"version": VERSION, "rows": {}}
    return value


def save(path: Path, data: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, sort_keys=True, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def record(
    path: Path,
    *,
    toolchain: dict | None,
    category: str,
    action: str,
    success: bool,
    duration_seconds: float,
) -> dict:
    data = load(path)
    rows = data.setdefault("rows", {})
    key = "|".join((_toolchain_key(toolchain), category or "unknown", action or "unknown"))
    row = rows.get(key, {
        "toolchain": _toolchain_key(toolchain),
        "category": category or "unknown",
        "action": action or "unknown",
        "attempts": 0,
        "successes": 0,
        "total_seconds": 0.0,
    })
    row["attempts"] = int(row.get("attempts", 0)) + 1
    row["successes"] = int(row.get("successes", 0)) + (1 if success else 0)
    row["total_seconds"] = round(float(row.get("total_seconds", 0.0)) + max(0.0, float(duration_seconds)), 3)
    row["success_rate"] = round(row["successes"] / row["attempts"], 4)
    row["mean_seconds"] = round(row["total_seconds"] / row["attempts"], 3)
    rows[key] = row
    save(path, data)
    return row


def row_for(data: dict, *, toolchain: dict | None, category: str, action: str) -> dict | None:
    key = "|".join((_toolchain_key(toolchain), category or "unknown", action or "unknown"))
    row = data.get("rows", {}).get(key) if isinstance(data, dict) else None
    return row if isinstance(row, dict) else None


def adapt(policy: dict, history: dict, *, toolchain: dict | None, category: str) -> dict:
    result = dict(policy)
    action = str(result.get("action", "replan"))
    row = row_for(history, toolchain=toolchain, category=category, action=action)
    if not row:
        result["learning"] = {"status": "insufficient_history"}
        return result

    attempts = int(row.get("attempts", 0))
    rate = float(row.get("success_rate", 0.0))
    result["learning"] = {
        "status": "observed",
        "attempts": attempts,
        "success_rate": rate,
        "mean_seconds": float(row.get("mean_seconds", 0.0)),
    }

    if attempts >= 3 and rate < 0.34:
        result["priority"] = "critical"
        result["provider_switch"] = True
        result["learning"]["escalated"] = True

    if attempts >= 5 and rate == 0.0 and category in {
        "compile_failure",
        "test_failure",
        "regression",
        "no_progress",
        "unknown_failure",
    }:
        result["action"] = "switch_strategy"
        result["provider_switch"] = True
        result["learning"]["strategy_override"] = "switch_strategy"

    return result
