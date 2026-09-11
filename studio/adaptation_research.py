"""Fail-closed bridge from missing capabilities to researched adaptation evidence."""
from __future__ import annotations

try:
    from .autonomous_research import run_and_remember
    from .capability_registry import validate as validate_registry
except ImportError:
    from autonomous_research import run_and_remember
    from capability_registry import validate as validate_registry


class AdaptationResearchError(ValueError):
    pass


def research_missing_capability(
    memory,
    registry,
    project_id,
    capability,
    search_provider,
    fetch_provider,
    *,
    min_sources=2,
):
    validate_registry(registry)
    if not isinstance(project_id, str) or not project_id.strip():
        raise AdaptationResearchError("project id invalid")
    if not isinstance(capability, str) or not capability.strip() or len(capability) > 120:
        raise AdaptationResearchError("capability invalid")

    candidate_id = "capability:" + capability
    objective = "Research implementation and security constraints for missing capability " + capability
    updated_memory, research = run_and_remember(
        memory,
        project_id,
        candidate_id,
        objective,
        search_provider,
        fetch_provider,
        min_sources=min_sources,
    )

    if research.get("status") != "research_complete":
        return updated_memory, registry, {
            "status": "adaptation_required",
            "missing_capability": capability,
            "research_status": research.get("status"),
            "synthesis_status": "not_started",
            "promotion_status": "not_ready",
            "next_action": "research_more",
            "capability_registered": False,
        }

    return updated_memory, registry, {
        "status": "adaptation_required",
        "missing_capability": capability,
        "research_status": "research_complete",
        "research_candidate_id": candidate_id,
        "research_items": len(research["items"]),
        "synthesis_status": "required",
        "promotion_status": "not_ready",
        "next_action": "synthesize_candidate",
        "capability_registered": False,
    }
