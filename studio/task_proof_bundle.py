"""Immutable proof bundles for verified objective-DAG tasks."""
from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from pathlib import Path

VERSION=1
_SAFE_ID_RE=re.compile(r"[^A-Za-z0-9_.-]+")


class TaskProofError(ValueError):
    pass


def _canonical(value: dict) -> bytes:
    return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")


def _seal(value: dict) -> dict:
    item=dict(value)
    item.pop("sha256",None)
    item["sha256"]=hashlib.sha256(_canonical(item)).hexdigest()
    return item


def _safe_file(root: Path, rel: str) -> Path | None:
    root=root.resolve()
    target=(root/rel).resolve()
    try:
        target.relative_to(root)
    except ValueError:
        return None
    if not target.is_file() or target.is_symlink():
        return None
    return target


def _file_proof(root: Path, rel: str) -> dict | None:
    target=_safe_file(root,rel)
    if target is None:
        return None
    digest=hashlib.sha256()
    size=0
    try:
        with target.open("rb") as handle:
            while True:
                chunk=handle.read(1024*1024)
                if not chunk:
                    break
                digest.update(chunk)
                size+=len(chunk)
    except OSError:
        return None
    return {"ref":rel,"sha256":digest.hexdigest(),"size":size}


def build(
    *,
    project_root: Path,
    project_id: str,
    task: dict,
    commit: str,
    review: dict,
    verification: dict,
    confidence: dict,
) -> dict:
    if not isinstance(project_id,str) or not project_id.strip():
        raise TaskProofError("proof project invalid")
    if not isinstance(task,dict) or not isinstance(task.get("id"),str) or not task["id"]:
        raise TaskProofError("proof task invalid")
    if not isinstance(commit,str) or len(commit)!=40:
        raise TaskProofError("proof commit invalid")
    if not isinstance(review,dict) or review.get("complete") is not True:
        raise TaskProofError("proof review incomplete")
    if not isinstance(verification,dict) or verification.get("passed") is not True:
        raise TaskProofError("proof verification failed")
    if not isinstance(confidence,dict):
        raise TaskProofError("proof confidence invalid")

    criteria=[]
    refs=[]
    for row in review.get("criteria",[]):
        if not isinstance(row,dict):
            continue
        item_refs=[
            str(ref) for ref in row.get("evidence_refs",[])
            if isinstance(ref,str) and ref
        ]
        refs.extend(item_refs)
        criteria.append({
            "criterion":str(row.get("criterion") or ""),
            "passed":row.get("passed") is True,
            "evidence":str(row.get("evidence") or "")[:2000],
            "evidence_refs":item_refs[:20],
            "source":str(row.get("source") or "review"),
        })

    if not criteria or any(item["passed"] is not True for item in criteria):
        raise TaskProofError("proof acceptance criteria incomplete")

    file_refs=sorted({ref for ref in refs if not ref.startswith("command:")})
    command_refs=sorted({ref for ref in refs if ref.startswith("command:")})
    files=[]
    missing=[]
    for rel in file_refs:
        proof=_file_proof(Path(project_root),rel)
        if proof is None:
            missing.append(rel)
        else:
            files.append(proof)
    if missing:
        raise TaskProofError("proof evidence file missing: "+", ".join(missing[:10]))

    verification_record={
        "status":verification.get("status"),
        "passed":verification.get("passed"),
        "commands":verification.get("commands",[]),
        "stability_confirmed":verification.get("stability_confirmed"),
        "targeted_precheck":verification.get("targeted_precheck"),
        "targeted_impact":verification.get("targeted_impact"),
    }
    verification_digest=hashlib.sha256(_canonical(verification_record)).hexdigest()

    return _seal({
        "version":VERSION,
        "project_id":project_id,
        "task":{
            "id":task["id"],
            "title":str(task.get("title") or ""),
            "critical":bool(task.get("critical",False)),
            "done_when":list(task.get("done_when") or []),
        },
        "commit":commit,
        "criteria":criteria,
        "evidence_files":files,
        "evidence_commands":command_refs,
        "verification":verification_record,
        "verification_sha256":verification_digest,
        "confidence":confidence,
    })


def validate(value: dict) -> dict:
    if not isinstance(value,dict):
        raise TaskProofError("proof invalid")
    digest=value.get("sha256")
    if not isinstance(digest,str) or len(digest)!=64:
        raise TaskProofError("proof digest invalid")
    unsigned=dict(value)
    unsigned.pop("sha256",None)
    if hashlib.sha256(_canonical(unsigned)).hexdigest()!=digest:
        raise TaskProofError("proof integrity failure")
    if value.get("version")!=VERSION:
        raise TaskProofError("proof version invalid")
    if not isinstance(value.get("commit"),str) or len(value["commit"])!=40:
        raise TaskProofError("proof commit invalid")
    if not isinstance(value.get("criteria"),list) or not value["criteria"]:
        raise TaskProofError("proof criteria invalid")
    if any(not isinstance(item,dict) or item.get("passed") is not True for item in value["criteria"]):
        raise TaskProofError("proof criteria failed")
    if not isinstance(value.get("evidence_files"),list):
        raise TaskProofError("proof files invalid")
    return value


def filename(task_id: str, commit: str) -> str:
    safe=_SAFE_ID_RE.sub("-",str(task_id)).strip("-") or "task"
    return f"{safe}-{commit}.json"


def save(path: Path, value: dict) -> None:
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


def load(path: Path) -> dict:
    try:
        value=json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError) as exc:
        raise TaskProofError("proof unreadable") from exc
    return validate(value)
