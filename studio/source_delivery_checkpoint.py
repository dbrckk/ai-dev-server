"""Bind published-source resumption to its request, commit and exact bytes."""
from __future__ import annotations

import hashlib
import re
from contextlib import contextmanager
from pathlib import Path

from core import APIError, StudioError, canonical
from execution_checkpoint import ExecutionCheckpointError, advance, load


class SourceCheckpointError(StudioError):
    """A changed checkpoint requires new evidence, never another model edit."""


class SourceDeliveryHTTPError(APIError):
    def __init__(self, stage: str, status: int):
        if stage not in {"restore", "publish", "review", "target_ci"}:
            raise ValueError("Invalid source delivery stage")
        if type(status) is not int or not 100 <= status <= 599:
            raise ValueError("Invalid source delivery HTTP status")
        super().__init__(status)
        self.source_stage = stage
        self.args = (f"Source delivery {stage} failed: HTTP {status}",)


@contextmanager
def source_operation(stage: str):
    try:
        yield
    except APIError as exc:
        raise SourceDeliveryHTTPError(stage, exc.status) from None


def request_fingerprint(request: dict) -> str:
    operator = request.get("production_os") or {}
    identity = {key: request.get(key) for key in (
        "id", "target_repo", "repository_branch_id", "brief",
    )}
    identity["production_os"] = {key: operator.get(key) for key in (
        "workflow_id", "workflow_task_id",
    )}
    return hashlib.sha256(canonical(identity).encode("utf-8")).hexdigest()


def load_published_source(path: Path, request: dict, source_path: str) -> dict | None:
    if not path.exists() and not path.is_symlink():
        return None
    if path.is_symlink() or not path.is_file():
        raise SourceCheckpointError("Source delivery checkpoint path invalid")
    try:
        checkpoint = load(path)
    except ExecutionCheckpointError as exc:
        raise SourceCheckpointError("Source delivery checkpoint invalid") from exc
    evidence = checkpoint.get("last_verification")
    if (checkpoint["project_id"] != request["id"]
            or checkpoint["engine"] != "generic" or checkpoint["round"] != 1
            or checkpoint["phase"] not in {"published", "complete"}
            or not re.fullmatch(r"[a-f0-9]{40}", checkpoint["base_sha"])
            or not isinstance(evidence, dict)
            or evidence.get("request_fingerprint") != request_fingerprint(request)
            or evidence.get("target_repo") != request["target_repo"]
            or evidence.get("source_path") != source_path
            or evidence.get("changed_files") != [source_path]
            or evidence.get("model_authored") is not True
            or evidence.get("source_validation") != "passed"):
        raise SourceCheckpointError("Source delivery checkpoint identity mismatch")
    return checkpoint


def resume_published_source(path: Path, request: dict, source_path: str,
                            commit_sha: str, source: str) -> tuple[dict, dict] | None:
    checkpoint = load_published_source(path, request, source_path)
    if checkpoint is None:
        return None
    evidence = dict(checkpoint["last_verification"])
    if (checkpoint["base_sha"] != commit_sha
            or evidence.get("updated_source_sha256")
            != hashlib.sha256(source.encode("utf-8")).hexdigest()):
        raise SourceCheckpointError("Source delivery checkpoint source changed")
    # Revalidate review/CI even after an earlier successful observation.
    evidence.update(status="pending", passed=False, target_ci="pending_exact_commit")
    evidence.pop("target_ci_run_id", None)
    return advance(checkpoint, phase="published", last_verification=evidence), evidence
