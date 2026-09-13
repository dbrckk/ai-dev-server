"""Shared adaptive routing score and explainable decision traces."""
from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class ScoreTrace:
    name: str
    total: float
    components: dict[str, float]

    def as_dict(self) -> dict:
        return {"name": self.name, "total": round(self.total, 3), "components": {k: round(v, 3) for k, v in self.components.items()}}


def score_provider(*, name: str, priority: float, free_preferred: bool, reliability: float, latency: float) -> ScoreTrace:
    components = {
        "priority": float(priority),
        "free": 20.0 if free_preferred else 0.0,
        "reliability": float(reliability),
        "latency": float(latency),
    }
    return ScoreTrace(name=name, total=sum(components.values()), components=components)


def score_agent(*, name: str, capability_fit: float, priority: float, free_adjustment: float, long_task_adjustment: float, reliability: float) -> ScoreTrace:
    components = {
        "capability_fit": float(capability_fit),
        "priority": float(priority),
        "free": float(free_adjustment),
        "long_task": float(long_task_adjustment),
        "reliability": float(reliability),
    }
    return ScoreTrace(name=name, total=sum(components.values()), components=components)
