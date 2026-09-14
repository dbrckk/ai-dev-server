"""Deny-by-default policy for cross-project CAS sharing."""
from __future__ import annotations

import re

from core import StudioError

_ALLOWED = {
    "toolchain-template",
    "public-test-fixture",
}
_SAFE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")


def validate_shareable_class(artifact_class: str | None) -> str:
    if not isinstance(artifact_class, str) or artifact_class not in _ALLOWED:
        raise StudioError("Artifact CAS shareable class is not approved")
    if not _SAFE.fullmatch(artifact_class):
        raise StudioError("Artifact CAS shareable class invalid")
    return artifact_class


def approved_classes() -> tuple[str, ...]:
    return tuple(sorted(_ALLOWED))


_MAX_SHAREABLE_BYTES = 2 * 1024 * 1024
_FORBIDDEN_MARKERS = (
    "BEGIN PRIVATE KEY",
    "BEGIN RSA PRIVATE KEY",
    "ghp_",
    "github_pat_",
    "AKIA",
    "AIza",
    "sk-",
)


def validate_shareable_payload(data: bytes, artifact_class: str | None) -> str:
    artifact_class = validate_shareable_class(artifact_class)
    if not isinstance(data, (bytes, bytearray)):
        raise StudioError("Artifact CAS shareable payload invalid")
    data = bytes(data)
    if len(data) == 0 or len(data) > _MAX_SHAREABLE_BYTES:
        raise StudioError("Artifact CAS shareable payload size invalid")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        raise StudioError("Artifact CAS binary payload cannot be shared") from None
    if "\x00" in text:
        raise StudioError("Artifact CAS binary-like payload cannot be shared")
    if any(marker in text for marker in _FORBIDDEN_MARKERS):
        raise StudioError("Artifact CAS shareable payload contains forbidden secret marker")
    return artifact_class
