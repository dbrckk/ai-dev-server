"""Global capacity scheduler for autonomous multi-project execution.

This module stays deterministic and side-effect free except for its CLI output.
It allocates token envelopes across active projects and assigns provider classes
in the preferred order: local/unmetered, pooled free quota, remote free, paid.
"""
from __future__ import annotations

import argparse
import json
import time
from dataclasses import dataclass
from pathlib import Path

import provider_health


CRITICAL_PHASES = {"verification", "tests", "review", "security_fix", "release_fix"}
ACTIVE_STATES = {"running", "deferred", "failed", "queued", "pending"}


@dataclass(frozen=True)
class ProviderCapacity:
    name: str
    available_tokens: int | None
    unmetered: bool = False
    free_preferred: bool = True
    paid: bool = False
    reliability: float = 0.5
    latency_ms: float | None = None
    cost_per_million_tokens: float = 0.0
    circuit_open: bool = False
    observations: int = 0

    @property
    def tier(self) -> int:
        if self.unmetered:
            return 0
        if self.free_preferred and not self.paid:
            return 1
        if not self.paid:
            return 2
        return 3

    @property
    def adaptive_score(self) -> float:
        """Higher is better; preserve free-first policy while ranking peers by evidence."""
        reliability = max(0.0, min(1.0, float(self.reliability)))
        latency = 1000.0 if self.latency_ms is None else max(0.0, float(self.latency_ms))
        latency_score = 1.0 / (1.0 + latency / 1000.0)
        cost = max(0.0, float(self.cost_per_million_tokens))
        cost_score = 1.0 / (1.0 + cost)
        availability = 1.0 if self.unmetered else min(1.0, max(0.0, float(self.available_tokens or 0)) / 1_000_000.0)
        return (0.55 * reliability) + (0.20 * latency_score) + (0.15 * availability) + (0.10 * cost_score)


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
    try:
        pressure = float(row.get("capacity_pressure", 0.0) or 0.0)
    except (TypeError, ValueError):
        pressure = 0.0
    pressure = max(0.0, min(1.5, pressure))
    try:
        efficiency = float(row.get("efficiency_multiplier", 1.0) or 1.0)
    except (TypeError, ValueError):
        efficiency = 1.0
    efficiency = max(0.75, min(1.25, efficiency))
    try:
        stagnation = float(row.get("stagnation_multiplier", 1.0) or 0.0)
    except (TypeError, ValueError):
        stagnation = 1.0
    stagnation = max(0.0, min(1.0, stagnation))
    paused = bool(row.get("capacity_paused", False))
    return {
        "id": project_id,
        "status": status,
        "phase": phase,
        "requested_tokens": requested,
        "priority": priority,
        "difficulty_band": difficulty,
        "critical": critical,
        "capacity_pressure": round(pressure, 4),
        "efficiency_multiplier": round(efficiency, 4),
        "stagnation_multiplier": round(stagnation, 4),
        "capacity_paused": paused,
        "stagnation_level": str(row.get("stagnation_level") or "normal"),
        "force_diversify": bool(row.get("force_diversify", False)),
        "recovery_active": bool(row.get("recovery_active", False)),
        "recovery_reason": str(row.get("recovery_reason") or ""),
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
    pressure_bonus = 1.0 + min(0.60, project.get("capacity_pressure", 0.0) * 0.40)
    efficiency_bonus = max(0.75, min(1.25, project.get("efficiency_multiplier", 1.0)))
    stagnation_multiplier = max(0.0, min(1.0, project.get("stagnation_multiplier", 1.0)))
    return max(
        0.01,
        project["priority"]
        * difficulty_bonus
        * critical_bonus
        * failure_bonus
        * pressure_bonus
        * efficiency_bonus
        * stagnation_multiplier,
    )


def _finite_capacity(providers: list[ProviderCapacity]) -> int:
    return sum(
        max(0, int(provider.available_tokens or 0))
        for provider in providers
        if not provider.unmetered
    )


def _weighted_work_conserving(projects: list[dict], capacity: int) -> dict[str, int]:
    """Distribute finite capacity by weight without stranding capacity at capped peers."""
    remaining = max(0, int(capacity))
    allocations = {project["id"]: 0 for project in projects}
    pending = [
        project
        for project in projects
        if not project.get("capacity_paused") and int(project.get("_max_envelope", 0)) > 0
    ]

    while remaining > 0 and pending:
        total_weight = sum(_weight(project) for project in pending) or 1.0
        available_at_start = remaining
        progressed = 0

        for project in list(pending):
            project_id = project["id"]
            cap = max(0, int(project.get("_max_envelope", 0)))
            room = max(0, cap - allocations[project_id])
            if room == 0:
                pending.remove(project)
                continue

            share = max(1, int(available_at_start * (_weight(project) / total_weight)))
            grant = min(room, share, remaining)
            allocations[project_id] += grant
            remaining -= grant
            progressed += grant
            if allocations[project_id] >= cap:
                pending.remove(project)
            if remaining <= 0:
                break

        if progressed == 0:
            break

    return allocations


def allocate(
    projects: list[dict],
    providers: list[ProviderCapacity],
    *,
    critical_reserve_ratio: float = 0.10,
    exploration_strength: float = 0.08,
) -> dict:
    """Allocate project envelopes and provider order for one scheduling cycle."""
    cleaned = [item for row in projects if (item := _clean_project(row)) is not None]
    try:
        explore = max(0.0, min(0.25, float(exploration_strength)))
    except (TypeError, ValueError):
        explore = 0.08

    def routing_score(provider: ProviderCapacity) -> float:
        # Deterministic uncertainty bonus: new/under-observed peers get bounded
        # opportunities to prove themselves without random routing or tier bypass.
        uncertainty = 1.0 / (1.0 + max(0, int(provider.observations))) ** 0.5
        return provider.adaptive_score + explore * uncertainty

    ordered_providers = sorted(
        (provider for provider in providers if not provider.circuit_open),
        key=lambda p: (p.tier, -routing_score(p), p.name),
    )
    has_unmetered = any(p.unmetered for p in ordered_providers)

    try:
        reserve_ratio = float(critical_reserve_ratio)
    except (TypeError, ValueError):
        reserve_ratio = 0.10
    reserve_ratio = max(0.0, min(0.50, reserve_ratio))

    finite = _finite_capacity(ordered_providers)
    reserve = int(finite * reserve_ratio)
    ordinary_pool = max(0, finite - reserve)

    prepared = []
    for project in cleaned:
        requested = project["requested_tokens"]
        stagnation_cap = max(
            0,
            int(requested * max(
                0.0,
                min(1.0, float(project.get("stagnation_multiplier", 1.0) or 0.0)),
            )),
        )
        prepared.append({
            **project,
            "_max_envelope": min(requested, stagnation_cap),
        })

    reserve_allocations: dict[str, int] = {project["id"]: 0 for project in prepared}
    shared_allocations: dict[str, int] = {project["id"]: 0 for project in prepared}

    if not has_unmetered:
        critical_projects = [project for project in prepared if project["critical"]]
        reserve_allocations.update(_weighted_work_conserving(critical_projects, reserve))

        shared_projects = []
        for project in prepared:
            already_reserved = reserve_allocations.get(project["id"], 0)
            shared_projects.append({
                **project,
                "_max_envelope": max(0, int(project["_max_envelope"]) - already_reserved),
            })
        shared_allocations = _weighted_work_conserving(shared_projects, ordinary_pool)

    allocations = []
    for project in prepared:
        weight = _weight(project)
        requested = project["requested_tokens"]
        max_envelope = int(project["_max_envelope"])

        if project.get("capacity_paused"):
            envelope = 0
            constrained = True
        elif has_unmetered:
            envelope = max_envelope
            constrained = envelope < requested
        else:
            envelope = min(
                max_envelope,
                reserve_allocations.get(project["id"], 0)
                + shared_allocations.get(project["id"], 0),
            )
            constrained = envelope < requested

        provider_order = []
        for provider in ordered_providers:
            available = (
                None
                if provider.available_tokens is None
                else max(0, int(provider.available_tokens))
            )
            if available == 0 and not provider.unmetered:
                continue
            provider_order.append({
                "name": provider.name,
                "tier": provider.tier,
                "unmetered": provider.unmetered,
                "free_preferred": provider.free_preferred,
                "paid": provider.paid,
                "available_tokens": available,
                "reliability": round(provider.reliability, 4),
                "latency_ms": provider.latency_ms,
                "cost_per_million_tokens": round(provider.cost_per_million_tokens, 6),
                "adaptive_score": round(provider.adaptive_score, 6),
                "observations": provider.observations,
                "exploration_bonus": round(
                    explore / (1.0 + max(0, provider.observations)) ** 0.5, 6
                ),
                "routing_score": round(routing_score(provider), 6),
            })

        allocations.append({
            **{key: value for key, value in project.items() if not key.startswith("_")},
            "weight": round(weight, 3),
            "token_envelope": envelope,
            "constrained": constrained,
            "capacity_pressure": project.get("capacity_pressure", 0.0),
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
        "exploration_strength": round(explore, 4),
        "finite_capacity_tokens": finite,
        "critical_reserve_tokens": reserve,
        "ordinary_capacity_tokens": ordinary_pool,
        "has_unmetered_capacity": has_unmetered,
        "projects": allocations,
        "summary": {
            "active_projects": len(allocations),
            "critical_projects": sum(1 for row in allocations if row["critical"]),
            "constrained_projects": sum(1 for row in allocations if row["constrained"]),
            "paused_projects": sum(1 for row in allocations if row.get("capacity_paused")),
            "requested_tokens": sum(row["requested_tokens"] for row in allocations),
            "allocated_tokens": sum(row["token_envelope"] for row in allocations),
        },
    }


def provider_capacities(
    rows: list[dict], *, health_data: dict | None = None, now: float | None = None
) -> list[ProviderCapacity]:
    current_time = time.time() if now is None else float(now)
    result = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        name = str(row.get("name") or "").strip()
        if not name:
            continue
        unmetered = bool(row.get("unmetered"))
        raw_available = row.get("available_tokens")
        if unmetered or raw_available is None:
            available = None
        else:
            available = max(0, int(raw_available))
        empirical = (health_data or {}).get(name)
        if "reliability" in row:
            try:
                reliability = float(row.get("reliability", 0.5))
            except (TypeError, ValueError):
                reliability = 0.5
        elif isinstance(empirical, dict):
            try:
                successes = max(0, int(empirical.get("successes", 0)))
                failures = max(0, int(empirical.get("failures", 0)))
            except (TypeError, ValueError):
                successes = failures = 0
            # Beta(1,1) smoothing prevents tiny samples from dominating routing.
            reliability = (successes + 1) / (successes + failures + 2)
        else:
            reliability = 0.5
        reliability = max(0.0, min(1.0, reliability))
        raw_latency = row.get("latency_ms")
        if raw_latency is None and isinstance(empirical, dict):
            raw_latency = empirical.get("latency_ms_ema")
        try:
            latency = None if raw_latency is None else max(0.0, float(raw_latency))
        except (TypeError, ValueError):
            latency = None
        try:
            cost = max(0.0, float(row.get("cost_per_million_tokens", 0.0) or 0.0))
        except (TypeError, ValueError):
            cost = 0.0
        circuit_open = False
        if isinstance(empirical, dict):
            try:
                circuit_open = float(empirical.get("opened_until", 0.0) or 0.0) > current_time
            except (TypeError, ValueError):
                circuit_open = False
        result.append(ProviderCapacity(
            name=name,
            available_tokens=available,
            unmetered=unmetered,
            free_preferred=bool(row.get("free_preferred", True)),
            paid=bool(row.get("paid", False)),
            reliability=reliability,
            latency_ms=latency,
            cost_per_million_tokens=cost,
            circuit_open=circuit_open,
            observations=(
                max(0, int(empirical.get("successes", 0) or 0))
                + max(0, int(empirical.get("failures", 0) or 0))
                if isinstance(empirical, dict) else 0
            ),
        ))
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="AI Dev Server global capacity scheduler")
    parser.add_argument("--projects", required=True, help="JSON file containing a projects array")
    parser.add_argument("--providers", required=True, help="JSON file containing a providers array")
    parser.add_argument("--critical-reserve-ratio", type=float, default=0.10)
    parser.add_argument("--output", default="")
    parser.add_argument("--provider-health", default="", help="Optional provider-health JSON state")
    args = parser.parse_args(argv)

    projects_payload = json.loads(Path(args.projects).read_text(encoding="utf-8"))
    providers_payload = json.loads(Path(args.providers).read_text(encoding="utf-8"))
    projects = projects_payload.get("projects", []) if isinstance(projects_payload, dict) else projects_payload
    provider_rows = providers_payload.get("providers", []) if isinstance(providers_payload, dict) else providers_payload

    health_data = provider_health.load(Path(args.provider_health)) if args.provider_health else {}
    report = allocate(
        list(projects),
        provider_capacities(list(provider_rows), health_data=health_data),
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
