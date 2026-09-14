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
