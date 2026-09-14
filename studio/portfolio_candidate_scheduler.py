"""Bounded scheduler for speculative implementation portfolios."""
from __future__ import annotations

from dataclasses import dataclass

MAX_CANDIDATES = 3


@dataclass(frozen=True)
class PortfolioSchedule:
    candidate_limit: int
    agent_limit: int
    model_limit: int
    include_model: bool
    continue_after_verified: bool
    uncertainty: float
    free_capacity: float
    verification_pressure: float
    reason: str

    def as_dict(self) -> dict:
        return {
            "candidate_limit": self.candidate_limit,
            "agent_limit": self.agent_limit,
            "model_limit": self.model_limit,
            "include_model": self.include_model,
            "continue_after_verified": self.continue_after_verified,
            "uncertainty": round(self.uncertainty, 4),
            "free_capacity": round(self.free_capacity, 4),
            "verification_pressure": round(self.verification_pressure, 4),
            "reason": self.reason,
        }


def _free_capacity(status: dict) -> float:
    if not isinstance(status, dict):
        return 0.0
    if status.get("unmetered_available") is True:
        return 1.0
    best = 0.0
    rows = status.get("providers")
    if isinstance(rows, list):
        for row in rows:
            if not isinstance(row, dict) or row.get("mode") != "pooled-free":
                continue
            quota = row.get("monthly_quota")
            if not isinstance(quota, dict) or quota.get("exhausted") is True:
                continue
            try:
                best = max(best, float(quota.get("remaining_ratio", 0.0) or 0.0))
            except (TypeError, ValueError):
                pass
    return max(0.0, min(1.0, best))


def choose_schedule(
    *,
    capacity_status: dict,
    route_confidence: float,
    verification_seconds: float | None,
    remaining_seconds: float | None,
    available_agents: int,
    strategy: str,
    available_models: int = 1,
    recommended_width: int | None = None,
) -> PortfolioSchedule:
    confidence = max(0.0, min(1.0, float(route_confidence or 0.0)))
    uncertainty = 1.0 - confidence
    available_agents = max(0, int(available_agents))
    available_models = max(0, int(available_models))
    available_candidate_count = available_agents + available_models
    capacity = _free_capacity(capacity_status)
    verification = max(0.0, float(verification_seconds or 0.0))
    verification_pressure = min(1.0, verification / 300.0)

    candidate_limit = 1
    reason = "single candidate is sufficient"

    enough_time_for_two = remaining_seconds is None or remaining_seconds >= max(180.0, verification * 2.0)
    enough_time_for_three = remaining_seconds is None or remaining_seconds >= max(360.0, verification * 3.0)

    if (
        uncertainty >= 0.35
        and capacity >= 0.45
        and verification <= 300.0
        and enough_time_for_two
    ):
        candidate_limit = 2
        reason = "uncertain route with abundant low-cost capacity"
    if (
        uncertainty >= 0.60
        and capacity >= 0.80
        and verification <= 120.0
        and enough_time_for_three
        and available_candidate_count >= 3
    ):
        candidate_limit = 3
        reason = "high uncertainty, abundant free capacity, cheap verification"

    include_model = strategy != "agent_only" and available_models > 0

    if recommended_width is not None:
        try:
            learned_width = max(1, min(MAX_CANDIDATES, int(recommended_width)))
        except (TypeError, ValueError):
            learned_width = candidate_limit
        # Historical learning may reduce speculative breadth, but cannot widen
        # a run beyond current safety/capacity conditions.
        candidate_limit = min(candidate_limit, learned_width)

    if strategy == "agent_only":
        model_limit = 0
        agent_limit = min(available_agents, candidate_limit)
    elif strategy == "model_only":
        agent_limit = 0
        model_limit = min(available_models, candidate_limit)
    else:
        # Prefer heterogeneous portfolios: model+agent at width 2, and
        # two independent direct models plus one agent at width 3.
        if candidate_limit >= 3 and available_models >= 2 and available_agents >= 1:
            model_limit = 2
            agent_limit = 1
        elif candidate_limit >= 3 and available_models >= 1 and available_agents >= 2:
            model_limit = 1
            agent_limit = 2
        elif candidate_limit >= 2 and available_models >= 1 and available_agents >= 1:
            model_limit = 1
            agent_limit = 1
        else:
            model_limit = min(available_models, candidate_limit)
            agent_limit = min(available_agents, max(0, candidate_limit - model_limit))
            if model_limit + agent_limit < candidate_limit:
                agent_limit += min(
                    available_agents - agent_limit,
                    candidate_limit - model_limit - agent_limit,
                )

    actual_capacity = model_limit + agent_limit
    candidate_limit = max(1, min(MAX_CANDIDATES, candidate_limit, max(1, actual_capacity)))
    model_limit = min(model_limit, candidate_limit)
    agent_limit = min(agent_limit, max(0, candidate_limit - model_limit))
    continue_after_verified = candidate_limit > 1 and uncertainty >= 0.35 and capacity >= 0.45

    return PortfolioSchedule(
        candidate_limit=candidate_limit,
        agent_limit=agent_limit,
        model_limit=model_limit,
        include_model=include_model,
        continue_after_verified=continue_after_verified,
        uncertainty=uncertainty,
        free_capacity=capacity,
        verification_pressure=verification_pressure,
        reason=reason,
    )
