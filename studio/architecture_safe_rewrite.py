"""Build bounded retry context after an architecture-sensitive patch is rejected."""
from __future__ import annotations

import json

MAX_REJECTED_FILES = 12
MAX_CONTENT_PREVIEW = 800


def _patch_summary(patch: object) -> list[dict]:
    if not isinstance(patch, dict):
        return []
    files = patch.get("files")
    if not isinstance(files, list):
        return []
    result = []
    for item in files[:MAX_REJECTED_FILES]:
        if not isinstance(item, dict):
            continue
        path = item.get("path")
        content = item.get("content")
        if not isinstance(path, str):
            continue
        result.append({
            "path": path,
            "content_preview": content[:MAX_CONTENT_PREVIEW] if isinstance(content, str) else "",
        })
    return result


def build_context(
    base_context: str,
    rejected_patch: object,
    guard_error: str,
    *,
    engine: str,
) -> str:
    payload = {
        "architecture_safe_rewrite": {
            "engine": engine,
            "required": True,
            "attempt": 1,
            "rules": [
                "Preserve the existing architecture and dependency graph.",
                "Do not modify dependency manifests, build configuration, CI, infrastructure, routing architecture, dependency injection architecture, persistence architecture, or core service boundaries.",
                "Advance the original objective using only local implementation changes that fit the current architecture.",
                "Do not repeat any architecture-sensitive part of the rejected patch.",
                "Return a complete patch in the same schema expected for implementation.",
            ],
            "guard_error": str(guard_error)[:2000],
            "rejected_patch_summary": _patch_summary(rejected_patch),
        }
    }
    return base_context + "\nARCHITECTURE_SAFE_REWRITE:\n" + json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
