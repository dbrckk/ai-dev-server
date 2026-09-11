"""Fail-closed validation for synthesized capability candidates."""
from __future__ import annotations

import hashlib
import json
import re

SHA_RE = re.compile(r"[0-9a-f]{64}")


class CapabilityValidationError(ValueError):
    pass


def _canon(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def _validate_candidate(envelope):
    if not isinstance(envelope, dict):
        raise CapabilityValidationError("candidate envelope invalid")
    required = {
        "status", "candidate_id", "candidate_sha256", "candidate",
        "benchmark_status", "regression_status", "promotion_status",
        "capability_registered",
    }
    if set(envelope) != required:
        raise CapabilityValidationError("candidate envelope fields invalid")
    if envelope.get("status") != "candidate_synthesized":
        raise CapabilityValidationError("candidate status invalid")
    candidate = envelope.get("candidate")
    if not isinstance(candidate, dict):
        raise CapabilityValidationError("candidate payload invalid")
    digest = envelope.get("candidate_sha256")
    if not isinstance(digest, str) or not SHA_RE.fullmatch(digest):
        raise CapabilityValidationError("candidate digest invalid")
    if hashlib.sha256(_canon(candidate)).hexdigest() != digest:
        raise CapabilityValidationError("candidate integrity failure")
    if envelope.get("promotion_status") != "not_ready" or envelope.get("capability_registered") is not False:
        raise CapabilityValidationError("candidate trust state invalid")
    return candidate, digest


def validate_candidate(candidate_envelope, targeted_test, benchmark, regression):
    candidate, digest = _validate_candidate(candidate_envelope)
    for name, proof in (
        ("targeted_test", targeted_test),
        ("benchmark", benchmark),
        ("regression", regression),
    ):
        if not isinstance(proof, dict):
            raise CapabilityValidationError(name + " proof invalid")
        if proof.get("candidate_sha256") != digest:
            raise CapabilityValidationError(name + " proof candidate mismatch")
        if proof.get("passed") is not True:
            return {
                "status": "candidate_rejected",
                "candidate_id": candidate_envelope["candidate_id"],
                "candidate_sha256": digest,
                "failed_gate": name,
                "benchmark_status": "passed" if benchmark.get("passed") is True else "failed",
                "regression_status": "passed" if regression.get("passed") is True else "failed",
                "promotion_status": "not_ready",
                "capability_registered": False,
            }

    benchmark_score = benchmark.get("score")
    baseline_score = benchmark.get("baseline_score")
    if not isinstance(benchmark_score, (int, float)) or isinstance(benchmark_score, bool):
        raise CapabilityValidationError("benchmark score invalid")
    if not isinstance(baseline_score, (int, float)) or isinstance(baseline_score, bool):
        raise CapabilityValidationError("benchmark baseline invalid")
    if benchmark_score < baseline_score:
        return {
            "status": "candidate_rejected",
            "candidate_id": candidate_envelope["candidate_id"],
            "candidate_sha256": digest,
            "failed_gate": "benchmark_regression",
            "benchmark_status": "failed",
            "regression_status": "passed",
            "promotion_status": "not_ready",
            "capability_registered": False,
        }

    evidence = {
        "targeted_test_sha256": targeted_test.get("evidence_sha256"),
        "benchmark_sha256": benchmark.get("evidence_sha256"),
        "regression_sha256": regression.get("evidence_sha256"),
    }
    if any(not isinstance(value, str) or not SHA_RE.fullmatch(value) for value in evidence.values()):
        raise CapabilityValidationError("validation evidence digest invalid")

    return {
        "status": "candidate_validated",
        "candidate_id": candidate_envelope["candidate_id"],
        "candidate_sha256": digest,
        "capability": candidate.get("capability"),
        "provider": candidate.get("provider"),
        "benchmark_status": "passed",
        "regression_status": "passed",
        "promotion_status": "eligible",
        "capability_registered": False,
        "evidence": evidence,
    }
