"""Agent capability registry for AI Dev Server."""
from __future__ import annotations

from dataclasses import dataclass, field
import shutil
from typing import Iterable


@dataclass(frozen=True)
class AgentSpec:
    name: str
    command: str
    capabilities: frozenset[str]
    priority: int = 50
    free_preferred: bool = True
    long_running: bool = False
    browser: bool = False
    mcp: bool = False
    metadata: dict[str, str] = field(default_factory=dict)

    def available(self) -> bool:
        return shutil.which(self.command) is not None


_DEFAULTS = (
    AgentSpec(
        "opencode",
        "opencode",
        frozenset({"code_editing", "tests", "debug", "repo_analysis", "mcp"}),
        priority=90,
        mcp=True,
    ),
    AgentSpec(
        "codex",
        "codex",
        frozenset({"code_editing", "tests", "debug", "repo_analysis", "review"}),
        priority=85,
    ),
    AgentSpec(
        "claude-code",
        "claude",
        frozenset({"code_editing", "tests", "debug", "repo_analysis", "review", "planning"}),
        priority=80,
        free_preferred=False,
    ),
    AgentSpec(
        "deepseek-harness",
        "dsh",
        frozenset({"code_editing", "repo_analysis", "planning", "research"}),
        priority=75,
        long_running=True,
    ),
    AgentSpec(
        "hermes",
        "hermes",
        frozenset({"planning", "research", "delegation", "repo_analysis", "long_task"}),
        priority=95,
        long_running=True,
        mcp=True,
    ),
    AgentSpec(
        "openhands",
        "openhands",
        frozenset({"code_editing", "tests", "debug", "repo_analysis", "long_task", "browser"}),
        priority=88,
        long_running=True,
        browser=True,
    ),
)


class AgentRegistry:
    def __init__(self, specs: Iterable[AgentSpec] = _DEFAULTS):
        self._specs = {spec.name: spec for spec in specs}

    def all(self) -> tuple[AgentSpec, ...]:
        return tuple(self._specs.values())

    def get(self, name: str) -> AgentSpec | None:
        return self._specs.get(name)

    def available(self) -> tuple[AgentSpec, ...]:
        return tuple(spec for spec in self._specs.values() if spec.available())


DEFAULT_REGISTRY = AgentRegistry()
