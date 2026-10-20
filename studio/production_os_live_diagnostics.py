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
                      "role": role, "status": "unavailable"}
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
        # One additional request, no retries. Only the source AST is inspected;
        # generated code is never run on the trusted Actions runner.
        code_smoke = {"status": "no_ready_provider"}
        if ready_indices:
            chosen = next(
                (i for i in ready_indices if _provider_family(selected[i]) == "cloudflare_workers_free"),
                ready_indices[0],
            )
            provider = selected[chosen]
            code_smoke = {"provider_index": chosen,
                          "provider_family": _provider_family(provider),
                          "status": "unavailable"}
            try:
                response = api_factory(provider.base, provider.key).call(
                    "POST", "/chat/completions", {
                        "model": provider.model_for("implementation"),
                        "messages": [{"role": "user", "content": (
                            "Write only Python code, no Markdown. Define exactly "
                            "def increment(value): with one return statement "
                            "that returns the input integer plus one."
                        )}],
                        "max_tokens": 384, "temperature": 0,
                    }, timeout_seconds=40, max_attempts=1)
                choices = response.get("choices") if isinstance(response, dict) else None
                message = choices[0].get("message") if isinstance(choices, list) and choices and isinstance(choices[0], dict) else None
                source = message.get("content") if isinstance(message, dict) else None
                code_smoke["status"] = "ready" if _safe_increment_source(source) else "invalid_code"
            except APIError as exc:
                code_smoke["http_status"] = int(exc.status)
            except Exception:
                pass
        result["coding_smoke"] = code_smoke
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
