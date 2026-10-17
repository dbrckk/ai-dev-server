"""Execution adapters for registered coding agents.

Adapters deliberately use argv lists (never a shell) and return bounded evidence.
Agent-specific invocation templates can be added without changing the router.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
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
        # Prevent untrusted subprocesses (including Hermes and OpenCode)
        # from inheriting credentials that control workers, GitHub delivery,
        # or host Git/SSH authentication. Model-provider credentials remain
        # available for authorized inference; scoped aliases also work.
        control_prefixes = (
            "GITHUB_", "GH_", "STUDIO_", "PRODUCTION_OS_",
            "ASSET_FORGE_GITHUB_", "GIT_",
        )
        # Cloudflare's fallback key is for the trusted in-process router only.
        # Hermes/OpenCode/Codex do not need this extra ambient credential.
        control_keys = {
            "CODESPACES_PAT", "SSH_ASKPASS", "SSH_AUTH_SOCK",
            "CLOUDFLARE_API_TOKEN",
        }
        for key in list(env):
            if key.startswith(control_prefixes) or key in control_keys:
                env.pop(key, None)
        # Never let an autonomous prompt override process-critical variables.
        if extra_env:
            for key,value in extra_env.items():
                if (key in {"PATH", "HOME", "PYTHONPATH", "LD_PRELOAD"}
                        or key.startswith(control_prefixes) or key in control_keys):
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
        # The subprocess inherits model-provider credentials such as
        # OMNIROUTE_API_KEY and OPENAI_API_KEY. Previous masking only examined
        # extra_env, allowing inherited secrets to reach persistent evidence.
        # Redact the *full* output before tail truncation; otherwise slicing
        # at the 24k boundary can expose a partial credential.
        secret_suffixes = ("_KEY", "_TOKEN", "_SECRET", "_PASSWORD", "_CREDENTIAL")
        secret_names = {"HF_TOKEN", "GITHUB_TOKEN", "CODESPACES_PAT"}
        redactions = {
            value for key, value in env.items()
            if isinstance(value, str) and value
            and (key.upper().endswith(secret_suffixes)
                 or key.upper() in secret_names)
        }
        stdout = result.stdout
        stderr = result.stderr
        ordered_redactions = sorted(redactions, key=len, reverse=True)
        for value in ordered_redactions:
            stdout = stdout.replace(value, "[REDACTED]")
            stderr = stderr.replace(value, "[REDACTED]")
        stdout = stdout[-24000:]
        stderr = stderr[-24000:]
        if self.spec.name == "codex":
            # Preserve the last terminal usage event even if large output
            # would otherwise push it outside the 24k evidence tail.
            terminal_event = None
            for raw_line in result.stdout.splitlines():
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                except (json.JSONDecodeError, TypeError):
                    continue
                if isinstance(event, dict) and event.get("type") == "turn.completed":
                    terminal_event = line
            if terminal_event:
                for value in ordered_redactions:
                    terminal_event = terminal_event.replace(value, "[REDACTED]")
                if terminal_event not in stdout:
                    budget = max(0, 24000 - len(terminal_event) - 1)
                    stdout = terminal_event + "\n" + stdout[-budget:]
        return AgentRun(
            agent=self.spec.name,
            returncode=result.returncode,
            duration_seconds=round(duration, 3),
            stdout_tail=stdout,
            stderr_tail=stderr,
        )
