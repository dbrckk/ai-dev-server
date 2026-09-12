"""Provider-routed structured model calls for generic projects."""
from __future__ import annotations

import json

from core import API, APIError, ProtocolError, StudioError
from provider_router import candidates_for, load_providers


def _decode(response: dict) -> dict:
    try:
        choice = response["choices"][0]
        if choice.get("finish_reason") == "length":
            raise ProtocolError("Generic model response truncated")
        raw = choice["message"]["content"].strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
        value = json.loads(raw)
    except (KeyError, IndexError, TypeError, AttributeError, json.JSONDecodeError):
        raise ProtocolError("Generic model returned invalid JSON") from None
    if not isinstance(value, dict):
        raise ProtocolError("Generic model JSON must be an object")
    return value


def ask(system: str, user: str, *, code: bool = False) -> tuple[dict, dict]:
    try:
        providers = load_providers(prefer_free=True)
    except ValueError as exc:
        raise StudioError(str(exc)) from None
    role = "implementation" if code else "product"
    providers = candidates_for(role, providers=providers)
    if not providers:
        raise StudioError("No configured provider available for generic project")
    last = None
    for provider in providers:
        model = provider.model_for(role)
        api = API(provider.base, provider.key)
        params = {
            "model": model,
            "stream": False,
            "max_tokens": 16000 if code else 8192,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        if api.base == "https://integrate.api.nvidia.com/v1" and model.startswith("nvidia/nemotron-3-"):
            params.update(chat_template_kwargs={"enable_thinking": True}, reasoning_budget=2048)
        try:
            response = api.call("POST", "/chat/completions", params)
            return _decode(response), {"provider": provider.name, "model": model}
        except (APIError, StudioError, ProtocolError) as exc:
            last = exc
            continue
    raise StudioError("All generic-project providers failed: " + (str(last) if last else "unknown")) from None
