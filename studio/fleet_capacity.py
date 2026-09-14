"""Build a global capacity plan from the live fleet and configured providers."""
from __future__ import annotations

import json
import os
from pathlib import Path

from atomic_file import write_text as atomic_write_text
from capacity_scheduler import ProviderCapacity, allocate
from durable_state import load_recovering
from fleet_dashboard import collect
from provider_monthly_quota import load as load_monthly_quota, quota_status
from provider_router import load_providers
from queue import matrix


DEFAULT_MAX_TOKENS_PER_MODEL_CALL = 16_000


def _runtime_state(project_out: Path) -> dict:
    path = project_out / ".autonomy" / "runtime-state.json"
    if not path.is_file():
        return {}
    try:
        value = load_recovering(path)
    except Exception:
        return {}
    return value if isinstance(value, dict) else {}


def _project_rows(root: Path, request_dir: Path) -> list[dict]:
    dashboard = collect(root)
    health = {row["id"]: row for row in dashboard.get("projects", [])}
    rows = []
    for request in matrix(request_dir):
        project_id = str(request.get("id") or "").strip()
        if not project_id:
            continue
        current = health.get(project_id, {})
        runtime = _runtime_state(root / project_id)

        status = (
            current.get("runtime_status")
            or runtime.get("status")
            or "queued"
        )
        phase = (
            runtime.get("phase")
            or runtime.get("current_phase")
            or runtime.get("next_stage")
            or request.get("phase")
            or "implementation"
        )
        max_calls = max(1, int(request.get("max_calls", 12)))
        explicit_tokens = request.get("capacity_request_tokens")
        if explicit_tokens is None:
            requested_tokens = max_calls * DEFAULT_MAX_TOKENS_PER_MODEL_CALL
        else:
            requested_tokens = max(1, int(explicit_tokens))

        rows.append({
            "id": project_id,
            "status": status,
            "phase": str(phase),
            "requested_tokens": requested_tokens,
            "priority": max(1, min(100, int(request.get("priority", 50)))),
            "difficulty_band": str(
                runtime.get("difficulty_band")
                or request.get("difficulty_band")
                or "medium"
            ),
        })
    return rows


def _provider_rows() -> list[ProviderCapacity]:
    quota_raw = os.environ.get("STUDIO_PROVIDER_MONTHLY_QUOTA_PATH", "")
    quota_path = Path(quota_raw) if quota_raw else None
    quota_data = (
        load_monthly_quota(quota_path)
        if quota_path is not None
        else {"schema": 1, "months": {}}
    )

    capacities = []
    for provider in load_providers(prefer_free=True):
        available = None
        if provider.monthly_token_quota > 0:
            available = quota_status(
                quota_data,
                provider.name,
                provider.monthly_token_quota,
            )["remaining_tokens"]
        capacities.append(ProviderCapacity(
            name=provider.name,
            available_tokens=available,
            unmetered=provider.unmetered,
            free_preferred=provider.free_preferred,
            paid=(
                not provider.unmetered
                and provider.monthly_token_quota <= 0
                and (
                    provider.input_cost_per_million > 0
                    or provider.output_cost_per_million > 0
                    or not provider.free_preferred
                )
            ),
        ))
    return capacities


def plan(
    root: Path | str = "studio-output",
    request_dir: Path | str = "control/mobile-requests",
    *,
    critical_reserve_ratio: float = 0.10,
) -> dict:
    root = Path(root)
    request_dir = Path(request_dir)
    projects = _project_rows(root, request_dir)
    providers = _provider_rows()
    report = allocate(
        projects,
        providers,
        critical_reserve_ratio=critical_reserve_ratio,
    )
    report["provider_capacity"] = [
        {
            "name": item.name,
            "available_tokens": item.available_tokens,
            "unmetered": item.unmetered,
            "free_preferred": item.free_preferred,
            "paid": item.paid,
            "capacity_known": item.unmetered or item.available_tokens is not None,
        }
        for item in providers
    ]
    report["summary"]["providers"] = len(providers)
    report["summary"]["providers_with_known_capacity"] = sum(
        1 for item in providers
        if item.unmetered or item.available_tokens is not None
    )
    return report


def persist(
    root: Path | str = "studio-output",
    request_dir: Path | str = "control/mobile-requests",
    *,
    critical_reserve_ratio: float = 0.10,
    output: Path | str | None = None,
) -> dict:
    root = Path(root)
    report = plan(
        root,
        request_dir,
        critical_reserve_ratio=critical_reserve_ratio,
    )
    target = Path(output) if output is not None else root / "capacity-plan.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_text(
        target,
        json.dumps(report, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return report
