"""Enforce fail-closed safety invariants for architecture recommendation automation."""
from __future__ import annotations

import argparse
import json

import architecture_feedback
import architecture_planner
import architecture_evaluator
import architecture_benchmark


def validate() -> dict:
    failures = []

    req = {"target_repo": "owner/app", "app_name": "demo"}
    recs = {
        "matches": [
            {
                "repo": "a/core",
                "score": 90.0,
                "quality_score": 9.0,
                "tier": "core",
                "capabilities": ["testing"],
                "alternatives": ["a/alt"],
            },
            {
                "repo": "a/alt",
                "score": 95.0,
                "quality_score": 9.8,
                "tier": "core",
                "capabilities": ["testing"],
            },
        ]
    }
    learning = {
        "rankings": [
            {
                "repo": "a/core",
                "samples": max(architecture_feedback.MIN_SAMPLES, 5),
                "success_rate": 1.0,
                "mean_model_calls": 2.0,
                "mean_cycles": 1.0,
                "mean_blockers": 0.0,
            }
        ]
    }

    adjusted = architecture_feedback.apply(recs, learning)
    policy = adjusted.get("feedback_policy") or {}
    if policy.get("advisory_only") is not True:
        failures.append("feedback_not_advisory")
    if policy.get("can_add_dependency") is not False:
        failures.append("feedback_can_add_dependency")
    if float(policy.get("max_score_bonus", 999)) > 5.0:
        failures.append("feedback_bonus_too_large")
    max_age = policy.get("max_evidence_age_seconds")
    if not isinstance(max_age, (int, float)) or max_age <= 0 or max_age > 90 * 24 * 60 * 60:
        failures.append("feedback_evidence_age_unbounded")

    decision = architecture_planner.plan(req, recs, learning=learning)
    dep_policy = decision.get("dependency_policy") or {}
    if decision.get("advisory_only") is not True:
        failures.append("planner_not_advisory")
    if dep_policy.get("allow_automatic_dependency_addition") is not False:
        failures.append("planner_allows_dependency_addition")
    if dep_policy.get("require_explicit_approval_or_existing_policy") is not True:
        failures.append("planner_missing_dependency_approval")

    evaluation = architecture_evaluator.evaluate(
        decision,
        {"status": "repair_needed", "blockers": ["testing failed"]},
    )
    eval_policy = evaluation.get("policy") or {}
    if evaluation.get("advisory_only") is not True:
        failures.append("evaluator_not_advisory")
    if eval_policy.get("auto_replace_dependencies") is not False:
        failures.append("evaluator_auto_replaces_dependencies")
    if eval_policy.get("require_benchmark_before_stack_change") is not True:
        failures.append("evaluator_missing_benchmark_requirement")

    benchmark = architecture_benchmark.benchmark(decision, evaluation, recs)
    bench_policy = benchmark.get("policy") or {}
    if benchmark.get("advisory_only") is not True:
        failures.append("benchmark_not_advisory")
    if bench_policy.get("auto_migrate") is not False:
        failures.append("benchmark_auto_migrate_enabled")
    if bench_policy.get("require_isolated_benchmark") is not True:
        failures.append("benchmark_missing_isolated_requirement")
    if bench_policy.get("require_dependency_policy_approval") is not True:
        failures.append("benchmark_missing_dependency_approval")

    return {
        "valid": not failures,
        "failures": failures,
        "policy": {
            "architecture_advisory_only": True,
            "automatic_dependency_addition": False,
            "automatic_migration": False,
            "max_feedback_bonus": architecture_feedback.MAX_SCORE_BONUS,
            "minimum_feedback_samples": architecture_feedback.MIN_SAMPLES,
            "max_feedback_age_seconds": architecture_feedback.MAX_EVIDENCE_AGE_SECONDS,
        },
    }


def main(argv=None) -> int:
    argparse.ArgumentParser(description="Validate architecture automation safety contract").parse_args(argv)
    report = validate()
    print(json.dumps(report, sort_keys=True))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
