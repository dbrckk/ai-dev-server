"""Meta-router CLI combining agent selection with star-list discovery."""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass

from agents.router import rank_agents
from star_scanner import scan
from strategy_efficiency import select_strategy


MIN_EVENTS = 6
MIN_GAP = 0.20


@dataclass(frozen=True)
class MetaRoute:
    mode: str
    agent_limit: int
    confidence: float
    reason: str
    strategy: str = "dual"

    def as_dict(self) -> dict:
        return {
            "mode": self.mode,
            "agent_limit": self.agent_limit,
            "confidence": round(self.confidence, 3),
            "reason": self.reason,
            "strategy": self.strategy,
        }


def _rate(events: list[dict], kind: str, role: str) -> tuple[int, float]:
    rows = [event for event in events if event.get("kind") == kind and event.get("role") == role]
    if not rows:
        return 0, 0.0
    success = sum(1 for event in rows if event.get("success") is True)
    return len(rows), success / len(rows)


def choose_execution_mode(events: list[dict], *, role: str, agent_available: bool, strategy_data: dict | None = None) -> MetaRoute:
    if not agent_available:
        return MetaRoute("model_only", 0, 1.0, "no eligible external agent", "model_only")
    if isinstance(strategy_data, dict):
        selected = select_strategy(
            strategy_data,
            allowed={"model_only","agent_only","model_to_agent","agent_to_model","dual"},
        )
        if selected is not None:
            strategy, info = selected
            confidence = min(1.0, float(info["samples"]) / 12.0)
            mapping = {
                "model_only": ("model_only", 0),
                "agent_only": ("agent_focus", 1),
                "model_to_agent": ("model_focus", 1),
                "agent_to_model": ("agent_focus", 1),
                "dual": ("dual", 2),
            }
            mode, limit = mapping[strategy]
            return MetaRoute(
                mode,
                limit,
                confidence,
                "bounded strategy " + str(info.get("selection_mode","exploit")) + " by verified-success efficiency",
                strategy,
            )
    agent_n, agent_rate = _rate(events, "agent", role)
    provider_n, provider_rate = _rate(events, "model_candidate", role)
    if agent_n < MIN_EVENTS or provider_n < MIN_EVENTS:
        return MetaRoute("dual", 2, 0.0, "insufficient comparative evidence", "dual")
    gap = agent_rate - provider_rate
    confidence = min(1.0, min(agent_n, provider_n) / 20.0)
    if gap >= MIN_GAP:
        return MetaRoute("agent_focus", 2, confidence, "verified agent success rate materially higher", "agent_to_model")
    if gap <= -MIN_GAP:
        return MetaRoute("model_focus", 1, confidence, "verified model-candidate success rate materially higher", "model_to_agent")
    return MetaRoute("dual", 2, confidence, "success rates are too close for specialization", "dual")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--capability", action="append", default=[])
    parser.add_argument("--long-task", action="store_true")
    parser.add_argument("--allow-paid", action="store_true")
    parser.add_argument("--skip-stars", action="store_true")
    args = parser.parse_args()

    decisions = rank_agents(
        args.capability,
        prefer_free=not args.allow_paid,
        long_task=args.long_task,
    )
    payload = {
        "capabilities": args.capability,
        "agents": [
            {
                "name": item.agent.name,
                "available": item.agent.available(),
                "score": round(item.score, 2),
                "matched": item.matched,
                "missing": item.missing,
            }
            for item in decisions
        ],
    }
    if not args.skip_stars:
        try:
            payload["star_list"] = scan(args.capability)
        except Exception as exc:
            payload["star_list"] = {"status": "unavailable", "error": str(exc)}
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
