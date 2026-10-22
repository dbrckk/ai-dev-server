"""Shared provider defaults for the Actions worker and its live diagnostics.

A Cloudflare Workers Free fallback is opt-in only: a configured API credential
is not proof of an available zero-cost quota, and paid models are never selected.
"""
import json
import os
import re


_CLOUDFLARE_FREE_MODEL = "@cf/zai-org/glm-4.7-flash"


def _cloudflare_free_fallback(environ):
    """Return a conservative OpenAI-compatible Workers AI coding fallback.

    A Free-plan confirmation is required to prevent unintended metered use on
    Workers Paid. The model is explicitly Free-eligible as of October 2026.
    Never serialize the API token: ProviderSpec reads only its variable name.
    """
    if str(environ.get("STUDIO_CLOUDFLARE_FREE_TIER_ONLY") or "").strip() != "1":
        return None
    account = str(environ.get("CLOUDFLARE_ACCOUNT_ID") or "").strip().lower()
    if not re.fullmatch(r"[0-9a-f]{32}", account):
        return None
    if not str(environ.get("CLOUDFLARE_API_TOKEN") or "").strip():
        return None
    return {
        "name": "cloudflare-workers-free-fallback",
        "base": f"https://api.cloudflare.com/client/v4/accounts/{account}/ai/v1",
        "key_env": "CLOUDFLARE_API_TOKEN",
        "model": _CLOUDFLARE_FREE_MODEL,
        "code_model": _CLOUDFLARE_FREE_MODEL,
        "priority": 95,
        "free_preferred": True,
        "unmetered": False,
        "monthly_token_quota": 0,
    }


def configure(environ):
    if (not environ.get("STUDIO_PROVIDERS_JSON", "").strip()
            and environ.get("STUDIO_API_BASE", "").rstrip("/") == "https://integrate.api.nvidia.com/v1"):
        # Hosted primary defaults to the live-qualified Lightning model.
        # Avoid sending two paid-or-quota-metered requests to the same API
        # model/key when the primary and implementation model already match.
        # If an operator selected a different primary/code model, retain an
        # independently selectable Lightning fallback without overriding it.
        qualified = "nvidia/nemotron-3.5-lightning-30b-a3b"
        primary = str(environ.get("STUDIO_MODEL") or qualified).strip()
        primary_code = str(environ.get("STUDIO_CODE_MODEL") or primary).strip()
        providers = []
        if primary != qualified or primary_code != qualified:
            providers.append(
                {"name": "nvidia-lightning-fallback", "base": "https://integrate.api.nvidia.com/v1",
                 "key_env": "STUDIO_API_KEY", "model": qualified,
                 "code_model": qualified, "priority": 95, "free_preferred": True},
            )
        providers.append(
            {"name": "poolside-laguna-fallback", "base": "https://integrate.api.nvidia.com/v1",
             "key_env": "STUDIO_API_KEY", "model": "poolside/laguna-xs-2.1",
             "code_model": "poolside/laguna-xs-2.1", "priority": 90, "free_preferred": True},
        )
        free_fallback = _cloudflare_free_fallback(environ)
        if free_fallback:
            providers.append(free_fallback)
        environ["STUDIO_PROVIDERS_JSON"] = json.dumps(providers, separators=(",", ":"))
        return True
    return False


if __name__ == "__main__" and configure(os.environ):
    with open(os.environ["GITHUB_ENV"], "a", encoding="utf-8") as handle:
        handle.write("STUDIO_PROVIDERS_JSON=" + os.environ["STUDIO_PROVIDERS_JSON"] + "\n")
