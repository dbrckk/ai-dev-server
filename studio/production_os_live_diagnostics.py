"""Bounded live inference and operator-access checks; no queue or repository writes."""
import ast
import json
import os
import time

from core import API, APIError, StudioError
from production_os_provider_config import configure
from provider_router import load_providers


def _warm_operator_connection(client, *, seconds=120, clock=time.monotonic, sleep=time.sleep):
    """Bounded read-only Render warmup before probing operator credentials.

    Readiness GETs can be retried after ambiguous timeouts; operator POSTs
    must never be retried. Only transient gateway/readiness failures qualify.
    """
    deadline = clock() + seconds
    while True:
        remaining = deadline - clock()
        if remaining <= 0:
            return False
        try:
            result = client.call("GET", "/readyz", timeout_seconds=min(30, remaining))
            if isinstance(result, dict) and result.get("status") == "ready":
                return True
        except APIError as exc:
            if exc.status not in (502, 503, 504):
                raise
        except StudioError as exc:
            if str(exc) != "API unavailable or timed out":
                raise
        if clock() >= deadline:
            return False
        sleep(min(5, max(0, deadline - clock())))


def _provider_family(provider):
    """Public, bounded category; never print arbitrary provider names or URLs."""
    if (provider.name == "cloudflare-workers-free-fallback"
            and provider.model == "@cf/zai-org/glm-4.7-flash"
            and provider.base.startswith("https://api.cloudflare.com/client/v4/accounts/")
            and provider.base.endswith("/ai/v1")):
        return "cloudflare_workers_free"
    if provider.base.rstrip("/") == "https://integrate.api.nvidia.com/v1":
        return "nvidia_nim"
    return "other"


def _probe_options(provider, model):
    # These tiny probes need an answer inside 128/384 tokens. Supported
    # Nemotron templates otherwise spend that output allowance on reasoning.
    # Production requests retain their existing reasoning and token budgets.
    if (_provider_family(provider) == "nvidia_nim"
            and model.startswith(("nvidia/nemotron-3-", "nvidia/nemotron-3.5-"))):
        return {"chat_template_kwargs": {"enable_thinking": False}}
    return {}


def _model_profile(model):
    # Only public allowlisted labels; arbitrary configuration may be private.
    return {
        "nvidia/nemotron-3-super-120b-a12b": "nemotron_3_super",
        "nvidia/nemotron-3.5-lightning-30b-a3b": "nemotron_3_5_lightning",
        "poolside/laguna-xs-2.1": "laguna_xs_2_1",
        "@cf/zai-org/glm-4.7-flash": "cloudflare_glm_4_7_flash",
    }.get(model, "other")


def _coding_smoke(selected, ready_indices, api_factory):
    # Match real provider fallback without opaque POST retries or more output
    # capacity: all attempts share the original 384 tokens and 40 seconds.
    ordered = sorted(ready_indices,
                     key=lambda i: _provider_family(selected[i]) != "cloudflare_workers_free")
    remaining_tokens = 384
    deadline = time.monotonic() + 40
    attempts = []
    result = {"status": "no_ready_provider", "attempts": attempts}
    for offset, index in enumerate(ordered):
        remaining = deadline - time.monotonic()
        if remaining < 1:
            break
        limit = remaining_tokens // (len(ordered) - offset)
        remaining_tokens -= limit
        provider = selected[index]
        model = provider.model_for("implementation")
        attempt = {"provider_index": index, "provider_family": _provider_family(provider),
                   "model_profile": _model_profile(model), "max_tokens": limit,
                   "status": "unavailable"}
        try:
            response = api_factory(provider.base, provider.key).call(
                "POST", "/chat/completions", {
                    "model": model,
                    "messages": [{"role": "user", "content": (
                        "Write only Python code, no Markdown. Define exactly "
                        "def increment(value): with one return statement "
                        "that returns the input integer plus one."
                    )}],
                    "max_tokens": limit, "temperature": 0,
                    **_probe_options(provider, model),
                }, timeout_seconds=remaining, max_attempts=1)
            choices = response.get("choices") if isinstance(response, dict) else None
            message = choices[0].get("message") if isinstance(choices, list) and choices and isinstance(choices[0], dict) else None
            source = message.get("content") if isinstance(message, dict) else None
            attempt["status"] = "ready" if _safe_increment_source(source) else "invalid_code"
        except APIError as exc:
            attempt["http_status"] = int(exc.status)
        except Exception:
            pass
        attempts.append(attempt)
        result = {**attempt, "attempts": attempts}
        if attempt["status"] == "ready":
            break
    return result


def _safe_increment_source(source):
    """Check generated Python behavior by interpreting a tiny safe AST, never exec."""
    if not isinstance(source, str) or len(source) > 1024:
        return False
    try:
        tree = ast.parse(source)
        if len(tree.body) != 1 or not isinstance(tree.body[0], ast.FunctionDef):
            return False
        fn = tree.body[0]
        if (fn.name != "increment" or fn.decorator_list or fn.returns is not None
                or len(fn.args.args) != 1 or fn.args.args[0].arg != "value" or fn.args.args[0].annotation is not None
                or fn.args.defaults or fn.args.kwonlyargs or fn.args.posonlyargs
                or fn.args.vararg or fn.args.kwarg or len(fn.body) != 1
                or not isinstance(fn.body[0], ast.Return)):
            return False

        def interpret(expr, value):
            if isinstance(expr, ast.Name) and expr.id == "value":
                return value
            if isinstance(expr, ast.Constant) and type(expr.value) is int and abs(expr.value) <= 10:
                return expr.value
            if isinstance(expr, ast.BinOp) and isinstance(expr.op, (ast.Add, ast.Sub)):
                left, right = interpret(expr.left, value), interpret(expr.right, value)
                return left + right if isinstance(expr.op, ast.Add) else left - right
            raise ValueError("unsupported AST")

        return all(interpret(fn.body[0].value, value) == value + 1 for value in (-7, 0, 1, 41))
    except (SyntaxError, ValueError, TypeError, RecursionError, OverflowError):
        return False


def diagnose(*, api_factory=API, providers=None, environ=None):
    env = os.environ if environ is None else environ
    configure(env)
    providers = load_providers() if providers is None else providers
    result = {"schema_version": 1, "providers": [], "operator_access": "not_configured",
              "cloudflare_free_configured": any(
                  _provider_family(provider) == "cloudflare_workers_free" for provider in providers)}
    # Limit live calls, but always include the opt-in Cloudflare fallback if present.
    selected = list(providers[:3])
    if not any(_provider_family(p) == "cloudflare_workers_free" for p in selected):
        free = next((p for p in providers[3:] if _provider_family(p) == "cloudflare_workers_free"), None)
        if free is not None:
            selected = (selected[:2] + [free]) if len(selected) == 3 else (selected + [free])
    # Same model selection for product and implementation as the real worker.
    for index, provider in enumerate(selected):
        for role in ("product", "implementation"):
            model = provider.model_for(role)
            if role == "implementation" and model == provider.model_for("product"):
                continue
            record = {"provider_index": index, "provider_family": _provider_family(provider),
                      "model_profile": _model_profile(model), "role": role, "status": "unavailable"}
            try:
                params = {
                    "model": model, "messages": [{"role": "user", "content": 'Return only JSON {"ready":true}.'}],
                    "max_tokens": 128, "temperature": 0,
                    **_probe_options(provider, model),
                }
                if provider.base.rstrip('/') == 'https://integrate.api.nvidia.com/v1':
                    params['response_format'] = {'type': 'json_object'}
                response = api_factory(provider.base, provider.key).call(
                    "POST", "/chat/completions", params, timeout_seconds=30)
                choices = response.get("choices") if isinstance(response, dict) else None
                message = choices[0].get("message") if isinstance(choices, list) and choices and isinstance(choices[0], dict) else None
                finish = choices[0].get("finish_reason") if isinstance(choices, list) and choices and isinstance(choices[0], dict) else None
                if finish in {"stop", "length", "content_filter", "tool_calls"}:
                    record["finish_reason"] = finish
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
            diagnose_wake = str(env.get("PRODUCTION_OS_DIAGNOSE_WAKE") or "") == "1"
            if diagnose_wake and not _warm_operator_connection(operator_client):
                result["worker_wake"] = {"mode": "unavailable"}
            else:
                operator_client.call("GET", "/v1/dashboard/device-sessions", timeout_seconds=(30 if diagnose_wake else 10))
                result["operator_access"] = "ready"
            if diagnose_wake and result["operator_access"] == "ready":
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
    ready_indices = [
        index for index in range(len(selected))
        if (records := [x for x in result["providers"] if x["provider_index"] == index])
        and all(x["status"] == "ready" for x in records)
    ]
    result["inference_ready"] = bool(ready_indices)
    if str(env.get("PRODUCTION_OS_DIAGNOSE_CODE_SMOKE") or "") == "1":
        result["coding_smoke"] = _coding_smoke(selected, ready_indices, api_factory)

    return result


def main():
    try:
        result = diagnose()
    except Exception:
        result = {"schema_version": 1, "inference_ready": False, "configuration": "invalid"}
    # A responding model alone cannot qualify the control plane. Operator
    # access is required, and an explicitly requested wake probe must succeed.
    # Scheduled fallback remains a supported (reported) operating mode.
    ready = result.get("inference_ready") is True and result.get("operator_access") == "ready"
    if str(os.environ.get("PRODUCTION_OS_DIAGNOSE_CODE_SMOKE") or "") == "1":
        ready = ready and result.get("coding_smoke", {}).get("status") == "ready"
    if str(os.environ.get("PRODUCTION_OS_DIAGNOSE_WAKE") or "") == "1":
        wake = result.get("worker_wake")
        ready = ready and isinstance(wake, dict) and wake.get("mode") in {
            "immediate", "scheduled_fallback",
        }
    result["diagnostic_ready"] = ready
    print("Production-OS live diagnosis: " + json.dumps(result, sort_keys=True))
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
