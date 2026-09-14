"""Safe capacity snapshot for reports; never exposes provider keys."""
from __future__ import annotations

from pathlib import Path

from provider_router import load_providers
from provider_monthly_quota import load as load_quota, quota_status


def snapshot(quota_path: Path | None = None) -> dict:
    try:
        providers = load_providers(prefer_free=True)
    except ValueError:
        providers = ()
    quota_data = load_quota(quota_path) if quota_path is not None else {"schema": 1, "months": {}}
    rows = []
    for provider in providers:
        if provider.unmetered:
            mode = "unmetered"
        elif provider.monthly_token_quota > 0:
            mode = "pooled-free"
        else:
            mode = "metered"
        row = {
            "provider": provider.name,
            "mode": mode,
            "free_preferred": provider.free_preferred,
            "model": provider.model,
        }
        if provider.monthly_token_quota > 0:
            row["monthly_quota"] = quota_status(
                quota_data,
                provider.name,
                provider.monthly_token_quota,
            )
        rows.append(row)
    return {
        "providers": rows,
        "unmetered_available": any(row["mode"] == "unmetered" for row in rows),
        "pooled_free_available": any(
            row["mode"] == "pooled-free"
            and not row.get("monthly_quota", {}).get("exhausted", False)
            for row in rows
        ),
        "paid_only": bool(rows) and all(row["mode"] == "metered" for row in rows),
    }
