"""Capability-based agent routing."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .registry import AgentRegistry, AgentSpec, DEFAULT_REGISTRY
from adaptive_scoring import score_agent, ScoreTrace
from safe_rewrite_learning import origin_violation_penalty, rewrite_recovery_bonus, exploration_bonus


@dataclass(frozen=True)
class RouteDecision:
    agent: AgentSpec
    score: float
    matched: tuple[str, ...]
    missing: tuple[str, ...]
    trace: dict | None = None


def _score(
    spec: AgentSpec,
    required: set[str],
    prefer_free: bool,
    long_task: bool,
    *,
    reliability: float = 0.0,
    weights: dict[str, float] | None = None,
    safe_rewrite_summary: dict | None = None,
) -> RouteDecision:
    matched = sorted(required & set(spec.capabilities))
    missing = sorted(required - set(spec.capabilities))
    coverage = len(matched) / max(1, len(required))
    capability_fit = coverage * 100.0 - (35.0 * len(missing))
    free_adjustment = (30.0 if spec.free_preferred else -30.0) if prefer_free else 0.0
    long_task_adjustment = (20.0 if spec.long_running else -10.0) if long_task else 0.0
    trace = score_agent(
        name=spec.name,
        capability_fit=capability_fit,
        priority=spec.priority,
        free_adjustment=free_adjustment,
        long_task_adjustment=long_task_adjustment,
        reliability=reliability,
        weights=weights,
    )
    components = dict(trace.components)
    if isinstance(safe_rewrite_summary, dict):
        components["architecture_violation"] = -origin_violation_penalty(
            safe_rewrite_summary,
            kind="agent",
            name=spec.name,
            role="implementation",
        )
        components["safe_rewrite_recovery"] = rewrite_recovery_bonus(
            safe_rewrite_summary,
            kind="agent",
            name=spec.name,
            role="implementation",
        )
        components["architecture_exploration"] = exploration_bonus(
            safe_rewrite_summary,
            kind="agent",
            name=spec.name,
            role="implementation",
        )
        trace = ScoreTrace(
            name=spec.name,
            total=sum(float(value) for value in components.values()),
            components=components,
        )
    score = trace.total
    if not spec.available():
        score -= 1000.0
    trace_data = trace.as_dict()
    if not spec.available():
        trace_data["components"]["availability"] = -1000.0
        trace_data["total"] = round(score, 3)
    return RouteDecision(spec, score, tuple(matched), tuple(missing), trace_data)


def rank_agents(
    required: Iterable[str],
    *,
    registry: AgentRegistry = DEFAULT_REGISTRY,
    prefer_free: bool = True,
    long_task: bool = False,
    reliability: dict[str, float] | None = None,
    weights: dict[str, float] | None = None,
    safe_rewrite_summary: dict | None = None,
) -> list[RouteDecision]:
    required_set = {x.strip() for x in required if x and x.strip()}
    reliability = reliability or {}
    decisions = [
        _score(
            spec,
            required_set,
            prefer_free,
            long_task,
            reliability=float(reliability.get(spec.name, 0.0)),
            weights=weights,
            safe_rewrite_summary=safe_rewrite_summary,
        )
        for spec in registry.all()
    ]
    return sorted(decisions, key=lambda item: (-item.score, item.agent.name))


def choose_agent(
    required: Iterable[str],
    *,
    registry: AgentRegistry = DEFAULT_REGISTRY,
    prefer_free: bool = True,
    long_task: bool = False,
) -> RouteDecision:
    ranked = rank_agents(required, registry=registry, prefer_free=prefer_free, long_task=long_task)
    available = [item for item in ranked if item.agent.available()]
    if not available:
        raise RuntimeError("No registered agent is currently available")
    return available[0]
