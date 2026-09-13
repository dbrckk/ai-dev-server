"""Integrity-sealed persistent failure memory for generic autonomous runs."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path

VERSION = 1


class FailureMemoryError(ValueError):
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
        raise FailureMemoryError("failure memory project invalid")
    if not isinstance(engine, str) or not engine.strip():
        raise FailureMemoryError("failure memory engine invalid")
    if not isinstance(base_sha, str) or len(base_sha) != 40:
        raise FailureMemoryError("failure memory base sha invalid")
    return _seal({
        "version": VERSION,
        "project_id": project_id,
        "engine": engine,
        "base_sha": base_sha,
        "signature": None,
        "repeated_failures": 0,
        "avoid_providers": [],
        "avoid_models": [],
    })


def validate(value: dict) -> dict:
    if not isinstance(value, dict):
        raise FailureMemoryError("failure memory invalid")
    digest = value.get("sha256")
    if not isinstance(digest, str) or len(digest) != 64:
        raise FailureMemoryError("failure memory digest invalid")
    unsigned = dict(value)
    unsigned.pop("sha256", None)
    if hashlib.sha256(_canonical(unsigned)).hexdigest() != digest:
        raise FailureMemoryError("failure memory integrity failure")
    if value.get("version") != VERSION:
        raise FailureMemoryError("failure memory version invalid")
    if not isinstance(value.get("project_id"), str) or not value["project_id"].strip():
        raise FailureMemoryError("failure memory project invalid")
    if not isinstance(value.get("engine"), str) or not value["engine"].strip():
        raise FailureMemoryError("failure memory engine invalid")
    if not isinstance(value.get("base_sha"), str) or len(value["base_sha"]) != 40:
        raise FailureMemoryError("failure memory base sha invalid")
    signature = value.get("signature")
    if signature is not None and (not isinstance(signature, str) or len(signature) != 64):
        raise FailureMemoryError("failure memory signature invalid")
    repeated = value.get("repeated_failures")
    if type(repeated) is not int or repeated < 0:
        raise FailureMemoryError("failure memory repeat count invalid")
    for key in ("avoid_providers", "avoid_models"):
        items = value.get(key)
        if not isinstance(items, list) or any(not isinstance(item, str) or not item for item in items):
            raise FailureMemoryError("failure memory identity list invalid")
        if len(set(items)) != len(items):
            raise FailureMemoryError("failure memory identity list duplicated")
    if repeated == 0 and signature is not None:
        raise FailureMemoryError("failure memory zero-count signature invalid")
    if repeated > 0 and signature is None:
        raise FailureMemoryError("failure memory missing signature")
    return value


def resume(memory: dict, *, project_id: str, engine: str, base_sha: str) -> dict:
    validate(memory)
    if (
        memory.get("project_id") != project_id
        or memory.get("engine") != engine
        or memory.get("base_sha") != base_sha
    ):
        return new(project_id, engine, base_sha)
    return memory


def advance(
    memory: dict,
    *,
    base_sha: str,
    signature: str | None,
    repeated_failures: int,
    avoid_providers: list[str],
    avoid_models: list[str],
) -> dict:
    validate(memory)
    if not isinstance(base_sha, str) or len(base_sha) != 40:
        raise FailureMemoryError("failure memory base sha invalid")
    if type(repeated_failures) is not int or repeated_failures < 0:
        raise FailureMemoryError("failure memory repeat count invalid")
    if repeated_failures == 0:
        signature = None
        avoid_providers = []
        avoid_models = []
    elif not isinstance(signature, str) or len(signature) != 64:
        raise FailureMemoryError("failure memory signature invalid")
    item = {
        "version": VERSION,
        "project_id": memory["project_id"],
        "engine": memory["engine"],
        "base_sha": base_sha,
        "signature": signature,
        "repeated_failures": repeated_failures,
        "avoid_providers": sorted(set(avoid_providers)),
        "avoid_models": sorted(set(avoid_models)),
    }
    return _seal(item)


def save(path: Path, memory: dict) -> None:
    validate(memory)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(memory, handle, sort_keys=True, ensure_ascii=False, indent=2)
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
        raise FailureMemoryError("failure memory unreadable") from exc
    return validate(value)
