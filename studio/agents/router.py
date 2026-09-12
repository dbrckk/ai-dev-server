"""Capability-based agent routing."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .registry import AgentRegistry, AgentSpec, DEFAULT_REGISTRY


@dataclass(frozen=True)
class RouteDecision:
    agent: AgentSpec
    score: float
    matched: tuple[str, ...]
    missing: tuple[str, ...]


def _score(spec: AgentSpec, required: set[str], prefer_free: bool, long_task: bool) -> RouteDecision:
    matched = sorted(required & set(spec.capabilities))
    missing = sorted(required - set(spec.capabilities))
    coverage = len(matched) / max(1, len(required))
    score = coverage * 100.0 + spec.priority
    if missing:
        score -= 35.0 * len(missing)
    if prefer_free:
        score += 15.0 if spec.free_preferred else -20.0
    if long_task:
        score += 20.0 if spec.long_running else -10.0
    if not spec.available():
        score -= 1000.0
    return RouteDecision(spec, score, tuple(matched), tuple(missing))


def rank_agents(
    required: Iterable[str],
    *,
    registry: AgentRegistry = DEFAULT_REGISTRY,
    prefer_free: bool = True,
    long_task: bool = False,
) -> list[RouteDecision]:
    required_set = {x.strip() for x in required if x and x.strip()}
    decisions = [_score(spec, required_set, prefer_free, long_task) for spec in registry.all()]
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
