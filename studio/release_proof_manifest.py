"""Release-level manifest aggregating verified task proof bundles."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path

from task_proof_bundle import TaskProofError, filename as task_proof_filename, load as load_task_proof

VERSION=1


class ReleaseProofError(ValueError):
    pass


def _canonical(value: dict) -> bytes:
    return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")


def _seal(value: dict) -> dict:
    item=dict(value)
    item.pop("sha256",None)
    item["sha256"]=hashlib.sha256(_canonical(item)).hexdigest()
    return item


def build(*, proof_dir: Path, project_id: str, objective_dag: dict, release_commit: str) -> dict:
    if not isinstance(project_id,str) or not project_id.strip():
        raise ReleaseProofError("release proof project invalid")
    if not isinstance(release_commit,str) or len(release_commit)!=40:
        raise ReleaseProofError("release proof commit invalid")
    if not isinstance(objective_dag,dict):
        raise ReleaseProofError("release proof dag invalid")

    tasks=objective_dag.get("tasks")
    if not isinstance(tasks,list) or not tasks:
        raise ReleaseProofError("release proof tasks invalid")

    entries=[]
    for task in tasks:
        if not isinstance(task,dict):
            raise ReleaseProofError("release proof task invalid")
        if task.get("state")!="verified":
            raise ReleaseProofError("release proof requires fully verified DAG")
        task_id=str(task.get("id") or "")
        commit=task.get("last_commit")
        if not task_id or not isinstance(commit,str) or len(commit)!=40:
            raise ReleaseProofError("release proof task commit invalid")
        proof_path=Path(proof_dir)/task_proof_filename(task_id,commit)
        if not proof_path.is_file():
            raise ReleaseProofError("release task proof missing: "+task_id)
        try:
            proof=load_task_proof(proof_path)
        except TaskProofError as exc:
            raise ReleaseProofError("release task proof invalid: "+task_id+": "+str(exc)) from None
        if proof.get("project_id")!=project_id:
            raise ReleaseProofError("release task proof project mismatch: "+task_id)
        if proof.get("commit")!=commit:
            raise ReleaseProofError("release task proof commit mismatch: "+task_id)
        proof_task=proof.get("task") if isinstance(proof.get("task"),dict) else {}
        if proof_task.get("id")!=task_id:
            raise ReleaseProofError("release task proof id mismatch: "+task_id)
        entries.append({
            "task_id":task_id,
            "commit":commit,
            "proof_file":proof_path.name,
            "proof_sha256":proof["sha256"],
            "confidence":task.get("confidence"),
            "critical":bool(task.get("critical",False)),
        })

    entries.sort(key=lambda item:item["task_id"])
    return _seal({
        "version":VERSION,
        "project_id":project_id,
        "release_commit":release_commit,
        "task_count":len(entries),
        "tasks":entries,
    })


def validate(value: dict) -> dict:
    if not isinstance(value,dict):
        raise ReleaseProofError("release proof invalid")
    digest=value.get("sha256")
    if not isinstance(digest,str) or len(digest)!=64:
        raise ReleaseProofError("release proof digest invalid")
    unsigned=dict(value)
    unsigned.pop("sha256",None)
    if hashlib.sha256(_canonical(unsigned)).hexdigest()!=digest:
        raise ReleaseProofError("release proof integrity failure")
    if value.get("version")!=VERSION:
        raise ReleaseProofError("release proof version invalid")
    if not isinstance(value.get("release_commit"),str) or len(value["release_commit"])!=40:
        raise ReleaseProofError("release proof commit invalid")
    tasks=value.get("tasks")
    if not isinstance(tasks,list) or len(tasks)!=int(value.get("task_count",-1)):
        raise ReleaseProofError("release proof tasks invalid")
    return value


def save(path: Path,value: dict)->None:
    validate(value)
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix=path.name+".",dir=path.parent)
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as handle:
            json.dump(value,handle,sort_keys=True,ensure_ascii=False,indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp,path)
    finally:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass


def load(path: Path)->dict:
    try:
        value=json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError) as exc:
        raise ReleaseProofError("release proof unreadable") from exc
    return validate(value)
