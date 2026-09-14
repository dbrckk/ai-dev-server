"""Fail-safe discovery of OpenAI-compatible local AI gateways."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

DEFAULT_ENDPOINTS = (
    ("omniroute", "http://127.0.0.1:20128/v1", 1_470_000_000),
    ("ollama", "http://127.0.0.1:11434/v1", 0),
    ("localai", "http://127.0.0.1:8080/v1", 0),
    ("vllm", "http://127.0.0.1:8000/v1", 0),
    ("llamacpp", "http://127.0.0.1:8081/v1", 0),
)

CODE_HINTS = (
    "coder",
    "code",
    "qwen",
    "deepseek",
    "starcoder",
    "codestral",
    "devstral",
)
VISION_HINTS = (
    "vision",
    "vl",
    "llava",
    "qwen2.5-vl",
    "qwen3-vl",
)


def _bool(value: object, default: bool = True) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() not in {"0", "false", "no", "off"}
    return default


def _model_ids(value: object) -> list[str]:
    if not isinstance(value, dict):
        return []
    rows = value.get("data")
    if not isinstance(rows, list):
        return []
    ids = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        model_id = row.get("id")
        if isinstance(model_id, str) and model_id.strip():
            ids.append(model_id.strip())
    return sorted(set(ids))[:256]


def _pick(models: list[str], hints: tuple[str, ...]) -> str:
    for hint in hints:
        for model in models:
            if hint in model.lower():
                return model
    return models[0] if models else ""


def probe_gateway(
    name: str,
    base: str,
    monthly_token_quota: int = 0,
    *,
    timeout: float = 0.25,
) -> dict | None:
    try:
        req = urllib.request.Request(
            base.rstrip("/") + "/models",
            headers={"Accept": "application/json", "User-Agent": "ai-dev-server"},
        )
        with urllib.request.urlopen(req, timeout=max(0.05, min(1.0, timeout))) as response:
            if response.status != 200:
                return None
            raw = response.read(300_000)
        value = json.loads(raw)
    except (OSError, ValueError, urllib.error.URLError):
        return None

    models = _model_ids(value)
    if not models:
        return None

    return {
        "name": name,
        "base": base.rstrip("/"),
        "models": models,
        "model": _pick(models, ()),
        "code_model": _pick(models, CODE_HINTS),
        "vision_model": _pick(models, VISION_HINTS) if any(
            any(hint in model.lower() for hint in VISION_HINTS)
            for model in models
        ) else "",
        "unmetered": monthly_token_quota <= 0,
        "monthly_token_quota": max(0, int(monthly_token_quota)),
    }


def discover(*, timeout: float = 0.25) -> list[dict]:
    if not _bool(os.environ.get("STUDIO_AUTO_DISCOVER_LOCAL_CAPACITY", "true"), True):
        return []

    custom = os.environ.get("STUDIO_LOCAL_CAPACITY_ENDPOINTS_JSON", "")
    endpoints = DEFAULT_ENDPOINTS
    if custom.strip():
        try:
            value = json.loads(custom)
        except json.JSONDecodeError:
            value = None
        if isinstance(value, list):
            parsed = []
            for item in value:
                if not isinstance(item, dict):
                    continue
                name = item.get("name")
                base = item.get("base")
                quota = item.get("monthly_token_quota", 0)
                if isinstance(name, str) and isinstance(base, str):
                    try:
                        parsed.append((name, base, max(0, int(quota or 0))))
                    except (TypeError, ValueError):
                        pass
            if parsed:
                endpoints = tuple(parsed)

    found = []
    for name, base, quota in endpoints:
        row = probe_gateway(name, base, quota, timeout=timeout)
        if row is not None:
            found.append(row)
    return found
