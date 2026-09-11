"""Persistent trusted memory for projects, research and reusable experience."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path

VERSION = 1
KINDS = {"project", "research", "experience"}


class MemoryError(ValueError):
    pass


def _canon(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def _seal(value):
    out = dict(value)
    out.pop("memory_sha256", None)
    out["memory_sha256"] = hashlib.sha256(_canon(out)).hexdigest()
    return out


def new_memory():
    return _seal({"version": VERSION, "entries": []})


def validate(memory):
    if not isinstance(memory, dict) or memory.get("version") != VERSION or not isinstance(memory.get("entries"), list):
        raise MemoryError("memory invalid")
    digest = memory.get("memory_sha256")
    unsigned = dict(memory)
    unsigned.pop("memory_sha256", None)
    if not isinstance(digest, str) or hashlib.sha256(_canon(unsigned)).hexdigest() != digest:
        raise MemoryError("memory integrity failure")
    for entry in memory["entries"]:
        _validate_entry(entry)
    return memory


def _validate_entry(entry):
    required = {
        "id", "kind", "project_id", "summary", "tags", "evidence",
        "provenance", "reusable", "confidence"
    }
    if not isinstance(entry, dict) or set(entry) != required:
        raise MemoryError("entry malformed")
    if not isinstance(entry["id"], str) or not entry["id"].strip():
        raise MemoryError("entry id invalid")
    if entry["kind"] not in KINDS:
        raise MemoryError("entry kind invalid")
    if not isinstance(entry["project_id"], str) or not entry["project_id"].strip():
        raise MemoryError("project id invalid")
    if not isinstance(entry["summary"], str) or not entry["summary"].strip() or len(entry["summary"]) > 4000:
        raise MemoryError("summary invalid")
    if not isinstance(entry["tags"], list) or any(not isinstance(x, str) or not x.strip() for x in entry["tags"]):
        raise MemoryError("tags invalid")
    if len(set(entry["tags"])) != len(entry["tags"]):
        raise MemoryError("tags duplicated")
    if not isinstance(entry["evidence"], dict) or not entry["evidence"]:
        raise MemoryError("evidence required")
    if not isinstance(entry["provenance"], dict) or not entry["provenance"]:
        raise MemoryError("provenance required")
    if not isinstance(entry["reusable"], bool):
        raise MemoryError("reusable invalid")
    if not isinstance(entry["confidence"], int) or isinstance(entry["confidence"], bool) or not 0 <= entry["confidence"] <= 100:
        raise MemoryError("confidence invalid")
    if entry["reusable"] and entry["confidence"] < 80:
        raise MemoryError("reusable memory requires high confidence")


def add_entry(memory, *, entry_id, kind, project_id, summary, tags, evidence, provenance,
              reusable=False, confidence=100):
    validate(memory)
    entry = {
        "id": entry_id,
        "kind": kind,
        "project_id": project_id,
        "summary": summary,
        "tags": list(tags),
        "evidence": evidence,
        "provenance": provenance,
        "reusable": reusable,
        "confidence": confidence,
    }
    _validate_entry(entry)
    if any(item["id"] == entry_id for item in memory["entries"]):
        raise MemoryError("entry id already exists")
    out = {"version": VERSION, "entries": [*memory["entries"], entry]}
    return _seal(out)


def query(memory, *, project_id=None, kind=None, tags=None, reusable_only=False):
    validate(memory)
    if kind is not None and kind not in KINDS:
        raise MemoryError("query kind invalid")
    wanted_tags = set(tags or [])
    result = []
    for entry in memory["entries"]:
        if project_id is not None and entry["project_id"] != project_id:
            continue
        if kind is not None and entry["kind"] != kind:
            continue
        if reusable_only and not entry["reusable"]:
            continue
        if wanted_tags and not wanted_tags.issubset(set(entry["tags"])):
            continue
        result.append(dict(entry))
    return result


def reusable_for_project(memory, target_project_id, *, tags=None):
    validate(memory)
    if not isinstance(target_project_id, str) or not target_project_id.strip():
        raise MemoryError("target project invalid")
    items = query(memory, tags=tags, reusable_only=True)
    return [item for item in items if item["project_id"] != target_project_id]


def save(path, memory):
    validate(memory)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(memory, handle, ensure_ascii=False, sort_keys=True, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass


def load(path):
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MemoryError("memory unreadable") from exc
    return validate(value)
