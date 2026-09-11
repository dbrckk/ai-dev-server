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
    capability=required_verifier_capability(candidate)
    if capability is None:
        return {
            "decision":"execute",
            "verifier":"builtin",
            "missing_capability":None,
        }
    if has_capability(registry,capability):
        item=registry["capabilities"][capability]
        return {
            "decision":"execute",
            "verifier":item["provider"],
            "missing_capability":None,
        }
    return {
        "decision":"adapt",
        "verifier":None,
        "missing_capability":capability,
    }
