"""Classify generic verification failures and map them to bounded recovery policies."""
from __future__ import annotations

import re

from user_input_required import extract_secret_names

DEPENDENCY_PATTERNS = (
    "module not found",
    "modulenotfounderror",
    "cannot find module",
    "no module named",
    "could not resolve",
    "failed to resolve",
    "dependency",
    "package not found",
    "could not find artifact",
    "could not find package",
    "lock file",
    "lockfile",
)

COMPILE_PATTERNS = (
    "syntaxerror",
    "syntax error",
    "compile error",
    "compilation failed",
    "cannot compile",
    "type error",
    "typeerror",
    "undefined reference",
    "unresolved reference",
    "cannot find symbol",
)

TEST_PATTERNS = (
    "assertionerror",
    "assertion failed",
    "test failed",
    "tests failed",
    "failed test",
    "expected",
)

ENVIRONMENT_PATTERNS = (
    "permission denied",
    "operation not permitted",
    "no space left on device",
    "read-only file system",
    "command not found",
    "executable file not found",
    "unsupported platform",
    "requires docker",
)

REGRESSION_PATTERNS = (
    "regression",
    "snapshot mismatch",
    "golden mismatch",
    "baseline mismatch",
)

EXTERNAL_PREREQUISITE_PATTERNS = (
    "api key required",
    "missing api key",
    "token required",
    "missing token",
    "secret required",
    "missing secret",
    "environment variable is required",
    "environment variable required",
    "environment variable is not set",
    "environment variable not set",
    "required environment variable",
)

_TIMEOUT_CODES = {124, 137, 143}


def _failed_result(verification: dict) -> dict | None:
    results = verification.get("results", [])
    if not isinstance(results, list):
        return None
    for item in results:
        if isinstance(item, dict) and item.get("passed") is not True:
            return item
    return None


def _text(result: dict | None) -> str:
    if not isinstance(result, dict):
        return ""
    return re.sub(r"\s+", " ", str(result.get("log_tail", ""))).strip().lower()


def classify(verification: dict | None, *, changed_files: list[str] | None = None, progress: dict | None = None) -> dict:
    if verification is None:
        return {
            "category": "no_history",
            "confidence": "high",
            "reason": "no previous verification exists for this project run",
            "recovery": "start",
        }
    if not isinstance(verification, dict):
        return {
            "category": "unknown_failure",
            "confidence": "low",
            "reason": "verification evidence is invalid",
            "recovery": "replan",
        }
    if isinstance(progress, dict):
        progress_status = progress.get("status")
        if progress_status == "regression":
            return {
                "category": "regression",
                "confidence": "high",
                "reason": "repository progress evidence shows verification regressed from passing to failing",
                "recovery": "revert_or_target_regression",
            }
        if progress_status in {"no_progress", "churn_without_verified_progress"}:
            return {
                "category": "no_progress",
                "confidence": "high",
                "reason": "repository delta did not improve trusted verification evidence",
                "recovery": "switch_strategy",
            }

    if verification.get("passed") is True:
        return {
            "category": "passed",
            "confidence": "high",
            "reason": "trusted verification passed",
            "recovery": "continue",
        }

    status = str(verification.get("status", "")).lower()
    result = _failed_result(verification)
    log = _text(result)
    rc = result.get("returncode") if isinstance(result, dict) else None
    changed_files_known = changed_files is not None
    changed_files = changed_files or []

    if status == "no_verifier":
        return {
            "category": "environment_failure",
            "confidence": "high",
            "reason": "no trusted verifier was available",
            "recovery": "synthesize_verifier",
        }

    secret_names = extract_secret_names(
        str(result.get("log_tail", "")) if isinstance(result, dict) else ""
    )
    if secret_names and any(pattern in log for pattern in EXTERNAL_PREREQUISITE_PATTERNS):
        return {
            "category": "external_prerequisite",
            "confidence": "high",
            "reason": "verification requires an explicit external secret/environment prerequisite",
            "recovery": "request_external_input",
            "required_env": secret_names,
        }

    if rc in _TIMEOUT_CODES or "timeoutexpired" in log or "timed out" in log or "timeout" in log:
        return {
            "category": "timeout",
            "confidence": "high",
            "reason": "verification exceeded its execution bound or was terminated",
            "recovery": "reduce_scope_or_timeout",
        }

    if any(pattern in log for pattern in DEPENDENCY_PATTERNS):
        return {
            "category": "dependency_failure",
            "confidence": "high",
            "reason": "verification evidence indicates unresolved or inconsistent dependencies",
            "recovery": "repair_dependencies",
        }

    if any(pattern in log for pattern in ENVIRONMENT_PATTERNS):
        return {
            "category": "environment_failure",
            "confidence": "high",
            "reason": "verification failed because the execution environment could not satisfy a prerequisite",
            "recovery": "repair_environment_or_defer",
        }

    if any(pattern in log for pattern in REGRESSION_PATTERNS):
        return {
            "category": "regression",
            "confidence": "high",
            "reason": "verification reports a baseline or regression mismatch",
            "recovery": "revert_or_target_regression",
        }

    if any(pattern in log for pattern in COMPILE_PATTERNS):
        return {
            "category": "compile_failure",
            "confidence": "high",
            "reason": "verification failed during compilation, parsing, typing or linking",
            "recovery": "repair_compile",
        }

    if any(pattern in log for pattern in TEST_PATTERNS):
        return {
            "category": "test_failure",
            "confidence": "medium",
            "reason": "verification evidence indicates functional test failure",
            "recovery": "repair_tests_or_behavior",
        }

    if changed_files_known and not changed_files:
        return {
            "category": "no_progress",
            "confidence": "medium",
            "reason": "verification failed and the round produced no source changes",
            "recovery": "switch_strategy",
        }

    return {
        "category": "unknown_failure",
        "confidence": "low",
        "reason": "failure evidence did not match a trusted classification rule",
        "recovery": "replan",
    }


def policy(classification: dict, *, repeated_failures: int = 1) -> dict:
    category = classification.get("category")
    repeated = max(0, int(repeated_failures))

    if category in {"passed", "no_history"}:
        return {"action": "continue", "priority": "normal", "provider_switch": False}
    if category == "dependency_failure":
        return {"action": "repair_dependencies", "priority": "high", "provider_switch": repeated >= 2}
    if category == "compile_failure":
        return {"action": "repair_compile", "priority": "high", "provider_switch": repeated >= 2}
    if category == "test_failure":
        return {"action": "repair_behavior", "priority": "high", "provider_switch": repeated >= 2}
    if category == "regression":
        return {"action": "target_regression", "priority": "critical", "provider_switch": repeated >= 2}
    if category == "timeout":
        return {"action": "reduce_scope", "priority": "high", "provider_switch": True}
    if category == "environment_failure":
        return {"action": "repair_environment_or_defer", "priority": "critical", "provider_switch": False}
    if category == "external_prerequisite":
        return {"action": "request_external_input", "priority": "critical", "provider_switch": False}
    if category == "no_progress":
        return {"action": "switch_strategy", "priority": "critical", "provider_switch": True}
    return {"action": "replan", "priority": "high", "provider_switch": repeated >= 2}
