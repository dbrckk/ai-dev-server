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


def choose_execution_mode(
    events: list[dict],
    *,
    role: str,
    agent_available: bool,
    strategy_data: dict | None = None,
    safe_rewrite_summary: dict | None = None,
    force_diversify: bool = False,
) -> MetaRoute:
    if not agent_available:
        return MetaRoute("model_only", 0, 1.0, "no eligible external agent", "model_only")
    if force_diversify:
        return MetaRoute(
            "dual",
            2,
            1.0,
            "stagnation controller forced independent strategy diversification",
            "dual",
        )
    architecture_bias = 0.0
    if role == "implementation" and isinstance(safe_rewrite_summary, dict):
        origins = safe_rewrite_summary.get("origin_rankings")
        if isinstance(origins, list):
            agent_rows = [row for row in origins if row.get("kind") == "agent" and row.get("eligible_for_routing_bias") is True]
            provider_rows = [row for row in origins if row.get("kind") == "provider" and row.get("eligible_for_routing_bias") is True]
            if agent_rows and provider_rows:
                agent_rate = sum(float(row.get("verification_pass_rate", 0.0)) for row in agent_rows) / len(agent_rows)
                provider_rate = sum(float(row.get("verification_pass_rate", 0.0)) for row in provider_rows) / len(provider_rows)
                architecture_bias = max(-0.25, min(0.25, agent_rate - provider_rate))

    if isinstance(strategy_data, dict):
        selected = select_strategy(
            strategy_data,
            allowed={"model_only","agent_only","model_to_agent","agent_to_model","dual"},
        )
        if selected is not None:
            strategy, info = selected
            confidence = min(
                1.0,
                (float(info["samples"]) / 12.0) * (1.0 - float(info.get("uncertainty", 0.0))),
            )
            mapping = {
                "model_only": ("model_only", 0),
                "agent_only": ("agent_focus", 1),
                "model_to_agent": ("model_focus", 1),
                "agent_to_model": ("agent_focus", 1),
                "dual": ("dual", 2),
            }
            mode, limit = mapping[strategy]
            if role == "implementation" and architecture_bias <= -MIN_GAP and mode == "agent_focus":
                mode, limit, strategy = "dual", 1, "dual"
            return MetaRoute(
                mode,
                limit,
                confidence,
                "bounded strategy " + str(info.get("selection_mode","exploit")) + " by verified-success efficiency"
                + ("; architecture discipline reduced agent focus" if role == "implementation" and architecture_bias <= -MIN_GAP else ""),
                strategy,
            )
    agent_n, agent_rate = _rate(events, "agent", role)
    provider_n, provider_rate = _rate(events, "model_candidate", role)
    if agent_n < MIN_EVENTS or provider_n < MIN_EVENTS:
        return MetaRoute("dual", 2, 0.0, "insufficient comparative evidence", "dual")
    gap = (agent_rate - provider_rate) + architecture_bias
    confidence = min(1.0, min(agent_n, provider_n) / 20.0)
    if (
        role == "implementation"
        and architecture_bias <= -MIN_GAP
        and gap >= MIN_GAP
    ):
        return MetaRoute(
            "dual",
            1,
            confidence,
            "agent success is higher but architecture discipline requires independent model fallback",
            "dual",
        )
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
