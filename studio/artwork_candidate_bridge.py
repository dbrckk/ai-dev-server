"""Bridge a trusted merged artwork provider into the generic candidate validator."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

try:
    from .artwork_validation import validate_artwork_provider
    from .capability_candidate_validator import validate_candidate
except ImportError:
    from artwork_validation import validate_artwork_provider
    from capability_candidate_validator import validate_candidate


class ArtworkCandidateBridgeError(ValueError):
    pass


def _canon(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def build_artwork_candidate(provider_path: Path, tests_path: Path):
    provider_path = Path(provider_path)
    tests_path = Path(tests_path)
    for label, path in (("provider", provider_path), ("tests", tests_path)):
        if not path.is_file() or path.is_symlink():
            raise ArtworkCandidateBridgeError(label + " source unavailable")

    try:
        implementation = provider_path.read_text(encoding="utf-8")
        tests = tests_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        raise ArtworkCandidateBridgeError("candidate source unreadable") from None
    if not implementation.strip() or not tests.strip():
        raise ArtworkCandidateBridgeError("candidate source empty")

    proof_bundle = validate_artwork_provider(provider_path)
    if proof_bundle.get("status") != "artwork_candidate_validated":
        raise ArtworkCandidateBridgeError("artwork proof bundle not validated")
    source_sha = hashlib.sha256(implementation.encode("utf-8")).hexdigest()
    if proof_bundle.get("provider_source_sha256") != source_sha:
        raise ArtworkCandidateBridgeError("artwork source proof mismatch")

    payload = {
        "version": 1,
        "capability": "asset_artwork",
        "provider": "studio.capabilities.asset_artwork",
        "implementation": implementation,
        "tests": tests,
        "risk_notes": [
            "Deterministic SVG output only",
            "No network, filesystem writes, subprocesses or registry mutation",
            "Promotion requires generic validation and source-controlled registry update",
        ],
        "research": [{
            "kind": "trusted_merged_implementation",
            "provider_source_sha256": source_sha,
            "validation_bundle": "studio.artwork_validation",
        }],
    }
    digest = hashlib.sha256(_canon(payload)).hexdigest()
    envelope = {
        "status": "candidate_synthesized",
        "candidate_id": "capability-candidate:asset_artwork:" + digest[:16],
        "candidate_sha256": digest,
        "candidate": payload,
        "benchmark_status": "required",
        "regression_status": "required",
        "promotion_status": "not_ready",
        "capability_registered": False,
    }

    def bind(proof):
        if not isinstance(proof, dict):
            raise ArtworkCandidateBridgeError("artwork proof invalid")
        value = dict(proof)
        value["candidate_sha256"] = digest
        return value

    validation = validate_candidate(
        envelope,
        bind(proof_bundle["targeted_test"]),
        bind(proof_bundle["benchmark"]),
        bind(proof_bundle["regression"]),
    )
    if validation.get("status") != "candidate_validated":
        raise ArtworkCandidateBridgeError("generic candidate validation failed")
    return envelope, validation
