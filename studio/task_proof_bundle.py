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


def _path_absent(root: Path, rel: str) -> bool:
    root=root.resolve()
    target=(root/rel).resolve()
    try:
        target.relative_to(root)
    except ValueError:
        return False
    return not target.exists() and not target.is_symlink()


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

    file_refs=sorted({
        ref for ref in refs
        if not ref.startswith("command:") and not ref.startswith("absent:")
    })
    command_refs=sorted({ref for ref in refs if ref.startswith("command:")})
    absent_refs=sorted({ref for ref in refs if ref.startswith("absent:")})
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

    states=[]
    invalid_absent=[]
    for ref in absent_refs:
        rel=ref[len("absent:"):]
        if not rel or not _path_absent(Path(project_root),rel):
            invalid_absent.append(rel or ref)
        else:
            states.append({"ref":ref,"state":"absent"})
    if invalid_absent:
        raise TaskProofError("proof absence evidence invalid: "+", ".join(invalid_absent[:10]))

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
        "evidence_states":states,
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
    if not isinstance(value.get("evidence_states",[]),list):
        raise TaskProofError("proof states invalid")
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


def verify_evidence_files(value: dict, project_root: Path) -> dict:
    """Re-hash persisted file evidence against the restored repository workspace."""
    validate(value)
    mismatches=[]
    for item in value.get("evidence_files",[]):
        if not isinstance(item,dict):
            continue
        rel=str(item.get("ref") or "")
        current=_file_proof(Path(project_root),rel)
        if current is None:
            mismatches.append({"ref":rel,"reason":"missing"})
            continue
        if (
            current.get("sha256")!=item.get("sha256")
            or int(current.get("size",0))!=int(item.get("size",0))
        ):
            mismatches.append({
                "ref":rel,
                "reason":"hash_mismatch",
                "expected_sha256":item.get("sha256"),
                "actual_sha256":current.get("sha256"),
            })
    state_mismatches=[]
    for item in value.get("evidence_states",[]):
        if not isinstance(item,dict):
            continue
        ref=str(item.get("ref") or "")
        if item.get("state")=="absent" and ref.startswith("absent:"):
            rel=ref[len("absent:"):]
            if not _path_absent(Path(project_root),rel):
                state_mismatches.append(ref)
    if mismatches or state_mismatches:
        refs=[str(item.get("ref")) for item in mismatches[:10]] + state_mismatches[:10]
        raise TaskProofError("proof evidence mismatch: " + ", ".join(refs))
    return {
        "valid":True,
        "checked_files":len(value.get("evidence_files",[])),
        "checked_states":len(value.get("evidence_states",[])),
    }
