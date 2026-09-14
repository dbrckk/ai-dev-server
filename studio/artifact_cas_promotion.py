"""Explicit promotion from project-private CAS to approved shared CAS."""
from __future__ import annotations

from artifact_cas import get as cas_get, put as cas_put
from artifact_share_policy import validate_shareable_payload
from core import StudioError


ATTESTATION = "explicitly-public-generated-artifact-v1"


def promote_private(
    digest: str,
    size: int,
    *,
    artifact_class: str,
    attestation: str,
) -> dict:
    if attestation != ATTESTATION:
        raise StudioError("Artifact CAS promotion requires explicit public attestation")
    data = cas_get(digest, size, shareable=False)
    artifact_class = validate_shareable_payload(data, artifact_class)
    shared = cas_put(
        data,
        shareable=True,
        artifact_class=artifact_class,
    )
    if shared.get("sha256") != digest or shared.get("size") != size:
        raise StudioError("Artifact CAS promotion changed content identity")
    return {
        "status": "promoted",
        "artifact_class": artifact_class,
        "sha256": digest,
        "size": size,
    }
