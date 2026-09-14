"""Project-scoped CAS namespaces for safe cross-project storage."""
from __future__ import annotations

import hashlib
import re

from core import StudioError

_SAFE = re.compile(r"^[a-z0-9._-]{1,120}$")


def project_namespace(project_id: str) -> str:
    if not isinstance(project_id, str) or not project_id:
        raise StudioError("Artifact CAS project id invalid")
    normalized = project_id.strip().lower().replace("/", "--")
    if _SAFE.fullmatch(normalized):
        return normalized
    return "project-" + hashlib.sha256(project_id.encode("utf-8")).hexdigest()[:24]


def scoped_digest(project_id: str, content_digest: str) -> str:
    if (
        not isinstance(content_digest, str)
        or len(content_digest) != 64
        or any(ch not in "0123456789abcdef" for ch in content_digest)
    ):
        raise StudioError("Artifact CAS content digest invalid")
    namespace = project_namespace(project_id)
    return hashlib.sha256(
        ("studio-artifact-cas-v1\0" + namespace + "\0" + content_digest).encode("utf-8")
    ).hexdigest()
