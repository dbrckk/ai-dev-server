"""Monthly token-quota accounting for pooled free/high-quota providers."""
from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from file_lock import exclusive

DEFAULT_OMNIROUTE_MONTHLY_TOKENS = 1_470_000_000


def month_key(now: datetime | None = None) -> str:
    current = now or datetime.now(timezone.utc)
    return current.astimezone(timezone.utc).strftime("%Y-%m")


def load(path: Path) -> dict:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"schema": 1, "months": {}}
    if not isinstance(value, dict) or value.get("schema") != 1:
        return {"schema": 1, "months": {}}
    months = value.get("months")
    return {"schema": 1, "months": months if isinstance(months, dict) else {}}


def _save(path: Path, data: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, sort_keys=True, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass


def record(
    path: Path,
    provider: str,
    *,
    prompt_tokens: int,
    completion_tokens: int,
    now: datetime | None = None,
) -> dict:
    path = Path(path)
    with exclusive(path):
        data = load(path)
        key = month_key(now)
        month = data["months"].setdefault(key, {})
        row = month.get(provider, {
            "calls": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        })
        prompt = max(0, int(prompt_tokens))
        completion = max(0, int(completion_tokens))
        row = {
            "calls": int(row.get("calls", 0)) + 1,
            "prompt_tokens": int(row.get("prompt_tokens", 0)) + prompt,
            "completion_tokens": int(row.get("completion_tokens", 0)) + completion,
            "total_tokens": int(row.get("total_tokens", 0)) + prompt + completion,
        }
        month[provider] = row
        # Retain only the newest 14 calendar buckets.
        for old in sorted(data["months"])[:-14]:
            data["months"].pop(old, None)
        _save(path, data)
        return row


def used_tokens(path_or_data: Path | dict, provider: str, *, now: datetime | None = None) -> int:
    data = load(path_or_data) if isinstance(path_or_data, Path) else path_or_data
    months = data.get("months", {}) if isinstance(data, dict) else {}
    row = months.get(month_key(now), {}).get(provider, {}) if isinstance(months, dict) else {}
    try:
        return max(0, int(row.get("total_tokens", 0)))
    except (TypeError, ValueError):
        return 0


def quota_status(
    path_or_data: Path | dict,
    provider: str,
    monthly_token_quota: int,
    *,
    now: datetime | None = None,
) -> dict:
    quota = max(0, int(monthly_token_quota))
    used = used_tokens(path_or_data, provider, now=now)
    remaining = max(0, quota - used) if quota else None
    ratio = (remaining / quota) if quota else None
    return {
        "month": month_key(now),
        "quota_tokens": quota if quota else None,
        "used_tokens": used,
        "remaining_tokens": remaining,
        "remaining_ratio": round(ratio, 6) if ratio is not None else None,
        "exhausted": bool(quota and used >= quota),
    }


def quota_admission(
    path_or_data: Path | dict,
    provider: str,
    monthly_token_quota: int,
    *,
    estimated_tokens: int,
    reserve_ratio: float = DEFAULT_RESERVE_RATIO,
    allow_reserve: bool = False,
    now: datetime | None = None,
) -> dict:
    """Decide whether a metered pooled provider may accept another call.

    Non-critical work cannot consume the configured reserve. Critical work may
    use it, while still refusing calls that would exceed the remaining quota.
    """
    quota = max(0, int(monthly_token_quota))
    estimate = max(1, int(estimated_tokens))
    try:
        ratio = float(reserve_ratio)
    except (TypeError, ValueError):
        ratio = DEFAULT_RESERVE_RATIO
    ratio = max(0.0, min(0.50, ratio))

    status = quota_status(path_or_data, provider, quota, now=now)
    if quota <= 0:
        return {
            **status,
            "estimated_tokens": estimate,
            "reserve_tokens": 0,
            "spendable_tokens": None,
            "allow_reserve": bool(allow_reserve),
            "admitted": True,
            "reason": "unlimited_or_untracked",
        }

    remaining = int(status["remaining_tokens"] or 0)
    reserve = min(quota, max(0, int(quota * ratio)))
    spendable = remaining if allow_reserve else max(0, remaining - reserve)
    admitted = estimate <= spendable
    if admitted:
        reason = "within_remaining_quota"
    elif allow_reserve:
        reason = "insufficient_remaining_quota"
    elif remaining >= estimate:
        reason = "reserved_for_critical_work"
    else:
        reason = "insufficient_remaining_quota"

    return {
        **status,
        "estimated_tokens": estimate,
        "reserve_tokens": reserve,
        "spendable_tokens": spendable,
        "allow_reserve": bool(allow_reserve),
        "admitted": admitted,
        "reason": reason,
    }
