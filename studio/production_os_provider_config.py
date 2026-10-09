"""Shared provider defaults for the Actions worker and its live diagnostics."""
import json
import os


def configure(environ):
    if (not environ.get("STUDIO_PROVIDERS_JSON", "").strip()
            and environ.get("STUDIO_API_BASE", "").rstrip("/") == "https://integrate.api.nvidia.com/v1"):
        environ["STUDIO_PROVIDERS_JSON"] = json.dumps([
            {"name": "nvidia-lightning-fallback", "base": "https://integrate.api.nvidia.com/v1",
             "key_env": "STUDIO_API_KEY", "model": "nvidia/nemotron-3.5-lightning-30b-a3b",
             "code_model": "nvidia/nemotron-3.5-lightning-30b-a3b", "priority": 70, "free_preferred": True},
            {"name": "poolside-laguna-fallback", "base": "https://integrate.api.nvidia.com/v1",
             "key_env": "STUDIO_API_KEY", "model": "poolside/laguna-xs-2.1",
             "code_model": "poolside/laguna-xs-2.1", "priority": 90, "free_preferred": True},
        ], separators=(",", ":"))
        return True
    return False


if __name__ == "__main__" and configure(os.environ):
    with open(os.environ["GITHUB_ENV"], "a", encoding="utf-8") as handle:
        handle.write("STUDIO_PROVIDERS_JSON=" + os.environ["STUDIO_PROVIDERS_JSON"] + "\n")
