"""Scale autonomous model-call budget from available free capacity."""
from __future__ import annotations

import math

ABSOLUTE_AUTO_CALL_CAP = 240
UNMETERED_MULTIPLIER = 4.0
POOLED_HIGH_MULTIPLIER = 3.0
POOLED_MEDIUM_MULTIPLIER = 2.0


def multiplier(capacity_status: dict) -> float:
    if not isinstance(capacity_status, dict):
        return 1.0
    if capacity_status.get("unmetered_available") is True:
        return UNMETERED_MULTIPLIER

    providers = capacity_status.get("providers")
    if not isinstance(providers, list):
        return 1.0

    best_ratio = 0.0
    for row in providers:
        if not isinstance(row, dict) or row.get("mode") != "pooled-free":
            continue
        quota = row.get("monthly_quota")
        if not isinstance(quota, dict) or quota.get("exhausted") is True:
            continue
        raw_ratio = quota.get("remaining_ratio", 0.0)
        # Quota metadata may be missing or corrupted. NaN compares oddly
        # with min/max and could be promoted to 100% free capacity; Infinity
        # and out-of-range values must never raise the automatic call budget.
        if isinstance(raw_ratio, bool):
            continue
        try:
            ratio = float(raw_ratio)
        except (TypeError, ValueError):
            continue
        if not math.isfinite(ratio) or not 0.0 <= ratio <= 1.0:
            continue
        best_ratio = max(best_ratio, ratio)

    if best_ratio >= 0.50:
        return POOLED_HIGH_MULTIPLIER
    if best_ratio >= 0.10:
        return POOLED_MEDIUM_MULTIPLIER
    return 1.0


def expanded_call_limit(
    base_limit: int,
    capacity_status: dict,
    *,
    explicit_limit: bool,
) -> dict:
    base = max(1, int(base_limit))
    if explicit_limit:
        return {
            "base_limit": base,
            "effective_limit": base,
            "multiplier": 1.0,
            "reason": "explicit_user_limit",
            "absolute_auto_cap": ABSOLUTE_AUTO_CALL_CAP,
        }

    factor = multiplier(capacity_status)
    effective = min(ABSOLUTE_AUTO_CALL_CAP, max(base, int(round(base * factor))))
    if factor >= UNMETERED_MULTIPLIER:
        reason = "unmetered_capacity"
    elif factor > 1.0:
        reason = "pooled_free_capacity"
    else:
        reason = "standard_capacity"

    return {
        "base_limit": base,
        "effective_limit": effective,
        "multiplier": factor,
        "reason": reason,
        "absolute_auto_cap": ABSOLUTE_AUTO_CALL_CAP,
    }
