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
                params = {
                    "model": model, "messages": [{"role": "user", "content": 'Return only JSON {"ready":true}.'}],
                    "max_tokens": 128, "temperature": 0,
                }
                if provider.base.rstrip('/') == 'https://integrate.api.nvidia.com/v1':
                    params['response_format'] = {'type': 'json_object'}
                response = api_factory(provider.base, provider.key).call(
                    "POST", "/chat/completions", params, timeout_seconds=30)
                choices = response.get("choices") if isinstance(response, dict) else None
                message = choices[0].get("message") if isinstance(choices, list) and choices and isinstance(choices[0], dict) else None
                content = message.get("content") if isinstance(message, dict) else None
                parsed = json.loads(content) if isinstance(content, str) else None
                record["status"] = "ready" if isinstance(parsed, dict) and parsed.get('ready') is True else "invalid_response"
            except APIError as exc:
                record["http_status"] = int(exc.status)
            except json.JSONDecodeError:
                record["status"] = "invalid_response"
            except Exception:
                # Remote bodies, exception messages and completions may echo credentials.
                pass
            result["providers"].append(record)
    operator = str(env.get("PRODUCTION_OS_OPERATOR_TOKEN") or "").strip()
    if operator:
        result["operator_access"] = "unavailable"
        try:
            operator_client = api_factory(env["PRODUCTION_OS_URL"], operator)
            operator_client.call("GET", "/v1/dashboard/device-sessions", timeout_seconds=10)
            result["operator_access"] = "ready"
            if str(env.get("PRODUCTION_OS_DIAGNOSE_WAKE") or "") == "1":
                # Operator-authorized GET only. Report allowed setting *names*,
                # never a GitHub credential, token value or remote error body.
                try:
                    readiness = operator_client.call(
                        "GET",
                        "/v1/dashboard/launch-readiness?repository=dbrckk%2Frepo-standards",
                        timeout_seconds=10,
                    )
                    wake = readiness.get("worker_wake") if isinstance(readiness, dict) else None
                    allowed = {
                        "GITHUB_TOKEN", "PRODUCTION_OS_ACTIONS_REPOSITORY",
                        "PRODUCTION_OS_ACTIONS_WORKFLOW",
                    }
                    if isinstance(wake, dict):
                        result["worker_wake"] = {
                            "mode": (
                                str(wake.get("mode"))
                                if wake.get("mode") in {"immediate", "scheduled_fallback"}
                                else "unknown"
                            ),
                            "missing_configuration": sorted({
                                name for name in wake.get("missing_configuration", [])
                                if isinstance(name, str) and name in allowed
                            }) if isinstance(wake.get("missing_configuration"), list) else [],
                        }
                    else:
                        result["worker_wake"] = {"mode": "unavailable"}
                except Exception:
                    result["worker_wake"] = {"mode": "unavailable"}
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
