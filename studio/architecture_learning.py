"""Aggregate architecture outcome evidence without turning correlation into authority."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

MIN_SAMPLES = 3


def _rows(root: Path):
    for path in sorted(root.glob("*/architecture-outcome.json")):
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            continue
        if isinstance(value, dict):
            yield value


def summarize(root: Path | str = "studio-output") -> dict:
    root = Path(root)
    stats = {}
    projects = 0

    for row in _rows(root):
        projects += 1
        outcome = row.get("outcome")
        if not isinstance(outcome, dict):
            continue
        successful = outcome.get("successful") is True
        calls = max(0, int(outcome.get("model_calls_this_cycle", 0) or 0))
        cycles = max(0, int(outcome.get("cycles", 0) or 0))
        blockers = max(0, int(outcome.get("blocker_count", 0) or 0))

        repos = row.get("chosen_repositories")
        if not isinstance(repos, list):
            continue
        for repo in repos:
            if not isinstance(repo, str) or not repo:
                continue
            item = stats.setdefault(repo, {
                "samples": 0,
                "successes": 0,
                "model_calls": 0,
                "cycles": 0,
                "blockers": 0,
            })
            item["samples"] += 1
            item["successes"] += int(successful)
            item["model_calls"] += calls
            item["cycles"] += cycles
            item["blockers"] += blockers

    rankings = []
    for repo, item in stats.items():
        samples = item["samples"]
        success_rate = item["successes"] / samples if samples else 0.0
        rankings.append({
            "repo": repo,
            "samples": samples,
            "success_rate": round(success_rate, 4),
            "mean_model_calls": round(item["model_calls"] / samples, 3) if samples else 0.0,
            "mean_cycles": round(item["cycles"] / samples, 3) if samples else 0.0,
            "mean_blockers": round(item["blockers"] / samples, 3) if samples else 0.0,
            "eligible_for_advisory_bias": samples >= MIN_SAMPLES,
        })

    rankings.sort(
        key=lambda x: (
            x["eligible_for_advisory_bias"],
            x["success_rate"],
            -x["mean_blockers"],
            -x["mean_model_calls"],
            x["samples"],
        ),
        reverse=True,
    )
    return {
        "schema": 1,
        "projects_observed": projects,
        "minimum_samples": MIN_SAMPLES,
        "advisory_only": True,
        "rankings": rankings,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Aggregate architecture outcome evidence")
    parser.add_argument("--root", default="studio-output")
    args = parser.parse_args(argv)
    print(json.dumps(summarize(args.root), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
