"""Validate model-generated replacement candidates before isolated execution."""
from __future__ import annotations
from pathlib import Path

class ReplacementCandidateRejected(ValueError):
    pass

MAX_FILES=64
MAX_FILE_BYTES=256*1024
MAX_TOTAL_BYTES=2*1024*1024
ALLOWED_COMMANDS={"python3","python","flutter","dart"}
PROTECTED_PREFIXES=(".git/",".github/workflows/","studio/","tests/test_architecture_")
PROTECTED_FILES={".env",".env.local",".env.production"}

def _safe_path(value):
    if not isinstance(value,str) or not value or value.startswith("/"):
        raise ReplacementCandidateRejected("candidate path invalid")
    normalized=value.replace(chr(92),"/")
    if ".." in Path(normalized).parts:
        raise ReplacementCandidateRejected("candidate path traversal")
    if normalized in PROTECTED_FILES or any(normalized.startswith(x) for x in PROTECTED_PREFIXES):
        raise ReplacementCandidateRejected("candidate path protected")
    return normalized

def validate(order,candidate):
    if not isinstance(order,dict) or not isinstance(candidate,dict):
        raise ReplacementCandidateRejected("replacement candidate malformed")
    if candidate.get("version")!=1:
        raise ReplacementCandidateRejected("replacement candidate version invalid")
    if candidate.get("work_order_id")!=order.get("id"):
        raise ReplacementCandidateRejected("replacement candidate identity mismatch")
    if candidate.get("current_repo")!=order.get("current_repo"):
        raise ReplacementCandidateRejected("current repo mismatch")
    if candidate.get("replacement_repo")!=order.get("replacement_repo"):
        raise ReplacementCandidateRejected("replacement repo mismatch")

    files=candidate.get("files")
    if not isinstance(files,list) or not files or len(files)>MAX_FILES:
        raise ReplacementCandidateRejected("replacement candidate files invalid")
    normalized_files=[]
    seen=set()
    total=0
    for item in files:
        if not isinstance(item,dict) or set(item)!={"path","content"}:
            raise ReplacementCandidateRejected("replacement file malformed")
        path=_safe_path(item["path"])
        content=item["content"]
        if not isinstance(content,str):
            raise ReplacementCandidateRejected("replacement file content invalid")
        if path in seen:
            raise ReplacementCandidateRejected("duplicate replacement path")
        seen.add(path)
        size=len(content.encode("utf-8"))
        if size>MAX_FILE_BYTES:
            raise ReplacementCandidateRejected("replacement file too large")
        total+=size
        if total>MAX_TOTAL_BYTES:
            raise ReplacementCandidateRejected("replacement candidate too large")
        normalized_files.append({"path":path,"content":content})

    commands=candidate.get("validation_commands")
    if not isinstance(commands,list) or not commands or len(commands)>8:
        raise ReplacementCandidateRejected("validation commands invalid")
    normalized_commands=[]
    for command in commands:
        if not isinstance(command,list) or not command or not all(isinstance(x,str) and x for x in command):
            raise ReplacementCandidateRejected("validation command malformed")
        if command[0] not in ALLOWED_COMMANDS:
            raise ReplacementCandidateRejected("validation executable not allowed")
        normalized_commands.append(command[:16])

    notes=candidate.get("notes")
    if notes is not None and not isinstance(notes,str):
        raise ReplacementCandidateRejected("candidate notes invalid")

    return {
        "version":1,
        "status":"replacement_candidate_validated",
        "work_order_id":order.get("id"),
        "current_repo":order.get("current_repo"),
        "replacement_repo":order.get("replacement_repo"),
        "baseline_sha":candidate.get("baseline_sha"),
        "files":normalized_files,
        "validation_commands":normalized_commands,
        "notes":notes[:4000] if isinstance(notes,str) else "",
    }
