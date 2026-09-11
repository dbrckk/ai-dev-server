"""Strict runtime for promoted studio capabilities."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import queue
import re
import threading

try:
    from .capability_registry import validate as validate_registry
except ImportError:
    from capability_registry import validate as validate_registry


PROVIDER_RE = re.compile(r"studio\.capabilities\.[a-z][a-z0-9_]{2,120}")
MAX_CONTEXT_BYTES = 128_000
MAX_RESULT_BYTES = 128_000
MAX_TIMEOUT_SECONDS = 30


class CapabilityRuntimeError(RuntimeError):
    pass


def _provider_path(provider: str, repo_root: Path) -> Path:
    if not isinstance(provider, str) or not PROVIDER_RE.fullmatch(provider):
        raise CapabilityRuntimeError("provider path invalid")
    module = provider.removeprefix("studio.capabilities.")
    path = (Path(repo_root) / "studio" / "capabilities" / (module + ".py"))
    if not path.is_file() or path.is_symlink():
        raise CapabilityRuntimeError("provider implementation unavailable")
    resolved = path.resolve()
    allowed_root = (Path(repo_root) / "studio" / "capabilities").resolve()
    if not resolved.is_relative_to(allowed_root):
        raise CapabilityRuntimeError("provider path escaped capability root")
    return resolved


def _bounded_json(value, limit, label):
    try:
        raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (TypeError, ValueError, UnicodeError, RecursionError):
        raise CapabilityRuntimeError(label + " is not valid JSON") from None
    if len(raw) > limit:
        raise CapabilityRuntimeError(label + " exceeds size limit")
    return raw


def _load_provider(provider: str, repo_root: Path):
    path = _provider_path(provider, repo_root)
    spec = importlib.util.spec_from_file_location(provider, path)
    if spec is None or spec.loader is None:
        raise CapabilityRuntimeError("provider import spec invalid")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except BaseException as exc:
        raise CapabilityRuntimeError("provider import failed: " + type(exc).__name__) from None
    run = getattr(module, "run", None)
    if not callable(run):
        raise CapabilityRuntimeError("provider must expose callable run(context)")
    return run


def execute_capability(registry, capability, context, *, repo_root=Path("."), timeout_seconds=10):
    validate_registry(registry)
    if not isinstance(capability, str) or not capability.strip():
        raise CapabilityRuntimeError("capability name invalid")
    if capability not in registry["capabilities"]:
        raise CapabilityRuntimeError("capability not registered")
    if (not isinstance(timeout_seconds, int) or isinstance(timeout_seconds, bool)
            or not 1 <= timeout_seconds <= MAX_TIMEOUT_SECONDS):
        raise CapabilityRuntimeError("timeout invalid")

    _bounded_json(context, MAX_CONTEXT_BYTES, "capability context")
    provider = registry["capabilities"][capability].get("provider")
    run = _load_provider(provider, Path(repo_root))

    result_queue = queue.Queue(maxsize=1)

    def invoke():
        try:
            result_queue.put(("ok", run(context)))
        except BaseException as exc:
            result_queue.put(("error", type(exc).__name__))

    thread = threading.Thread(target=invoke, daemon=True)
    thread.start()
    thread.join(timeout_seconds)
    if thread.is_alive():
        raise CapabilityRuntimeError("capability execution timed out")

    try:
        status, payload = result_queue.get_nowait()
    except queue.Empty:
        raise CapabilityRuntimeError("capability produced no result") from None
    if status != "ok":
        raise CapabilityRuntimeError("capability execution failed: " + str(payload))
    if not isinstance(payload, dict):
        raise CapabilityRuntimeError("capability result must be an object")
    _bounded_json(payload, MAX_RESULT_BYTES, "capability result")
    return payload
