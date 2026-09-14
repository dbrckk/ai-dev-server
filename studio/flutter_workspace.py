"""Strict Flutter editable-workspace snapshots for isolated repair candidates."""
from __future__ import annotations

from pathlib import Path
import shutil

from core import StudioError, allowed, patch_check

MAX_BYTES = 2_000_000
TRANSIENT_PATHS = (
    ".dart_tool",
    "build",
    "test/goldens",
)


def snapshot(root: Path) -> dict[str, str]:
    root = root.resolve()
    result: dict[str, str] = {}
    total = 0
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        rel = path.relative_to(root).as_posix()
        if not allowed(rel):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            raise StudioError("Flutter repair workspace contains unreadable editable text") from None
        total += len(text.encode("utf-8"))
        if total > MAX_BYTES:
            raise StudioError("Flutter repair workspace snapshot too large")
        result[rel] = text
    return result


def delta(root: Path, before: dict[str, str]) -> dict:
    after = snapshot(root)
    deleted = sorted(set(before) - set(after))
    if deleted:
        raise StudioError("Repair candidate deleted editable files")
    changed = [
        {"path": rel, "content": text}
        for rel, text in after.items()
        if before.get(rel) != text
    ]
    if not changed:
        return {"files": [], "changed": []}
    normalized = patch_check({"files": changed})
    return {
        "files": normalized,
        "changed": [item["path"] for item in normalized],
    }


def restore(root: Path, before: dict[str, str]) -> None:
    root = root.resolve()
    current = snapshot(root)
    for rel in set(current) - set(before):
        try:
            (root / rel).unlink()
        except FileNotFoundError:
            pass
    for rel, text in before.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    clean_transients(root)


def clean_transients(root: Path) -> None:
    root = root.resolve()
    for rel in TRANSIENT_PATHS:
        path = root / rel
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
        elif path.exists():
            path.unlink(missing_ok=True)
