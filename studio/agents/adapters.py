"""Execution adapters for registered coding agents.

Adapters deliberately use argv lists (never a shell) and return bounded evidence.
Agent-specific invocation templates can be added without changing the router.
"""
from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import subprocess
import time

from .registry import AgentSpec


@dataclass(frozen=True)
class AgentRun:
    agent: str
    returncode: int
    duration_seconds: float
    stdout_tail: str
    stderr_tail: str


class AgentAdapter:
    def __init__(self, spec: AgentSpec):
        self.spec = spec

    def probe(self) -> bool:
        return self.spec.available()

    def run(
        self,
        argv: list[str],
        *,
        cwd: Path,
        timeout: int = 1800,
        extra_env: dict[str, str] | None = None,
    ) -> AgentRun:
        if not self.probe():
            raise RuntimeError(f"Agent unavailable: {self.spec.name}")
        if not argv or argv[0] != self.spec.command:
            raise ValueError("Adapter argv must start with the registered command")
        if timeout < 1 or timeout > 7200:
            raise ValueError("Agent timeout outside allowed range")
        env = os.environ.copy()
        # Coding agents do not need repository-write credentials: publishing is
        # performed later by the trusted GitHub adapter after validation.
        for key in list(env):
            if key.startswith(("GITHUB_","GH_","STUDIO_")) or key=="CODESPACES_PAT":
                env.pop(key,None)
        # Never let an autonomous prompt override process-critical variables.
        if extra_env:
            for key,value in extra_env.items():
                if key in {"PATH","HOME","PYTHONPATH","LD_PRELOAD"} or key.startswith(("GITHUB_","GH_")):
                    continue
                env[key]=value
        started = time.monotonic()
        try:
            result = subprocess.run(
                argv,
                cwd=cwd,
                env=env,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(f"Agent timed out: {self.spec.name}") from exc
        duration = time.monotonic() - started
        stdout=result.stdout[-24000:]
        stderr=result.stderr[-24000:]
        for key,value in (extra_env or {}).items():
            if value and any(mark in key.upper() for mark in ("KEY","TOKEN","SECRET","PASSWORD")):
                stdout=stdout.replace(value,"[REDACTED]")
                stderr=stderr.replace(value,"[REDACTED]")
        return AgentRun(
            agent=self.spec.name,
            returncode=result.returncode,
            duration_seconds=round(duration, 3),
            stdout_tail=stdout,
            stderr_tail=stderr,
        )
