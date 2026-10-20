"""Single bounded, non-secret free-model coding qualification.

This probe deliberately never reads project sources, GitHub credentials,
operator tokens, or runtime secrets. It does not enqueue production work.
"""
from __future__ import annotations

import json
from pathlib import Path

from core import API, APIError, StudioError, canonical
from production_os_live_diagnostics import _safe_increment_source

GATEWAY = "https://api.kilo.ai/api/gateway"
MODEL = "kilo-auto/free"
OUTPUT = Path("studio-output/public-free-code-smoke/report.json")


def _catalog_confirms_zero_cost(payload: object) -> bool:
    """Reject uncertain pricing rather than assume an advertised free tier."""
    if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
        return False
    for entry in payload["data"]:
        if not isinstance(entry, dict) or entry.get("id") != MODEL:
            continue
        if entry.get("isFree") is not True:
            return False
        prices = entry.get("pricing")
        if not isinstance(prices, dict):
            return False
        try:
            return (
                "prompt" in prices and "completion" in prices
                and type(prices["prompt"]) is not bool
                and type(prices["completion"]) is not bool
                and float(prices["prompt"]) == 0.0
                and float(prices["completion"]) == 0.0
            )
        except (TypeError, ValueError, OverflowError):
            return False
    return False


def run() -> int:
    # Save only bounded, nonsensitive evidence. Never emit remote text.
    evidence = {
        "schema_version": 1,
        "scenario": "synthetic_python_increment",
        "model": MODEL,
        "catalog_free_confirmed": False,
        "requests_sent": 0,
        "code_verified": False,
        "status": "blocked",
    }
    try:
        client = API(GATEWAY, "")
        catalog = client.call("GET", "/models", timeout_seconds=18, max_attempts=1)
        evidence["catalog_free_confirmed"] = _catalog_confirms_zero_cost(catalog)
        if not evidence["catalog_free_confirmed"]:
            evidence["reason"] = "free_catalog_or_zero_price_unverified"
            return 1

        # The *only* submitted content is a fixed, synthetic, public exercise.
        # Reasoning tokens can consume most of a tiny answer; cap at 512.
        evidence["requests_sent"] = 1
        response = client.call("POST", "/chat/completions", {
            "model": MODEL,
            "messages": [{
                "role": "user",
                "content": (
                    "Return only Python source code, without Markdown or "
                    "explanations. Define exactly one function named "
                    "increment with one parameter named value and a single "
                    "return statement computing value plus one. Do not use "
                    "imports, annotations, decorators, or other statements."
                ),
            }],
            "max_tokens": 512,
            "temperature": 0,
        }, timeout_seconds=45, max_attempts=1)

        if not isinstance(response, dict):
            evidence["reason"] = "invalid_provider_response"
            return 1
        usage = response.get("usage")
        if isinstance(usage, dict):
            tokens = usage.get("completion_tokens")
            if type(tokens) is int and 0 <= tokens <= 512:
                evidence["completion_tokens"] = tokens
        # Gateways report charge data either at the top level or in usage.
        # Inspect every present field: a zero field cannot hide another charge.
        costs = []
        for container in (response, usage):
            if isinstance(container, dict):
                costs.extend(container[key] for key in ("market_cost", "cost") if key in container)
        details = usage.get("cost_details") if isinstance(usage, dict) else None
        if isinstance(details, dict):
            costs.extend(details[key] for key in (
                "upstream_inference_cost", "upstream_inference_prompt_cost",
                "upstream_inference_completions_cost",
            ) if key in details)
        evidence["cost_reported"] = bool(costs)
        if costs:
            try:
                if any(type(cost) is bool or cost is None for cost in costs):
                    raise ValueError("invalid cost type")
                if any(float(cost) != 0.0 for cost in costs):
                    evidence["reason"] = "unexpected_nonzero_cost"
                    return 1
                evidence["reported_zero_cost"] = True
            except (TypeError, ValueError, OverflowError):
                evidence["reason"] = "invalid_cost"
                return 1

        choices = response.get("choices")
        first = choices[0] if isinstance(choices, list) and choices else None
        message = first.get("message") if isinstance(first, dict) else None
        source = message.get("content") if isinstance(message, dict) else None
        evidence["code_verified"] = _safe_increment_source(source)
        evidence["status"] = "passed" if evidence["code_verified"] else "blocked"
        if not evidence["code_verified"]:
            evidence["reason"] = "source_behavior_not_verified"
        return 0 if evidence["code_verified"] else 1
    except APIError as exc:
        evidence["reason"] = "provider_http_error"
        evidence["http_status"] = int(exc.status)
        return 1
    except (StudioError, OSError, ValueError, TypeError, TimeoutError):
        evidence["reason"] = "transport_or_response_unavailable"
        return 1
    finally:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(canonical(evidence) + "\n", encoding="utf-8")
        print(canonical(evidence))


if __name__ == "__main__":
    raise SystemExit(run())
