"""Verified non-interactive Codex CLI contract and telemetry parsing."""
from __future__ import annotations

import json
from typing import Any
from urllib.parse import urlsplit


_USAGE_FIELDS = (
    "input_tokens",
    "cached_input_tokens",
    "cache_write_input_tokens",
    "output_tokens",
    "reasoning_output_tokens",
)


def codex_invocation(prompt: str) -> tuple[list[str], dict[str, str]]:
    """Build the upstream-supported headless Codex invocation.

    JSONL output gives the orchestrator structured terminal events while
    ``--ephemeral`` avoids leaving autonomous session state behind. The sandbox
    is fixed to workspace-write so an external user config cannot silently turn
    an implementation run into a read-only review.
    """
    return [
        "codex",
        "exec",
        "--json",
        "--ephemeral",
        "--sandbox",
        "workspace-write",
        prompt,
    ], {}



def codex_omniroute_invocation(
    prompt: str,
    *,
    base_url: str,
    codex_home: str,
) -> tuple[list[str], dict[str, str]]:
    """Build an isolated Codex invocation routed through OmniRoute.

    The custom provider is supplied as CLI config and the caller must provide a
    dedicated CODEX_HOME. This prevents ChatGPT account authentication/config
    from silently taking precedence over the custom Responses endpoint.
    """
    parsed = urlsplit(str(base_url or "").strip())
    loopback_hosts = {"127.0.0.1", "localhost", "::1", "0.0.0.0"}
    local_http = (
        parsed.scheme == "http"
        and (parsed.hostname or "").lower() in loopback_hosts
    )
    if (
        not (parsed.scheme == "https" or local_http)
        or not parsed.netloc
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError(
            "Codex OmniRoute base URL must use HTTPS, except loopback-local HTTP"
        )
    home = str(codex_home or "").strip()
    if not home:
        raise ValueError("Codex OmniRoute CODEX_HOME is required")
    base = str(base_url).strip().rstrip("/")
    if "'" in base or "\n" in base or "\r" in base:
        raise ValueError("Codex OmniRoute base URL contains unsupported characters")

    provider = (
        "model_providers.omniroute={ "
        "name='OmniRoute', "
        f"base_url='{base}', "
        "wire_api='responses', "
        "request_max_retries=0, "
        "stream_max_retries=0 "
        "}"
    )
    return [
        "codex",
        "-c",
        'model="auto"',
        "-c",
        'model_provider="omniroute"',
        "-c",
        provider,
        "exec",
        "--ignore-user-config",
        "--json",
        "--ephemeral",
        "--sandbox",
        "workspace-write",
        prompt,
    ], {"CODEX_HOME": home}


def _token_count(value: Any) -> int:
    if isinstance(value, bool):
        return 0
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0


def parse_codex_usage(stdout: str) -> dict[str, int] | None:
    """Return normalized usage from the last completed turn in JSONL output.

    Unknown and malformed lines are ignored so additive upstream event types do
    not break callers. Cached input is reported separately but is not added a
    second time to ``total_tokens`` because it is part of input usage.
    """
    completed: dict[str, int] | None = None
    for raw_line in stdout.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except (json.JSONDecodeError, TypeError):
            continue
        if not isinstance(event, dict) or event.get("type") != "turn.completed":
            continue
        usage = event.get("usage")
        if not isinstance(usage, dict):
            continue
        normalized = {field: _token_count(usage.get(field, 0)) for field in _USAGE_FIELDS}
        normalized["total_tokens"] = normalized["input_tokens"] + normalized["output_tokens"]
        completed = normalized
    return completed
