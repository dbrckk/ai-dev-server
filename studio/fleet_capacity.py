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
from capacity_ledger import detailed_snapshot as ledger_detailed_snapshot, load as load_capacity_ledger, preemption_leases
from capacity_efficiency import summarize as summarize_capacity_efficiency, project_multiplier as efficiency_multiplier
from stagnation_controller import summarize as summarize_stagnation
from recovery_controller import evaluate as evaluate_recovery
from global_admission import decide as decide_global_admission
from preemption_controller import plan as plan_preemption
from execution_checkpoint import load as load_execution_checkpoint, ExecutionCheckpointError
from queue import matrix
from worker_reliability import summarize as summarize_worker_reliability, project_multiplier as reliability_multiplier


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


def _project_rows(
    root: Path,
    request_dir: Path,
    *,
    ledger_usage: dict | None = None,
    previous_plan: dict | None = None,
    efficiency_summary: dict | None = None,
    stagnation_summary: dict | None = None,
    recovery_state_path: Path | None = None,
    provider_context: list[dict] | None = None,
    reliability_summary: dict | None = None,
) -> list[dict]:
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

        usage = (ledger_usage or {}).get(project_id, {})
        committed = max(0, int(usage.get("committed_tokens", 0) or 0))
        previous_rows = (
            previous_plan.get("projects", [])
            if isinstance(previous_plan, dict)
            and isinstance(previous_plan.get("projects"), list)
            else []
        )
        previous_envelope = next(
            (
                int(row.get("token_envelope", 0) or 0)
                for row in previous_rows
                if isinstance(row, dict) and row.get("id") == project_id
            ),
            0,
        )
        pressure = (
            min(1.5, committed / previous_envelope)
            if previous_envelope > 0
            else 0.0
        )
        verified_efficiency_multiplier = efficiency_multiplier(
            efficiency_summary or {},
            project_id,
        )
        worker_reliability_multiplier = reliability_multiplier(
            reliability_summary or {},
            project_id,
        )
        reliability_project = (
            (reliability_summary or {}).get("projects", {}).get(project_id, {})
            if isinstance((reliability_summary or {}).get("projects", {}), dict)
            else {}
        )
        efficiency_project = (
            (efficiency_summary or {}).get("projects", {}).get(project_id, {})
            if isinstance((efficiency_summary or {}).get("projects", {}), dict)
            else {}
        )
        predicted_success_probability = max(
            0.05,
            min(
                0.95,
                float(
                    efficiency_project.get("predicted_success_probability", 0.50)
                    or 0.50
                ),
            ),
        )
        stagnation = (
            (stagnation_summary or {}).get("projects", {}).get(project_id, {})
            if isinstance((stagnation_summary or {}).get("projects", {}), dict)
            else {}
        )
        stagnation_multiplier = max(
            0.0,
            min(1.0, float(stagnation.get("capacity_multiplier", 1.0) or 0.0)),
        )
        capacity_paused = bool(stagnation.get("pause", False))
        recovery = {
            "recover": False,
            "capacity_multiplier": 0.0,
            "force_diversify": False,
            "reason": "recovery_disabled",
        }
        if recovery_state_path is not None:
            recovery_context = {
                "base_sha": str(
                    runtime.get("base_sha")
                    or runtime.get("checkpoint_commit")
                    or runtime.get("last_commit")
                    or ""
                ),
                "phase": str(phase),
                "providers": provider_context or [],
            }
            recovery = evaluate_recovery(
                recovery_state_path,
                project_id=project_id,
                paused=capacity_paused,
                context=recovery_context,
            )
            if capacity_paused and recovery.get("recover") is True:
                capacity_paused = False
                stagnation_multiplier = max(
                    stagnation_multiplier,
                    float(recovery.get("capacity_multiplier", 0.15) or 0.15),
                )

        rows.append({
            "id": project_id,
            "status": status,
            "phase": str(phase),
            "requested_tokens": max(requested_tokens, committed),
            "priority": max(1, min(100, int(request.get("priority", 50)))),
            "difficulty_band": str(
                runtime.get("difficulty_band")
                or request.get("difficulty_band")
                or "medium"
            ),
            "capacity_pressure": round(pressure, 4),
            "efficiency_multiplier": verified_efficiency_multiplier,
            "reliability_multiplier": worker_reliability_multiplier,
            "worker_reliability_score": round(
                float(reliability_project.get("reliability_score", 0.5) or 0.5), 6
            ),
            "worker_reliability_samples": int(reliability_project.get("samples", 0) or 0),
            "predicted_success_probability": round(predicted_success_probability, 6),
            "stagnation_multiplier": stagnation_multiplier,
            "capacity_paused": capacity_paused,
            "stagnation_level": str(stagnation.get("level") or "normal"),
            "force_diversify": bool(stagnation.get("force_diversify", False))
            or bool(recovery.get("force_diversify", False)),
            "recovery_active": bool(recovery.get("recover", False)),
            "recovery_reason": str(recovery.get("reason") or ""),
            "committed_tokens": committed,
            "previous_envelope_tokens": previous_envelope,
        })
    return rows


def _preemption_evidence(root: Path, projects: list[dict]) -> dict:
    evidence = {}
    for row in projects:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str):
            continue
        project_id = row["id"]
        checkpoint_path = root / project_id / ".autonomy" / "execution-checkpoint.json"
        item = {"checkpoint_valid": False, "checkpoint_phase": None}
        if checkpoint_path.is_file():
            try:
                checkpoint = load_execution_checkpoint(checkpoint_path)
            except (OSError, ExecutionCheckpointError):
                checkpoint = None
            if isinstance(checkpoint, dict):
                item = {
                    "checkpoint_valid": True,
                    "checkpoint_phase": checkpoint.get("phase"),
                    "checkpoint_round": checkpoint.get("round"),
                    "checkpoint_base_sha": checkpoint.get("base_sha"),
                }
        evidence[project_id] = item
    return evidence


def _capacity_band(value: int | None, *, unmetered: bool = False) -> str:
    if unmetered:
        return "unmetered"
    if value is None:
        return "unknown"
    amount = max(0, int(value))
    if amount == 0:
        return "exhausted"
    if amount < 32_000:
        return "low"
    if amount < 1_000_000:
        return "normal"
    return "high"


def _provider_rows(
    *,
    reservations_by_provider: dict | None = None,
    quota_path: Path | None = None,
) -> list[ProviderCapacity]:
    if quota_path is None:
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
            reserved = max(
                0,
                int((reservations_by_provider or {}).get(provider.name, 0) or 0),
            )
            available = max(0, int(available or 0) - reserved)
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
    plan_path = root / "capacity-plan.json"
    try:
        previous_plan = json.loads(plan_path.read_text(encoding="utf-8")) if plan_path.is_file() else {}
    except (OSError, UnicodeError, json.JSONDecodeError):
        previous_plan = {}
    ledger = ledger_detailed_snapshot(root / "capacity-ledger.json")
    efficiency = summarize_capacity_efficiency(root / "capacity-efficiency.json")
    stagnation = summarize_stagnation(efficiency)
    try:
        liveness = json.loads((root / "worker-liveness.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        liveness = {}
    reliability = summarize_worker_reliability(liveness)
    providers = _provider_rows(
        reservations_by_provider=ledger.get("reservations_by_provider", {}),
        quota_path=root / "provider-monthly-quota.json",
    )
    provider_context = [
        {
            "name": item.name,
            "capacity_band": _capacity_band(
                item.available_tokens,
                unmetered=item.unmetered,
            ),
            "unmetered": item.unmetered,
            "paid": item.paid,
        }
        for item in providers
    ]
    projects = _project_rows(
        root,
        request_dir,
        ledger_usage=ledger.get("usage_by_project", {}),
        previous_plan=previous_plan,
        efficiency_summary=efficiency,
        stagnation_summary=stagnation,
        recovery_state_path=root / "recovery-state.json",
        provider_context=provider_context,
        reliability_summary=reliability,
    )
    report = allocate(
        projects,
        providers,
        critical_reserve_ratio=critical_reserve_ratio,
    )
    admission = decide_global_admission(report["projects"])
    active_leases = preemption_leases(load_capacity_ledger(root / "capacity-ledger.json"))
    if active_leases:
        decisions = admission.get("decisions", [])
        for decision in decisions:
            if not isinstance(decision, dict):
                continue
            lease = active_leases.get(decision.get("id"))
            if lease is None:
                continue
            decision["admitted"] = True
            decision["action"] = "admit_preemption_lease"
            decision["reason"] = "transactional_preemption_lease"
            decision["preemption_lease"] = lease
        admission["summary"]["admitted"] = sum(
            1 for row in decisions if isinstance(row, dict) and row.get("admitted") is True
        )
        admission["summary"]["deferred"] = sum(
            1 for row in decisions if isinstance(row, dict) and row.get("admitted") is False
        )
    admission_by_id = {
        row["id"]: row
        for row in admission["decisions"]
        if isinstance(row, dict) and isinstance(row.get("id"), str)
    }
    for row in report["projects"]:
        decision = admission_by_id.get(row["id"], {})
        row["admission"] = decision
        row["admitted"] = decision.get("admitted") is True
    preemption_evidence = _preemption_evidence(root, report["projects"])
    report["preemption"] = plan_preemption(report, preemption_evidence)
    report["summary"]["preemption_candidates"] = int(report["preemption"]["summary"]["preempt"])
    report["summary"]["preemption_blocked"] = int(report["preemption"]["summary"]["blocked"])
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
    report["admission"] = admission
    report["summary"]["admitted_projects"] = int(admission["summary"]["admitted"])
    report["summary"]["deferred_by_admission"] = int(admission["summary"]["deferred"])
    report["rebalance"] = {
        "previous_plan_present": bool(previous_plan),
        "active_reservations": int(ledger.get("active_reservations", 0) or 0),
        "reserved_tokens": int(ledger.get("reserved_tokens", 0) or 0),
        "consumed_tokens": int(ledger.get("consumed_tokens", 0) or 0),
        "reaped_reservations": int(ledger.get("reaped", 0) or 0),
        "pressured_projects": sum(
            1 for row in report["projects"]
            if float(row.get("capacity_pressure", 0.0) or 0.0) >= 0.80
        ),
        "efficiency_evidence_projects": len(efficiency.get("projects", {})),
        "efficiency_boosted_projects": sum(
            1 for row in report["projects"]
            if float(row.get("efficiency_multiplier", 1.0) or 1.0) > 1.0
        ),
        "reliability_evidence_projects": len(reliability.get("projects", {})),
        "reliability_reduced_projects": sum(
            1 for row in report["projects"]
            if float(row.get("reliability_multiplier", 1.0) or 1.0) < 1.0
        ),
        "efficiency_reduced_projects": sum(
            1 for row in report["projects"]
            if float(row.get("efficiency_multiplier", 1.0) or 1.0) < 1.0
        ),
        "stagnation_paused_projects": int(stagnation.get("paused_projects", 0) or 0),
        "stagnation_throttled_projects": int(stagnation.get("throttled_projects", 0) or 0),
        "stagnation_diversifying_projects": int(stagnation.get("diversifying_projects", 0) or 0),
        "recovery_active_projects": sum(
            1 for row in report["projects"]
            if row.get("recovery_active") is True
        ),
    }
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
