"""Validate autonomous agent edits before they are trusted or published."""
from __future__ import annotations
from pathlib import Path
from generic_policy import editable, validate_patch

MAX_SNAPSHOT_BYTES=8_000_000

def snapshot(root:Path)->dict[str,str]:
    root=root.resolve(); out={}; total=0
    for p in sorted(root.rglob("*")):
        if not p.is_file() or p.is_symlink(): continue
        rel=p.relative_to(root).as_posix()
        if not editable(rel): continue
        try: text=p.read_text(encoding="utf-8")
        except (OSError,UnicodeError): continue
        total+=len(text.encode("utf-8"))
        if total>MAX_SNAPSHOT_BYTES: raise ValueError("Agent workspace snapshot too large")
        out[rel]=text
    return out

def validate_delta(root:Path,before:dict[str,str])->dict:
    after=snapshot(root)
    deleted=sorted(set(before)-set(after))
    if deleted:
        for rel in deleted:
            p=root/rel; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(before[rel],encoding="utf-8")
        raise ValueError("Agent file deletion is not allowed")
    changed=[]
    for rel,text in after.items():
        if before.get(rel)!=text:
            changed.append({"path":rel,"content":text})
    if not changed:
        return {"files":[],"changed":[]}
    normalized=validate_patch({"files":changed})
    return {"files":normalized,"changed":[x["path"] for x in normalized]}

def restore(root:Path,before:dict[str,str])->None:
    root=root.resolve()
    current=snapshot(root)
    for rel in set(current)-set(before):
        try: (root/rel).unlink()
        except OSError: pass
    for rel,text in before.items():
        p=root/rel; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(text,encoding="utf-8")
