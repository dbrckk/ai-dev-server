"""Checkpointed model calls that can be safely replayed after a crash."""
from __future__ import annotations

import hashlib
from pathlib import Path

from core import canonical
from workflow_checkpoint import discard, get, operation_key, put


def _screenshots_fingerprint(screenshots) -> list[dict]:
    result = []
    for item in screenshots or ():
        path = Path(item)
        data = path.read_bytes()
        result.append({
            "name": path.name,
            "sha256": hashlib.sha256(data).hexdigest(),
            "size": len(data),
        })
    return result


def ask(model, role: str, context: str, screenshots=(), *, namespace: str = "model") -> tuple[dict, bool, str]:
    key = operation_key(namespace, {
        "role": role,
        "context": context,
        "screenshots": _screenshots_fingerprint(screenshots),
    })
    cached = get(key)
    if cached is not None:
        value = cached.get("response")
        if isinstance(value, dict):
            return value, True, key
        discard(key)

    value = model.ask(role, context, screenshots)
    if not isinstance(value, dict):
        raise ValueError("model response must be an object")
    put(key, {"response": value}, kind=namespace)
    return value, False, key


def ask_value(model, role: str, context: str, screenshots=(), *, namespace: str = "model") -> dict:
    return ask(model, role, context, screenshots, namespace=namespace)[0]
