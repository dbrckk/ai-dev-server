"""Meta-router CLI combining agent selection with star-list discovery."""
from __future__ import annotations

import argparse
import json

from agents.router import rank_agents
from star_scanner import scan


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
