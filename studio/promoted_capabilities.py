"""Trusted source-controlled registry for promoted generic capabilities."""
from __future__ import annotations

import json
from pathlib import Path
import re

try:
    from .capability_registry import has_capability, register, validate as validate_registry
except ImportError:
    from capability_registry import has_capability, register, validate as validate_registry

DEFAULT_REGISTRY = Path(__file__).resolve().parents[1] / "control" / "promoted_capabilities.json"
NAME_RE = re.compile(r"[a-z][a-z0-9_.-]{2,80}")
SHA_RE = re.compile(r"[0-9a-f]{40}")


class PromotedCapabilityError(ValueError):
    pass


def provider_for(name: str) -> str:
    if not isinstance(name, str) or not NAME_RE.fullmatch(name):
        raise PromotedCapabilityError("capability name invalid")
    slug = re.sub(r"[^a-z0-9]+", "_", name).strip("_")
    if not slug:
        raise PromotedCapabilityError("capability slug invalid")
    return "studio.capabilities." + slug


def load(path=DEFAULT_REGISTRY):
    path = Path(path)
    if not path.exists():
        return {"version": 1, "capabilities": {}}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PromotedCapabilityError("promoted capability registry unreadable") from exc
    if not isinstance(value, dict) or set(value) != {"version", "capabilities"} or value.get("version") != 1:
        raise PromotedCapabilityError("promoted capability registry malformed")
    capabilities = value.get("capabilities")
    if not isinstance(capabilities, dict):
        raise PromotedCapabilityError("promoted capability registry malformed")
    for name, entry in capabilities.items():
        if not isinstance(name, str) or not NAME_RE.fullmatch(name):
            raise PromotedCapabilityError("promoted capability name invalid")
        if not isinstance(entry, dict) or set(entry) != {"provider", "candidate_id", "baseline_sha", "candidate_sha"}:
            raise PromotedCapabilityError("promoted capability entry malformed")
        if entry.get("provider") != provider_for(name):
            raise PromotedCapabilityError("promoted capability provider mismatch")
        if not isinstance(entry.get("candidate_id"), str) or not entry["candidate_id"].strip():
            raise PromotedCapabilityError("promoted capability candidate invalid")
        for key in ("baseline_sha", "candidate_sha"):
            if not isinstance(entry.get(key), str) or not SHA_RE.fullmatch(entry[key]):
                raise PromotedCapabilityError("promoted capability commit identity invalid")
    return value


def _provider_file(provider: str, repo_root: Path) -> Path:
    if not isinstance(provider, str) or not provider.startswith("studio.capabilities."):
        raise PromotedCapabilityError("promoted capability provider invalid")
    module = provider.removeprefix("studio.capabilities.")
    if not re.fullmatch(r"[a-z][a-z0-9_]{2,120}", module):
        raise PromotedCapabilityError("promoted capability provider invalid")
    return Path(repo_root) / "studio" / "capabilities" / (module + ".py")


def sync_into_registry(registry, path=DEFAULT_REGISTRY, *, repo_root=None):
    validate_registry(registry)
    path = Path(path)
    promoted = load(path)
    root = Path(repo_root) if repo_root is not None else path.resolve().parents[1]
    result = registry
    for name in sorted(promoted["capabilities"]):
        entry = promoted["capabilities"][name]
        provider = entry["provider"]
        provider_file = _provider_file(provider, root)
        if not provider_file.is_file() or provider_file.is_symlink():
            raise PromotedCapabilityError("promoted capability provider implementation missing")
        if has_capability(result, name):
            current = result["capabilities"][name]
            if current.get("provider") != provider:
                raise PromotedCapabilityError("promoted capability conflicts with project provider")
            continue
        result = register(
            result,
            name,
            provider,
            {
                "source": "promoted_factory_capability",
                "candidate_id": entry["candidate_id"],
                "baseline_sha": entry["baseline_sha"],
                "candidate_sha": entry["candidate_sha"],
            },
        )
    return result
