"""Objective repository progress measurement for generic autonomous rounds."""
from __future__ import annotations

import hashlib
from pathlib import Path

from failure_loop import failure_signature

_SKIP_PARTS={".git","node_modules",".studio-venv",".studio-cmake-build","target","dist","build",".gradle",".idea",".vscode","__pycache__"}

def snapshot(root:Path)->dict:
    root=Path(root).resolve()
    files={}
    total_bytes=0
    for p in sorted(root.rglob("*")):
        if not p.is_file() or p.is_symlink():
            continue
        rel=p.relative_to(root)
        if any(part in _SKIP_PARTS for part in rel.parts):
            continue
        try:
            data=p.read_bytes()
        except OSError:
            continue
        # Ignore very large/binary artifacts; progress should reflect maintainable source/config.
        if len(data)>2_000_000 or b"\x00" in data[:4096]:
            continue
        key=rel.as_posix()
        files[key]=hashlib.sha256(data).hexdigest()
        total_bytes+=len(data)
    digest=hashlib.sha256(
        "\n".join(f"{k}:{files[k]}" for k in sorted(files)).encode("utf-8")
    ).hexdigest()
    return {"digest":digest,"files":files,"file_count":len(files),"bytes":total_bytes}

def compare(before:dict,after:dict,*,previous_verification:dict|None,current_verification:dict|None)->dict:
    before_files=before.get("files",{}) if isinstance(before,dict) else {}
    after_files=after.get("files",{}) if isinstance(after,dict) else {}
    added=sorted(set(after_files)-set(before_files))
    removed=sorted(set(before_files)-set(after_files))
    modified=sorted(k for k in set(before_files)&set(after_files) if before_files[k]!=after_files[k])
    changed=added+removed+modified

    prev_pass=isinstance(previous_verification,dict) and previous_verification.get("passed") is True
    cur_pass=isinstance(current_verification,dict) and current_verification.get("passed") is True
    prev_sig=failure_signature(previous_verification)
    cur_sig=failure_signature(current_verification)

    if prev_pass and not cur_pass:
        status="regression"
    elif cur_pass and not prev_pass:
        status="verified_progress"
    elif cur_pass and prev_pass:
        status="verified_stable" if not changed else "verified_progress"
    elif not changed:
        status="no_progress"
    elif prev_sig is not None and cur_sig == prev_sig:
        status="churn_without_verified_progress"
    elif cur_sig != prev_sig:
        status="progress_unverified"
    else:
        status="progress_unverified"

    return {
        "status":status,
        "changed":bool(changed),
        "changed_count":len(changed),
        "added":added[:100],
        "removed":removed[:100],
        "modified":modified[:100],
        "before_digest":before.get("digest"),
        "after_digest":after.get("digest"),
        "previous_verification_passed":prev_pass,
        "current_verification_passed":cur_pass,
        "previous_failure_signature":prev_sig,
        "current_failure_signature":cur_sig,
    }
