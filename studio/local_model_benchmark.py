"""Optional bounded micro-benchmark for local models."""
from __future__ import annotations

import json
import os
import tempfile
import time
from pathlib import Path

from core import API, ProtocolError

MAX_BENCHMARK_MODELS = 6
MAX_SECONDS_PER_CALL = 20.0


def _save(path: Path, data: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, sort_keys=True, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass


def load(path: Path) -> dict:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _decode_json(response: dict) -> dict:
    try:
        raw = response["choices"][0]["message"]["content"].strip()
        fence = chr(96) * 3
        if raw.startswith(fence):
            raw = raw.split("\n", 1)[1].rsplit(fence, 1)[0]
        value = json.loads(raw)
    except (KeyError, IndexError, TypeError, AttributeError, json.JSONDecodeError):
        raise ProtocolError("benchmark response is not valid JSON") from None
    if not isinstance(value, dict):
        raise ProtocolError("benchmark response must be a JSON object")
    return value


def _call(api: API, model: str, system: str, user: str) -> tuple[dict | None, float]:
    started = time.monotonic()
    try:
        response = api.call(
            "POST",
            "/chat/completions",
            {
                "model": model,
                "stream": False,
                "max_tokens": 256,
                "temperature": 0,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            },
            timeout_seconds=MAX_SECONDS_PER_CALL,
        )
        value = _decode_json(response)
    except Exception:
        value = None
    return value, time.monotonic() - started


def benchmark(base: str, model: str, *, key: str = "") -> dict:
    api = API(base, key)

    json_value, json_latency = _call(
        api,
        model,
        "Return only valid JSON. No markdown.",
        'Return exactly {"ok":true,"value":7}.',
    )
    json_pass = (
        isinstance(json_value, dict)
        and json_value.get("ok") is True
        and json_value.get("value") == 7
    )

    code_value, code_latency = _call(
        api,
        model,
        "Return only JSON with one field named code.",
        "Write a Python function add(a,b) that returns a+b.",
    )
    code_text = code_value.get("code") if isinstance(code_value, dict) else None
    code_pass = (
        isinstance(code_text, str)
        and "def add" in code_text
        and "return" in code_text
        and ("a + b" in code_text or "a+b" in code_text)
    )

    score = 0.0
    score += 50.0 if json_pass else 0.0
    score += 40.0 if code_pass else 0.0
    avg_latency = (json_latency + code_latency) / 2.0
    if avg_latency <= 2.0:
        score += 10.0
    elif avg_latency <= 5.0:
        score += 7.0
    elif avg_latency <= 12.0:
        score += 4.0

    return {
        "model": model,
        "json_pass": json_pass,
        "code_pass": code_pass,
        "json_latency_seconds": round(json_latency, 4),
        "code_latency_seconds": round(code_latency, 4),
        "average_latency_seconds": round(avg_latency, 4),
        "score": round(min(100.0, score), 2),
    }


def benchmark_gateway(
    provider: str,
    base: str,
    models: list[str],
    out_path: Path,
    *,
    key: str = "",
) -> dict:
    existing = load(out_path)
    results = dict(existing)
    if os.environ.get("STUDIO_LOCAL_BENCHMARK", "false").strip().lower() not in {"1","true","yes","on"}:
        return results

    for model in models[:MAX_BENCHMARK_MODELS]:
        item_key = provider + "|" + model
        if item_key in results:
            continue
        results[item_key] = benchmark(base, model, key=key)
    _save(out_path, results)
    return results


def routing_bonus(data: dict, provider: str, model: str) -> float:
    row = data.get(provider + "|" + model) if isinstance(data, dict) else None
    if not isinstance(row, dict):
        return 0.0
    try:
        score = float(row.get("score", 0.0))
    except (TypeError, ValueError):
        return 0.0
    return round(max(-8.0, min(8.0, (score - 50.0) / 50.0 * 8.0)), 4)
