"""Bounded live inference and operator-access checks; no queue or repository writes."""
import json
import os

from core import API, APIError
from production_os_provider_config import configure
from provider_router import load_providers


def diagnose(*, api_factory=API, providers=None, environ=None):
    env = os.environ if environ is None else environ
    configure(env)
    providers = load_providers() if providers is None else providers
    result = {"schema_version": 1, "providers": [], "operator_access": "not_configured"}
    # Same model selection for product and implementation as the real worker.
    for index, provider in enumerate(providers[:3]):
        for role in ("product", "implementation"):
            model = provider.model_for(role)
            if role == "implementation" and model == provider.model_for("product"):
                continue
            record = {"provider_index": index, "role": role, "status": "unavailable"}
            try:
                response = api_factory(provider.base, provider.key).call(
                    "POST", "/chat/completions", {
                        "model": model, "messages": [{"role": "user", "content": "Reply with OK."}],
                        "max_tokens": 128, "temperature": 0,
                    }, timeout_seconds=30)
                choices = response.get("choices") if isinstance(response, dict) else None
                message = choices[0].get("message") if isinstance(choices, list) and choices and isinstance(choices[0], dict) else None
                content = message.get("content") if isinstance(message, dict) else None
                record["status"] = "ready" if isinstance(content, str) and content.strip() else "invalid_response"
            except APIError as exc:
                record["http_status"] = int(exc.status)
            except Exception:
                # Remote bodies, exception messages and completions may echo credentials.
                pass
            result["providers"].append(record)
    operator = str(env.get("PRODUCTION_OS_OPERATOR_TOKEN") or "").strip()
    if operator:
        result["operator_access"] = "unavailable"
        try:
            api_factory(env["PRODUCTION_OS_URL"], operator).call("GET", "/v1/dashboard/device-sessions", timeout_seconds=10)
            result["operator_access"] = "ready"
        except APIError as exc:
            result["operator_http_status"] = int(exc.status)
        except Exception:
            pass
    result["inference_ready"] = any(
        records and all(x["status"] == "ready" for x in records)
        for index in range(min(3, len(providers)))
        if (records := [x for x in result["providers"] if x["provider_index"] == index])
    )
    return result


def main():
    try:
        result = diagnose()
    except Exception:
        result = {"schema_version": 1, "inference_ready": False, "configuration": "invalid"}
    print("Production-OS live diagnosis: " + json.dumps(result, sort_keys=True))
    return 0 if result["inference_ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
