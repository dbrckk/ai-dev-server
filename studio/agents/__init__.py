"""Agent registry and routing primitives."""
from .registry import AgentRegistry, AgentSpec, DEFAULT_REGISTRY
from .router import RouteDecision, choose_agent, rank_agents

__all__ = [
    "AgentRegistry",
    "AgentSpec",
    "DEFAULT_REGISTRY",
    "RouteDecision",
    "choose_agent",
    "rank_agents",
]
