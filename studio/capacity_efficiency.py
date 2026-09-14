"""Verified progress-per-token memory for projects, providers, and models."""
from __future__ import annotations

import json
from pathlib import Path

from atomic_file import write_text as atomic_write_text
from file_lock import exclusive

SCHEMA = 1
MAX_ROWS = 512
ALPHA = 0.25


def _empty() -> dict:
    return {"schema": SCHEMA, "rows": {}}


def _load_unlocked(path: Path) -> dict:
    if not Path(path).is_file():
        return _empty()
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return _empty()
    if not isinstance(value, dict) or value.get("schema") != SCHEMA:
        return _empty()
    rows = value.get("rows")
    return {"schema": SCHEMA, "rows": rows if isinstance(rows, dict) else {}}


def load(path: Path) -> dict:
    return _load_unlocked(Path(path))


def _key(project_id: str, provider: str, model: str) -> str:
    return "::".join((project_id, provider, model))


def record(
    path: Path,
    *,
    project_id: str,
    provider: str,
    model: str,
    tokens: int,
    verified_success: bool,
) -> dict:
    project = str(project_id).strip()
    provider_name = str(provider).strip()
    model_name = str(model).strip()
    if not project or not provider_name or not model_name:
        raise ValueError("efficiency identity invalid")
    consumed = max(1, int(tokens))
    path = Path(path)
    with exclusive(path):
        data = _load_unlocked(path)
        key = _key(project, provider_name, model_name)
        row = data["rows"].get(key, {
            "project_id": project,
            "provider": provider_name,
            "model": model_name,
            "samples": 0,
            "verified_successes": 0,
            "total_tokens": 0,
            "ema_tokens": 0.0,
            "ema_success": 0.0,
        })
        samples = max(0, int(row.get("samples", 0) or 0))
        prev_tokens = max(0.0, float(row.get("ema_tokens", 0.0) or 0.0))
        prev_success = max(0.0, min(1.0, float(row.get("ema_success", 0.0) or 0.0)))
        observed_success = 1.0 if verified_success else 0.0
        ema_tokens = float(consumed) if samples == 0 else ALPHA * consumed + (1.0 - ALPHA) * prev_tokens
        ema_success = observed_success if samples == 0 else ALPHA * observed_success + (1.0 - ALPHA) * prev_success
        row = {
            "project_id": project,
            "provider": provider_name,
            "model": model_name,
            "samples": samples + 1,
            "verified_successes": max(0, int(row.get("verified_successes", 0) or 0)) + int(bool(verified_success)),
            "total_tokens": max(0, int(row.get("total_tokens", 0) or 0)) + consumed,
            "ema_tokens": round(ema_tokens, 3),
            "ema_success": round(max(0.0, min(1.0, ema_success)), 6),
        }
        data["rows"][key] = row
        if len(data["rows"]) > MAX_ROWS:
            ordered = sorted(
                data["rows"].items(),
                key=lambda item: (
                    int((item[1] or {}).get("samples", 0) or 0),
                    int((item[1] or {}).get("total_tokens", 0) or 0),
                    item[0],
                ),
            )
            for old_key, _ in ordered[: len(data["rows"]) - MAX_ROWS]:
                data["rows"].pop(old_key, None)
        atomic_write_text(path, json.dumps(data, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        return row


def _metrics(row: dict) -> dict:
    samples = max(0, int(row.get("samples", 0) or 0))
    successes = max(0, int(row.get("verified_successes", 0) or 0))
    total_tokens = max(1, int(row.get("total_tokens", 0) or 0))
    cumulative = min(1.0, successes / samples) if samples else 0.0
    recent = max(0.0, min(1.0, float(row.get("ema_success", cumulative) or 0.0)))
    success = 0.4 * cumulative + 0.6 * recent
    tokens_per_success = total_tokens / max(1, successes)
    verified_per_million = successes * 1_000_000.0 / total_tokens
    conservative = success * min(1.0, samples / 8.0)
    score = conservative * 1_000_000.0 / max(1.0, float(row.get("ema_tokens", total_tokens)))
    return {
        "samples": samples,
        "success_rate": round(success, 6),
        "tokens_per_verified_success": round(tokens_per_success, 3),
        "verified_successes_per_million_tokens": round(verified_per_million, 6),
        "risk_adjusted_score": round(score, 6),
    }


def summarize(path_or_data: Path | dict) -> dict:
    data = load(path_or_data) if isinstance(path_or_data, Path) else path_or_data
    rows = []
    for row in (data.get("rows") or {}).values():
        if not isinstance(row, dict):
            continue
        item = dict(row)
        item.update(_metrics(row))
        rows.append(item)
    rows.sort(key=lambda row: (-float(row["risk_adjusted_score"]), -int(row["samples"]), row["provider"], row["model"]))
    project_scores = {}
    for row in rows:
        project = row["project_id"]
        bucket = project_scores.setdefault(project, {"weighted_score": 0.0, "tokens": 0, "samples": 0})
        tokens = max(1, int(row.get("total_tokens", 0) or 0))
        bucket["weighted_score"] += float(row["risk_adjusted_score"]) * tokens
        bucket["tokens"] += tokens
        bucket["samples"] += int(row["samples"])
    projects = {}
    for project, bucket in project_scores.items():
        projects[project] = {
            "samples": bucket["samples"],
            "risk_adjusted_score": round(bucket["weighted_score"] / max(1, bucket["tokens"]), 6),
        }
    return {"rows": rows, "projects": projects}


def project_multiplier(summary: dict, project_id: str) -> float:
    projects = summary.get("projects") if isinstance(summary, dict) else None
    if not isinstance(projects, dict):
        return 1.0
    row = projects.get(project_id)
    if not isinstance(row, dict) or int(row.get("samples", 0) or 0) < 3:
        return 1.0
    scores = [
        max(0.0, float(item.get("risk_adjusted_score", 0.0) or 0.0))
        for item in projects.values()
        if isinstance(item, dict) and int(item.get("samples", 0) or 0) >= 3
    ]
    if len(scores) < 2:
        return 1.0
    mean = sum(scores) / len(scores)
    if mean <= 0:
        return 1.0
    ratio = max(0.5, min(1.5, float(row.get("risk_adjusted_score", 0.0) or 0.0) / mean))
    return round(max(0.75, min(1.25, ratio)), 4)


def routing_bonus(
    summary: dict,
    *,
    project_id: str,
    provider: str,
    model: str,
) -> float:
    rows = summary.get("rows") if isinstance(summary, dict) else None
    if not isinstance(rows, list):
        return 0.0
    mature = [
        row for row in rows
        if isinstance(row, dict)
        and row.get("project_id") == project_id
        and int(row.get("samples", 0) or 0) >= 3
    ]
    if len(mature) < 2:
        return 0.0
    target = next(
        (
            row for row in mature
            if row.get("provider") == provider and row.get("model") == model
        ),
        None,
    )
    if target is None:
        return 0.0
    scores = [max(0.0, float(row.get("risk_adjusted_score", 0.0) or 0.0)) for row in mature]
    mean = sum(scores) / len(scores)
    if mean <= 0:
        return 0.0
    ratio = float(target.get("risk_adjusted_score", 0.0) or 0.0) / mean
    # Deliberately bounded: enough to influence close candidates, never enough
    # to overpower health, capability, quarantine, or architecture safeguards.
    return round(max(-8.0, min(8.0, (ratio - 1.0) * 8.0)), 6)
