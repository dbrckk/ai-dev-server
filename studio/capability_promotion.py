"""Controlled promotion of fully validated capability candidates."""
from __future__ import annotations

import copy
import re

try:
    from .promoted_capabilities import provider_for
except ImportError:
    from promoted_capabilities import provider_for


COMMIT_RE = re.compile(r"[0-9a-f]{40}")
DIGEST_RE = re.compile(r"[0-9a-f]{64}")


class CapabilityPromotionError(ValueError):
    pass


def _validate_registry_doc(value):
    if not isinstance(value, dict) or value.get("version") != 1 or not isinstance(value.get("capabilities"), dict):
        raise CapabilityPromotionError("promoted registry invalid")
    if set(value) != {"version", "capabilities"}:
        raise CapabilityPromotionError("promoted registry fields invalid")
    return value


def promote_candidate(registry_doc, candidate_envelope, validation, baseline_sha, candidate_commit_sha):
    _validate_registry_doc(registry_doc)

    if not isinstance(candidate_envelope, dict):
        raise CapabilityPromotionError("candidate envelope invalid")
    if not isinstance(validation, dict):
        raise CapabilityPromotionError("validation result invalid")

    if validation.get("status") != "candidate_validated":
        raise CapabilityPromotionError("candidate not validated")
    if validation.get("promotion_status") != "eligible":
        raise CapabilityPromotionError("candidate not eligible")
    if validation.get("capability_registered") is not False:
        raise CapabilityPromotionError("candidate already registered")

    candidate_id = candidate_envelope.get("candidate_id")
    candidate_sha256 = candidate_envelope.get("candidate_sha256")
    payload = candidate_envelope.get("candidate")
    if not isinstance(candidate_id, str) or not candidate_id:
        raise CapabilityPromotionError("candidate id invalid")
    if not isinstance(candidate_sha256, str) or not DIGEST_RE.fullmatch(candidate_sha256):
        raise CapabilityPromotionError("candidate digest invalid")
    if not isinstance(payload, dict):
        raise CapabilityPromotionError("candidate payload invalid")

    if validation.get("candidate_id") != candidate_id:
        raise CapabilityPromotionError("validation candidate id mismatch")
    if validation.get("candidate_sha256") != candidate_sha256:
        raise CapabilityPromotionError("validation candidate digest mismatch")

    capability = payload.get("capability")
    provider = payload.get("provider")
    if not isinstance(capability, str) or not capability:
        raise CapabilityPromotionError("candidate capability invalid")
    if provider != provider_for(capability):
        raise CapabilityPromotionError("candidate provider is not deterministic")
    if validation.get("capability") != capability or validation.get("provider") != provider:
        raise CapabilityPromotionError("validation candidate metadata mismatch")

    evidence = validation.get("evidence")
    required_evidence = {"targeted_test_sha256", "benchmark_sha256", "regression_sha256"}
    if not isinstance(evidence, dict) or set(evidence) != required_evidence:
        raise CapabilityPromotionError("validation evidence incomplete")
    if any(not isinstance(value, str) or not DIGEST_RE.fullmatch(value) for value in evidence.values()):
        raise CapabilityPromotionError("validation evidence digest invalid")

    for name, value in (("baseline", baseline_sha), ("candidate", candidate_commit_sha)):
        if not isinstance(value, str) or not COMMIT_RE.fullmatch(value):
            raise CapabilityPromotionError(name + " commit invalid")
    if baseline_sha == candidate_commit_sha:
        raise CapabilityPromotionError("candidate commit must differ from baseline")

    existing = registry_doc["capabilities"].get(capability)
    entry = {
        "provider": provider,
        "candidate_id": candidate_id,
        "baseline_sha": baseline_sha,
        "candidate_sha": candidate_commit_sha,
    }
    if existing is not None:
        if existing == entry:
            return copy.deepcopy(registry_doc), {
                "status": "already_promoted",
                "capability": capability,
                "promotion_status": "promoted",
                "capability_registered": False,
            }
        raise CapabilityPromotionError("promoted capability conflict")

    updated = copy.deepcopy(registry_doc)
    updated["capabilities"][capability] = entry
    return updated, {
        "status": "promotion_prepared",
        "capability": capability,
        "provider": provider,
        "candidate_id": candidate_id,
        "candidate_sha256": candidate_sha256,
        "promotion_status": "promoted_registry_ready",
        "capability_registered": False,
        "validation_evidence": dict(evidence),
    }
