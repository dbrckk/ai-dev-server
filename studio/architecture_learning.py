"""Aggregate architecture outcome evidence without turning correlation into authority."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from atomic_file import write_text as atomic_write_text
from file_lock import exclusive

MIN_SAMPLES = 5


def _rows(root: Path):
    candidates = []
    direct = root / "architecture-outcome.json"
    if direct.is_file():
        candidates.append(direct)
    candidates.extend(sorted(root.glob("*/architecture-outcome.json")))
    for path in candidates:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            continue
        if isinstance(value, dict):
            yield value


def summarize(root: Path | str = "studio-output") -> dict:
    root = Path(root)
    stats = {}
    stack_stats = {}
    projects = 0

    for row in _rows(root):
        projects += 1
        outcome = row.get("outcome")
        if not isinstance(outcome, dict):
            continue
        observed_at = row.get("observed_at")
        observed_at = float(observed_at) if isinstance(observed_at, (int, float)) else None
        successful = outcome.get("successful") is True
        calls = max(0, int(outcome.get("model_calls_this_cycle", 0) or 0))
        cycles = max(0, int(outcome.get("cycles", 0) or 0))
        blockers = max(0, int(outcome.get("blocker_count", 0) or 0))

        contexts = row.get("chosen_contexts")
        if isinstance(contexts, list) and contexts:
            observed = [
                {
                    "repo": item.get("repo"),
                    "domain": item.get("domain"),
                }
                for item in contexts
                if isinstance(item, dict) and isinstance(item.get("repo"), str)
            ]
        else:
            repos = row.get("chosen_repositories")
            observed = [
                {"repo": repo, "domain": None}
                for repo in repos
                if isinstance(repos, list) and isinstance(repo, str) and repo
            ] if isinstance(repos, list) else []

        stack_key = tuple(sorted(item["repo"] for item in observed))
        if stack_key:
            stack = stack_stats.setdefault(stack_key, {
                "repos": list(stack_key),
                "samples": 0,
                "successes": 0,
                "model_calls": 0,
                "cycles": 0,
                "blockers": 0,
                "latest_observed_at": None,
            })
            stack["samples"] += 1
            stack["successes"] += int(successful)
            stack["model_calls"] += calls
            stack["cycles"] += cycles
            stack["blockers"] += blockers
            if observed_at is not None:
                prev = stack.get("latest_observed_at")
                stack["latest_observed_at"] = observed_at if not isinstance(prev, (int,float)) else max(float(prev), observed_at)

        for observed_item in observed:
            repo = observed_item["repo"]
            domain = observed_item.get("domain")
            key = (repo, domain)
            item = stats.setdefault(key, {
                "repo": repo,
                "domain": domain,
                "samples": 0,
                "successes": 0,
                "model_calls": 0,
                "cycles": 0,
                "blockers": 0,
                "latest_observed_at": None,
            })
            item["samples"] += 1
            item["successes"] += int(successful)
            item["model_calls"] += calls
            item["cycles"] += cycles
            item["blockers"] += blockers
            if observed_at is not None:
                previous_ts = item.get("latest_observed_at")
                item["latest_observed_at"] = (
                    observed_at
                    if not isinstance(previous_ts, (int, float))
                    else max(float(previous_ts), observed_at)
                )

    rankings = []
    for (_repo, _domain), item in stats.items():
        samples = item["samples"]
        success_rate = item["successes"] / samples if samples else 0.0
        rankings.append({
            "repo": item["repo"],
            "domain": item.get("domain"),
            "samples": samples,
            "success_rate": round(success_rate, 4),
            "mean_model_calls": round(item["model_calls"] / samples, 3) if samples else 0.0,
            "mean_cycles": round(item["cycles"] / samples, 3) if samples else 0.0,
            "mean_blockers": round(item["blockers"] / samples, 3) if samples else 0.0,
            "latest_observed_at": item.get("latest_observed_at"),
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
    stack_rankings = []
    for _key, item in stack_stats.items():
        samples = item["samples"]
        success_rate = item["successes"] / samples if samples else 0.0
        stack_rankings.append({
            "repos": item["repos"],
            "samples": samples,
            "success_rate": round(success_rate, 4),
            "mean_model_calls": round(item["model_calls"] / samples, 3) if samples else 0.0,
            "mean_cycles": round(item["cycles"] / samples, 3) if samples else 0.0,
            "mean_blockers": round(item["blockers"] / samples, 3) if samples else 0.0,
            "latest_observed_at": item.get("latest_observed_at"),
            "eligible_for_advisory_bias": samples >= MIN_SAMPLES,
        })
    stack_rankings.sort(
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
        "schema": 2,
        "projects_observed": projects,
        "minimum_samples": MIN_SAMPLES,
        "advisory_only": True,
        "rankings": rankings,
        "stack_rankings": stack_rankings[:100],
    }


def write(root: Path | str = "studio-output", path: Path | str | None = None) -> dict:
    root = Path(root)
    path = Path(path) if path is not None else root / "architecture-learning.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with exclusive(path):
        result = summarize(root)
        atomic_write_text(
            path,
            json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Aggregate architecture outcome evidence")
    parser.add_argument("--root", default="studio-output")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    result = write(args.root) if args.write else summarize(args.root)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
