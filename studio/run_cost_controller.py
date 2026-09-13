"""Run-wide cost controller for bounded autonomous execution."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RunCostController:
    total_budget_seconds: float | None
    max_model_calls: int
    model_seconds: float = 0.0
    agent_seconds: float = 0.0
    verification_seconds: float = 0.0
    review_seconds: float = 0.0
    model_calls: int = 0
    agent_calls: int = 0
    verification_runs: int = 0
    fallbacks: int = 0
    events: list[dict] = field(default_factory=list)

    def _budget(self) -> float:
        return 3600.0 if self.total_budget_seconds is None else max(300.0, float(self.total_budget_seconds))

    def record_model(self, duration: float, *, phase: str) -> None:
        self.model_calls += 1
        self.model_seconds += max(0.0, float(duration))
        self.events.append({"kind":"model","phase":phase,"duration_seconds":max(0.0,float(duration))})

    def record_agent(self, duration: float, *, fallback: bool = True) -> None:
        self.agent_calls += 1
        self.agent_seconds += max(0.0, float(duration))
        if fallback:
            self.fallbacks += 1
        self.events.append({"kind":"agent","duration_seconds":max(0.0,float(duration))})

    def record_verification(self, duration: float) -> None:
        self.verification_runs += 1
        self.verification_seconds += max(0.0, float(duration))
        self.events.append({"kind":"verification","duration_seconds":max(0.0,float(duration))})

    def record_review(self, duration: float) -> None:
        self.review_seconds += max(0.0, float(duration))
        self.events.append({"kind":"review","duration_seconds":max(0.0,float(duration))})

    def decision(self) -> dict:
        budget = self._budget()
        if self.model_calls >= self.max_model_calls:
            return {"action":"verify","reason":"global model-call budget exhausted"}
        if self.model_seconds > budget * 0.45:
            return {"action":"verify","reason":"global model-time budget exceeded"}
        if self.agent_seconds > budget * 0.35:
            return {"action":"verify","reason":"global agent-time budget exceeded"}
        if self.fallbacks >= 4:
            return {"action":"verify","reason":"global fallback budget exhausted"}
        spent = self.model_seconds + self.agent_seconds + self.verification_seconds + self.review_seconds
        if spent > budget * 0.90:
            return {"action":"stop","reason":"global run cost budget nearly exhausted"}
        return {"action":"continue","reason":"within global run cost budget"}

    def snapshot(self) -> dict:
        return {
            "model_seconds": round(self.model_seconds,3),
            "agent_seconds": round(self.agent_seconds,3),
            "verification_seconds": round(self.verification_seconds,3),
            "review_seconds": round(self.review_seconds,3),
            "model_calls": self.model_calls,
            "agent_calls": self.agent_calls,
            "verification_runs": self.verification_runs,
            "fallbacks": self.fallbacks,
            "decision": self.decision(),
        }
