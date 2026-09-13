"""Integrity-bound progress ledger for dependency-scheduled generic edits."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path

VERSION = 1
MAX_BATCHES = 100


class DependencyLedgerError(ValueError):
    pass


def _canonical(value: dict) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _seal(value: dict) -> dict:
    item = dict(value)
    item.pop("sha256", None)
    item["sha256"] = hashlib.sha256(_canonical(item)).hexdigest()
    return item


def new(project_id: str, base_sha: str) -> dict:
    if not isinstance(project_id, str) or not project_id.strip():
        raise DependencyLedgerError("dependency ledger project invalid")
    if not isinstance(base_sha, str) or len(base_sha) != 40:
        raise DependencyLedgerError("dependency ledger base sha invalid")
    return _seal({
        "version": VERSION,
        "project_id": project_id,
        "base_sha": base_sha,
        "batches": [],
        "verified_files": [],
    })


def validate(value: dict) -> dict:
    if not isinstance(value, dict):
        raise DependencyLedgerError("dependency ledger invalid")
    digest = value.get("sha256")
    if not isinstance(digest, str) or len(digest) != 64:
        raise DependencyLedgerError("dependency ledger digest invalid")
    unsigned = dict(value)
    unsigned.pop("sha256", None)
    if hashlib.sha256(_canonical(unsigned)).hexdigest() != digest:
        raise DependencyLedgerError("dependency ledger integrity failure")
    if value.get("version") != VERSION:
        raise DependencyLedgerError("dependency ledger version invalid")
    if not isinstance(value.get("project_id"), str) or not value["project_id"]:
        raise DependencyLedgerError("dependency ledger project invalid")
    if not isinstance(value.get("base_sha"), str) or len(value["base_sha"]) != 40:
        raise DependencyLedgerError("dependency ledger base sha invalid")
    batches = value.get("batches")
    if not isinstance(batches, list) or len(batches) > MAX_BATCHES:
        raise DependencyLedgerError("dependency ledger batches invalid")
    for batch in batches:
        if not isinstance(batch, dict):
            raise DependencyLedgerError("dependency ledger batch invalid")
        files = batch.get("files")
        if not isinstance(files, list) or any(not isinstance(x, str) or not x for x in files):
            raise DependencyLedgerError("dependency ledger batch files invalid")
        if not isinstance(batch.get("commit"), str) or len(batch["commit"]) != 40:
            raise DependencyLedgerError("dependency ledger batch commit invalid")
    verified = value.get("verified_files")
    if not isinstance(verified, list) or any(not isinstance(x, str) or not x for x in verified):
        raise DependencyLedgerError("dependency ledger verified files invalid")
    return value


def resume(value: dict, *, project_id: str, base_sha: str) -> dict:
    validate(value)
    if value.get("project_id") != project_id or value.get("base_sha") != base_sha:
        return new(project_id, base_sha)
    return value


def advance(value: dict, *, base_sha: str, files: list[str]) -> dict:
    validate(value)
    if not isinstance(base_sha, str) or len(base_sha) != 40:
        raise DependencyLedgerError("dependency ledger base sha invalid")
    clean = sorted(set(str(x) for x in files if x))
    batches = list(value["batches"])
    if clean:
        batches.append({"files": clean, "commit": base_sha})
    batches = batches[-MAX_BATCHES:]
    verified = sorted(set(value["verified_files"]) | set(clean))
    return _seal({
        "version": VERSION,
        "project_id": value["project_id"],
        "base_sha": base_sha,
        "batches": batches,
        "verified_files": verified,
    })


def suggestions(value: dict, graph: dict, *, limit: int = 20) -> dict:
    validate(value)
    reverse = graph.get("reverse", {}) if isinstance(graph, dict) else {}
    last_files = value["batches"][-1]["files"] if value["batches"] else []
    downstream = []
    seen = set()
    for rel in last_files:
        for dependent in reverse.get(rel, []):
            if dependent in seen:
                continue
            seen.add(dependent)
            downstream.append(dependent)
    return {
        "verified_files": value["verified_files"][-100:],
        "published_batches": len(value["batches"]),
        "last_batch": last_files,
        "next_dependents": sorted(downstream)[:limit],
    }


def save(path: Path, value: dict) -> None:
    validate(value)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, sort_keys=True, ensure_ascii=False, indent=2)
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
        raise DependencyLedgerError("dependency ledger unreadable") from exc
    return validate(value)
