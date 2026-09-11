"""Synthesize isolated capability candidates from sealed research evidence."""
from __future__ import annotations

import hashlib
import json
import re

try:
    from .project_memory import query, validate as validate_memory
except ImportError:
    from project_memory import query, validate as validate_memory


NAME_RE = re.compile(r"[a-z][a-z0-9_.-]{2,80}")
PROVIDER_RE = re.compile(r"studio\.capabilities\.[a-z][a-z0-9_]{2,120}")


class CapabilitySynthesisError(ValueError):
    pass


def _canon(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def _research_for(memory, project_id, capability):
    validate_memory(memory)
    candidate_id = "capability:" + capability
    items = query(memory, project_id=project_id, kind="research")
    matched = []
    for item in items:
        evidence = item.get("evidence")
        if isinstance(evidence, dict) and evidence.get("candidate_id") == candidate_id:
            matched.append(item)
    if len(matched) < 2:
        raise CapabilitySynthesisError("insufficient sealed research for capability")
    return matched


def synthesize_candidate(memory, project_id, capability, synthesizer):
    if not isinstance(project_id, str) or not project_id.strip():
        raise CapabilitySynthesisError("project id invalid")
    if not isinstance(capability, str) or not NAME_RE.fullmatch(capability):
        raise CapabilitySynthesisError("capability invalid")
    if not callable(synthesizer):
        raise CapabilitySynthesisError("synthesizer invalid")

    research = _research_for(memory, project_id, capability)
    research_refs = [{
        "entry_id": item["id"],
        "content_sha256": item["evidence"]["content_sha256"],
        "item_sha256": item["evidence"]["item_sha256"],
        "source": item["provenance"]["source"],
    } for item in research]

    proposal = synthesizer({
        "capability": capability,
        "research": research_refs,
        "constraints": {
            "no_promotion": True,
            "no_registry_mutation": True,
            "tests_required": True,
            "regression_required": True,
        },
    })
    if not isinstance(proposal, dict):
        raise CapabilitySynthesisError("candidate proposal invalid")

    allowed = {"provider", "implementation", "tests", "risk_notes"}
    if set(proposal) != allowed:
        raise CapabilitySynthesisError("candidate proposal fields invalid")
    provider = proposal.get("provider")
    implementation = proposal.get("implementation")
    tests = proposal.get("tests")
    risk_notes = proposal.get("risk_notes")

    if not isinstance(provider, str) or not PROVIDER_RE.fullmatch(provider):
        raise CapabilitySynthesisError("candidate provider invalid")
    if not isinstance(implementation, str) or not implementation.strip() or len(implementation) > 200_000:
        raise CapabilitySynthesisError("candidate implementation invalid")
    if not isinstance(tests, str) or not tests.strip() or len(tests) > 120_000:
        raise CapabilitySynthesisError("candidate tests invalid")
    if not isinstance(risk_notes, list) or any(not isinstance(x, str) or not x.strip() for x in risk_notes):
        raise CapabilitySynthesisError("candidate risk notes invalid")

    payload = {
        "version": 1,
        "capability": capability,
        "provider": provider,
        "implementation": implementation,
        "tests": tests,
        "risk_notes": risk_notes,
        "research": research_refs,
    }
    digest = hashlib.sha256(_canon(payload)).hexdigest()
    return {
        "status": "candidate_synthesized",
        "candidate_id": "capability-candidate:" + capability + ":" + digest[:16],
        "candidate_sha256": digest,
        "candidate": payload,
        "benchmark_status": "required",
        "regression_status": "required",
        "promotion_status": "not_ready",
        "capability_registered": False,
    }


def validate_candidate_envelope(envelope):
    if not isinstance(envelope,dict):
        raise CapabilitySynthesisError("candidate envelope invalid")
    required={
        "status","candidate_id","candidate_sha256","candidate",
        "benchmark_status","regression_status","promotion_status","capability_registered",
    }
    if set(envelope)!=required or envelope.get("status")!="candidate_synthesized":
        raise CapabilitySynthesisError("candidate envelope fields invalid")
    candidate=envelope.get("candidate")
    digest=envelope.get("candidate_sha256")
    if not isinstance(candidate,dict) or not isinstance(digest,str) or not re.fullmatch(r"[0-9a-f]{64}",digest):
        raise CapabilitySynthesisError("candidate envelope payload invalid")
    if hashlib.sha256(_canon(candidate)).hexdigest()!=digest:
        raise CapabilitySynthesisError("candidate envelope integrity failure")
    capability=candidate.get("capability")
    if not isinstance(capability,str) or not NAME_RE.fullmatch(capability):
        raise CapabilitySynthesisError("candidate capability invalid")
    expected_id="capability-candidate:"+capability+":"+digest[:16]
    if envelope.get("candidate_id")!=expected_id:
        raise CapabilitySynthesisError("candidate envelope identity mismatch")
    if envelope.get("benchmark_status")!="required" or envelope.get("regression_status")!="required":
        raise CapabilitySynthesisError("candidate validation gates invalid")
    if envelope.get("promotion_status")!="not_ready" or envelope.get("capability_registered") is not False:
        raise CapabilitySynthesisError("candidate trust state invalid")
    return envelope
