"""Controlled dispatch policy for continuous-improvement execution."""
from __future__ import annotations

try:
    from .capability_registry import has_capability, validate as validate_registry
except ImportError:
    from capability_registry import has_capability, validate as validate_registry


BUILTIN_VERIFIERS={"persistent_warning"}
VERIFIER_CAPABILITIES={
    "repeated_failure":"improvement.verify.repeated_failure",
    "capability_churn":"improvement.verify.capability_churn",
}
APPLICATOR_CAPABILITIES={
    "repeated_failure":"improvement.apply.repeated_failure",
    "capability_churn":"improvement.apply.capability_churn",
    "persistent_warning":"improvement.apply.persistent_warning",
}


class ImprovementDispatchError(ValueError):
    pass


def required_verifier_capability(candidate):
    if not isinstance(candidate,dict) or not isinstance(candidate.get("kind"),str):
        raise ImprovementDispatchError("candidate invalid")
    kind=candidate["kind"]
    if kind in BUILTIN_VERIFIERS:
        return None
    capability=VERIFIER_CAPABILITIES.get(kind)
    if capability is None:
        raise ImprovementDispatchError("unsupported improvement kind")
    return capability


def dispatch(candidate,registry):
    validate_registry(registry)
    if not isinstance(candidate,dict) or not isinstance(candidate.get("kind"),str):
        raise ImprovementDispatchError("candidate invalid")
    kind=candidate["kind"]
    applicator=APPLICATOR_CAPABILITIES.get(kind)
    if applicator is None:
        raise ImprovementDispatchError("unsupported improvement kind")
    if not has_capability(registry,applicator):
        return {
            "decision":"adapt",
            "applicator":None,
            "verifier":None,
            "missing_capability":applicator,
        }

    applicator_provider=registry["capabilities"][applicator]["provider"]
    verifier_capability=required_verifier_capability(candidate)
    if verifier_capability is None:
        return {
            "decision":"execute",
            "applicator":applicator_provider,
            "verifier":"builtin",
            "missing_capability":None,
        }
    if has_capability(registry,verifier_capability):
        verifier_provider=registry["capabilities"][verifier_capability]["provider"]
        return {
            "decision":"execute",
            "applicator":applicator_provider,
            "verifier":verifier_provider,
            "missing_capability":None,
        }
    return {
        "decision":"adapt",
        "applicator":applicator_provider,
        "verifier":None,
        "missing_capability":verifier_capability,
    }
