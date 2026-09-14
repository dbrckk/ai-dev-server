"""Explicit promotion from project-private CAS to approved shared CAS."""
from __future__ import annotations

import os

from artifact_cas import get as cas_get, put as cas_put
from artifact_share_policy import validate_shareable_payload
from artifact_cas_audit import record as record_promotion
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
    project_id = os.environ.get("STUDIO_PROJECT_ID", "local-project")
    audit = record_promotion(
        project_id=project_id,
        artifact_class=artifact_class,
        digest=digest,
        size=size,
    )
    return {
        "status": "promoted",
        "artifact_class": artifact_class,
        "sha256": digest,
        "size": size,
        "audit_sequence": audit["sequence"],
    }
