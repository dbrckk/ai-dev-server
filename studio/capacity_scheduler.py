"""Global capacity scheduler for autonomous multi-project execution.

This module stays deterministic and side-effect free except for its CLI output.
It allocates token envelopes across active projects and assigns provider classes
in the preferred order: local/unmetered, pooled free quota, remote free, paid.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path


CRITICAL_PHASES = {"verification", "tests", "review", "security_fix", "release_fix"}
ACTIVE_STATES = {"running", "deferred", "failed", "queued", "pending"}


@dataclass(frozen=True)
class ProviderCapacity:
    name: str
    available_tokens: int | None
    unmetered: bool = False
    free_preferred: bool = True
    paid: bool = False

    @property
    def tier(self) -> int:
        if self.unmetered:
            return 0
        if self.free_preferred and not self.paid:
            return 1
        if not self.paid:
            return 2
        return 3


def _clean_project(row: dict) -> dict | None:
    if not isinstance(row, dict):
        return None
    project_id = str(row.get("id") or "").strip()
    if not project_id:
        return None
    status = str(row.get("status") or row.get("runtime_status") or "running")
    if status not in ACTIVE_STATES:
        return None
    phase = str(row.get("phase") or "implementation")
    requested = max(1, int(row.get("requested_tokens", 1)))
    priority = max(1, min(100, int(row.get("priority", 50))))
    difficulty = str(row.get("difficulty_band") or "medium")
    critical = bool(row.get("critical")) or phase in CRITICAL_PHASES
    return {
        "id": project_id,
        "status": status,
        "phase": phase,
        "requested_tokens": requested,
        "priority": priority,
        "difficulty_band": difficulty,
        "critical": critical,
    }


def _weight(project: dict) -> float:
    difficulty_bonus = {
        "low": 1.00,
        "medium": 1.10,
        "high": 1.20,
        "very_high": 1.30,
    }.get(project["difficulty_band"], 1.10)
    critical_bonus = 1.45 if project["critical"] else 1.0
    failure_bonus = 1.15 if project["status"] == "failed" else 1.0
    return max(0.01, project["priority"] * difficulty_bonus * critical_bonus * failure_bonus)


def _finite_capacity(providers: list[ProviderCapacity]) -> int:
    return sum(
        max(0, int(provider.available_tokens or 0))
        for provider in providers
        if not provider.unmetered
    )


def allocate(
    projects: list[dict],
    providers: list[ProviderCapacity],
    *,
    critical_reserve_ratio: float = 0.10,
) -> dict:
    """Allocate project envelopes and provider order for one scheduling cycle."""
    cleaned = [item for row in projects if (item := _clean_project(row)) is not None]
    ordered_providers = sorted(providers, key=lambda p: (p.tier, p.name))
    has_unmetered = any(p.unmetered for p in ordered_providers)

    try:
        reserve_ratio = float(critical_reserve_ratio)
    except (TypeError, ValueError):
        reserve_ratio = 0.10
    reserve_ratio = max(0.0, min(0.50, reserve_ratio))

    finite = _finite_capacity(ordered_providers)
    reserve = int(finite * reserve_ratio)
    ordinary_pool = max(0, finite - reserve)

    total_weight = sum(_weight(project) for project in cleaned) or 1.0
    allocations = []

    for project in cleaned:
        weight = _weight(project)
        requested = project["requested_tokens"]

        if has_unmetered:
            envelope = requested
            constrained = False
        else:
            pool = finite if project["critical"] else ordinary_pool
            fair_share = int(pool * (weight / total_weight))
            envelope = min(requested, max(0, fair_share))
            constrained = envelope < requested

        provider_order = []
        for provider in ordered_providers:
            available = None if provider.unmetered else max(0, int(provider.available_tokens or 0))
            if available == 0 and not provider.unmetered:
                continue
            provider_order.append({
                "name": provider.name,
                "tier": provider.tier,
                "unmetered": provider.unmetered,
                "free_preferred": provider.free_preferred,
                "paid": provider.paid,
                "available_tokens": available,
            })

        allocations.append({
            **project,
            "weight": round(weight, 3),
            "token_envelope": envelope,
            "constrained": constrained,
            "provider_order": provider_order,
        })

    allocations.sort(
        key=lambda row: (
            not row["critical"],
            -row["priority"],
            -row["weight"],
            row["id"],
        )
    )

    return {
        "schema": 1,
        "critical_reserve_ratio": round(reserve_ratio, 4),
        "finite_capacity_tokens": finite,
        "critical_reserve_tokens": reserve,
        "ordinary_capacity_tokens": ordinary_pool,
        "has_unmetered_capacity": has_unmetered,
        "projects": allocations,
        "summary": {
            "active_projects": len(allocations),
            "critical_projects": sum(1 for row in allocations if row["critical"]),
            "constrained_projects": sum(1 for row in allocations if row["constrained"]),
            "requested_tokens": sum(row["requested_tokens"] for row in allocations),
            "allocated_tokens": sum(row["token_envelope"] for row in allocations),
        },
    }


def provider_capacities(rows: list[dict]) -> list[ProviderCapacity]:
    result = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        name = str(row.get("name") or "").strip()
        if not name:
            continue
        unmetered = bool(row.get("unmetered"))
        raw_available = row.get("available_tokens")
        available = None if unmetered else max(0, int(raw_available or 0))
        result.append(ProviderCapacity(
            name=name,
            available_tokens=available,
            unmetered=unmetered,
            free_preferred=bool(row.get("free_preferred", True)),
            paid=bool(row.get("paid", False)),
        ))
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="AI Dev Server global capacity scheduler")
    parser.add_argument("--projects", required=True, help="JSON file containing a projects array")
    parser.add_argument("--providers", required=True, help="JSON file containing a providers array")
    parser.add_argument("--critical-reserve-ratio", type=float, default=0.10)
    parser.add_argument("--output", default="")
    args = parser.parse_args(argv)

    projects_payload = json.loads(Path(args.projects).read_text(encoding="utf-8"))
    providers_payload = json.loads(Path(args.providers).read_text(encoding="utf-8"))
    projects = projects_payload.get("projects", []) if isinstance(projects_payload, dict) else projects_payload
    provider_rows = providers_payload.get("providers", []) if isinstance(providers_payload, dict) else providers_payload

    report = allocate(
        list(projects),
        provider_capacities(list(provider_rows)),
        critical_reserve_ratio=args.critical_reserve_ratio,
    )
    rendered = json.dumps(report, sort_keys=True, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
