"""Verified non-interactive Codex CLI contract and telemetry parsing."""
from __future__ import annotations

import json
from typing import Any


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
    ``--ephemeral`` avoids leaving autonomous session state behind.
    """
    return ["codex", "exec", "--json", "--ephemeral", prompt], {}


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
