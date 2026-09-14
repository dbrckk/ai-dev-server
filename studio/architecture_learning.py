"""Aggregate architecture outcome evidence without turning correlation into authority."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from atomic_file import write_text as atomic_write_text
from file_lock import exclusive

MIN_SAMPLES = 5
CONFIDENCE_SAMPLE_TARGET = 20
QUALITY_PRIOR_MEAN = 50.0
QUALITY_PRIOR_STRENGTH = 5.0

def _wilson_lower(successes: int, samples: int, z: float = 1.96) -> float:
    if samples <= 0:
        return 0.0
    p = successes / samples
    z2 = z * z
    denom = 1.0 + z2 / samples
    centre = p + z2 / (2.0 * samples)
    margin = z * ((p * (1.0 - p) / samples + z2 / (4.0 * samples * samples)) ** 0.5)
    return max(0.0, min(1.0, (centre - margin) / denom))

def _confidence(samples: int) -> float:
    if samples <= 0:
        return 0.0
    return round(min(1.0, samples / CONFIDENCE_SAMPLE_TARGET), 4)

def _quality_shrunk_mean(total: float, samples: int) -> float:
    if samples <= 0:
        return QUALITY_PRIOR_MEAN
    return (
        total + QUALITY_PRIOR_MEAN * QUALITY_PRIOR_STRENGTH
    ) / (samples + QUALITY_PRIOR_STRENGTH)



def root_for_output(out: Path | str) -> Path:
    out = Path(out)
    if out.name == "studio-output":
        return out
    if out.parent.name == "studio-output":
        return out.parent
    return out


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
        quality = outcome.get("quality_score")
        quality = max(0.0, min(100.0, float(quality))) if isinstance(quality, (int, float)) else (100.0 if successful else 0.0)

        constraints = row.get("decision_constraints")
        framework = (
            constraints.get("framework")
            if isinstance(constraints, dict) and isinstance(constraints.get("framework"), str)
            else None
        )
        project_type = (
            constraints.get("project_type")
            if isinstance(constraints, dict) and isinstance(constraints.get("project_type"), str)
            else None
        )
        primary_domain = (
            constraints.get("primary_domain")
            if isinstance(constraints, dict) and isinstance(constraints.get("primary_domain"), str)
            else None
        )

        contexts = row.get("chosen_contexts")
        if isinstance(contexts, list) and contexts:
            observed = [
                {
                    "repo": item.get("repo"),
                    "domain": item.get("domain"),
                    "framework": framework,
                    "project_type": project_type,
                    "primary_domain": primary_domain,
                }
                for item in contexts
                if isinstance(item, dict) and isinstance(item.get("repo"), str)
            ]
        else:
            repos = row.get("chosen_repositories")
            observed = [
                {"repo": repo, "domain": None, "framework": framework, "project_type": project_type, "primary_domain": primary_domain}
                for repo in repos
                if isinstance(repos, list) and isinstance(repo, str) and repo
            ] if isinstance(repos, list) else []

        stack_repos = tuple(sorted(item["repo"] for item in observed))
        stack_key = (framework, project_type, primary_domain, stack_repos)
        if stack_repos:
            stack = stack_stats.setdefault(stack_key, {
                "framework": framework,
                "project_type": project_type,
                "primary_domain": primary_domain,
                "repos": list(stack_repos),
                "samples": 0,
                "successes": 0,
                "model_calls": 0,
                "cycles": 0,
                "blockers": 0,
                "quality_total": 0.0,
                "quality_sq_total": 0.0,
                "latest_observed_at": None,
            })
            stack["samples"] += 1
            stack["successes"] += int(successful)
            stack["model_calls"] += calls
            stack["cycles"] += cycles
            stack["blockers"] += blockers
            stack["quality_total"] += quality
            stack["quality_sq_total"] += quality * quality
            if observed_at is not None:
                prev = stack.get("latest_observed_at")
                stack["latest_observed_at"] = observed_at if not isinstance(prev, (int,float)) else max(float(prev), observed_at)

        for observed_item in observed:
            repo = observed_item["repo"]
            domain = observed_item.get("domain")
            item_framework = observed_item.get("framework")
            item_project_type = observed_item.get("project_type")
            item_primary_domain = observed_item.get("primary_domain")
            key = (repo, domain, item_framework, item_project_type, item_primary_domain)
            item = stats.setdefault(key, {
                "repo": repo,
                "domain": domain,
                "framework": item_framework,
                "project_type": item_project_type,
                "primary_domain": item_primary_domain,
                "samples": 0,
                "successes": 0,
                "model_calls": 0,
                "cycles": 0,
                "blockers": 0,
                "quality_total": 0.0,
                "quality_sq_total": 0.0,
                "latest_observed_at": None,
            })
            item["samples"] += 1
            item["successes"] += int(successful)
            item["model_calls"] += calls
            item["cycles"] += cycles
            item["blockers"] += blockers
            item["quality_total"] += quality
            item["quality_sq_total"] += quality * quality
            if observed_at is not None:
                previous_ts = item.get("latest_observed_at")
                item["latest_observed_at"] = (
                    observed_at
                    if not isinstance(previous_ts, (int, float))
                    else max(float(previous_ts), observed_at)
                )

    rankings = []
    for (_repo, _domain, _framework, _project_type, _primary_domain), item in stats.items():
        samples = item["samples"]
        success_rate = item["successes"] / samples if samples else 0.0
        posterior_success = (item["successes"] + 1.0) / (samples + 2.0) if samples >= 0 else 0.5
        wilson_lower = _wilson_lower(item["successes"], samples)
        confidence = _confidence(samples)
        quality_mean = item["quality_total"] / samples if samples else 0.0
        quality_variance = max(0.0, item["quality_sq_total"] / samples - quality_mean * quality_mean) if samples else 0.0
        quality_std = quality_variance ** 0.5
        quality_shrunk = _quality_shrunk_mean(item["quality_total"], samples)
        rankings.append({
            "repo": item["repo"],
            "domain": item.get("domain"),
            "framework": item.get("framework"),
            "project_type": item.get("project_type"),
            "primary_domain": item.get("primary_domain"),
            "samples": samples,
            "successes": item["successes"],
            "success_rate": round(success_rate, 4),
            "posterior_success_rate": round(posterior_success, 4),
            "wilson_lower_95": round(wilson_lower, 4),
            "evidence_confidence": confidence,
            "mean_model_calls": round(item["model_calls"] / samples, 3) if samples else 0.0,
            "mean_cycles": round(item["cycles"] / samples, 3) if samples else 0.0,
            "mean_blockers": round(item["blockers"] / samples, 3) if samples else 0.0,
            "mean_quality_score": round(quality_mean, 3),
            "quality_stddev": round(quality_std, 3),
            "quality_shrunk_mean": round(quality_shrunk, 3),
            "latest_observed_at": item.get("latest_observed_at"),
            "eligible_for_advisory_bias": samples >= MIN_SAMPLES,
        })

    rankings.sort(
        key=lambda x: (
            x["eligible_for_advisory_bias"],
            x["mean_quality_score"],
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
        posterior_success = (item["successes"] + 1.0) / (samples + 2.0) if samples >= 0 else 0.5
        wilson_lower = _wilson_lower(item["successes"], samples)
        confidence = _confidence(samples)
        quality_mean = item["quality_total"] / samples if samples else 0.0
        quality_variance = max(0.0, item["quality_sq_total"] / samples - quality_mean * quality_mean) if samples else 0.0
        quality_std = quality_variance ** 0.5
        quality_shrunk = _quality_shrunk_mean(item["quality_total"], samples)
        stack_rankings.append({
            "repos": item["repos"],
            "framework": item.get("framework"),
            "project_type": item.get("project_type"),
            "primary_domain": item.get("primary_domain"),
            "samples": samples,
            "successes": item["successes"],
            "success_rate": round(success_rate, 4),
            "posterior_success_rate": round(posterior_success, 4),
            "wilson_lower_95": round(wilson_lower, 4),
            "evidence_confidence": confidence,
            "mean_model_calls": round(item["model_calls"] / samples, 3) if samples else 0.0,
            "mean_cycles": round(item["cycles"] / samples, 3) if samples else 0.0,
            "mean_blockers": round(item["blockers"] / samples, 3) if samples else 0.0,
            "mean_quality_score": round(quality_mean, 3),
            "quality_stddev": round(quality_std, 3),
            "quality_shrunk_mean": round(quality_shrunk, 3),
            "latest_observed_at": item.get("latest_observed_at"),
            "eligible_for_advisory_bias": samples >= MIN_SAMPLES,
        })
    stack_rankings.sort(
        key=lambda x: (
            x["eligible_for_advisory_bias"],
            x["mean_quality_score"],
            x["success_rate"],
            -x["mean_blockers"],
            -x["mean_model_calls"],
            x["samples"],
        ),
        reverse=True,
    )

    return {
        "schema": 5,
        "projects_observed": projects,
        "minimum_samples": MIN_SAMPLES,
        "confidence_sample_target": CONFIDENCE_SAMPLE_TARGET,
        "quality_prior_mean": QUALITY_PRIOR_MEAN,
        "quality_prior_strength": QUALITY_PRIOR_STRENGTH,
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
