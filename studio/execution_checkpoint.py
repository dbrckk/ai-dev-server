"""Integrity-sealed execution checkpoints for resumable autonomous work."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path

VERSION = 1
ALLOWED_PHASES = {"restored", "planned", "implemented", "verified", "published", "complete"}


class ExecutionCheckpointError(ValueError):
    pass


def _canonical(value: dict) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _seal(value: dict) -> dict:
    item = dict(value)
    item.pop("sha256", None)
    item["sha256"] = hashlib.sha256(_canonical(item)).hexdigest()
    return item


def new(project_id: str, engine: str, base_sha: str) -> dict:
    if not isinstance(project_id, str) or not project_id.strip():
        raise ExecutionCheckpointError("checkpoint project invalid")
    if not isinstance(engine, str) or not engine.strip():
        raise ExecutionCheckpointError("checkpoint engine invalid")
    if not isinstance(base_sha, str) or len(base_sha) != 40:
        raise ExecutionCheckpointError("checkpoint base sha invalid")
    return _seal({
        "version": VERSION,
        "project_id": project_id,
        "engine": engine,
        "base_sha": base_sha,
        "round": 0,
        "phase": "restored",
        "last_verification": None,
    })


def validate(value: dict) -> dict:
    if not isinstance(value, dict):
        raise ExecutionCheckpointError("checkpoint invalid")
    digest = value.get("sha256")
    if not isinstance(digest, str) or len(digest) != 64:
        raise ExecutionCheckpointError("checkpoint digest invalid")
    unsigned = dict(value)
    unsigned.pop("sha256", None)
    if hashlib.sha256(_canonical(unsigned)).hexdigest() != digest:
        raise ExecutionCheckpointError("checkpoint integrity failure")
    if value.get("version") != VERSION:
        raise ExecutionCheckpointError("checkpoint version invalid")
    if not isinstance(value.get("project_id"), str) or not value["project_id"].strip():
        raise ExecutionCheckpointError("checkpoint project invalid")
    if not isinstance(value.get("engine"), str) or not value["engine"].strip():
        raise ExecutionCheckpointError("checkpoint engine invalid")
    if not isinstance(value.get("base_sha"), str) or len(value["base_sha"]) != 40:
        raise ExecutionCheckpointError("checkpoint base sha invalid")
    if type(value.get("round")) is not int or value["round"] < 0:
        raise ExecutionCheckpointError("checkpoint round invalid")
    if value.get("phase") not in ALLOWED_PHASES:
        raise ExecutionCheckpointError("checkpoint phase invalid")
    last = value.get("last_verification")
    if last is not None and not isinstance(last, dict):
        raise ExecutionCheckpointError("checkpoint verification invalid")
    return value


def advance(
    checkpoint: dict,
    *,
    base_sha: str | None = None,
    round_index: int | None = None,
    phase: str | None = None,
    last_verification: dict | None = None,
) -> dict:
    validate(checkpoint)
    item = dict(checkpoint)
    item.pop("sha256", None)
    if base_sha is not None:
        if not isinstance(base_sha, str) or len(base_sha) != 40:
            raise ExecutionCheckpointError("checkpoint base sha invalid")
        item["base_sha"] = base_sha
    if round_index is not None:
        if type(round_index) is not int or round_index < item["round"]:
            raise ExecutionCheckpointError("checkpoint round regression")
        item["round"] = round_index
    if phase is not None:
        if phase not in ALLOWED_PHASES:
            raise ExecutionCheckpointError("checkpoint phase invalid")
        item["phase"] = phase
    if last_verification is not None:
        if not isinstance(last_verification, dict):
            raise ExecutionCheckpointError("checkpoint verification invalid")
        item["last_verification"] = last_verification
    return _seal(item)


def save(path: Path, checkpoint: dict) -> None:
    validate(checkpoint)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(checkpoint, handle, sort_keys=True, ensure_ascii=False, indent=2)
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
    except (OSError, json.JSONDecodeError) as exc:
        raise ExecutionCheckpointError("checkpoint unreadable") from exc
    return validate(value)
