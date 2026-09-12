"""Safe text-edit policy for generic autonomous projects."""
from __future__ import annotations

from pathlib import PurePosixPath
import re

MAX_FILE_BYTES = 400_000
MAX_PATCH_BYTES = 1_500_000
BLOCKED_PARTS = {
    ".git", ".github", ".idea", ".vscode", "node_modules", "vendor",
    "build", "dist", ".next", ".gradle", "target", "__pycache__", ".studio-venv", ".studio-cmake-build",
}
BLOCKED_NAMES = {
    ".env", ".env.local", ".env.production", "id_rsa", "id_ed25519",
}
BLOCKED_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".zip",
    ".jar", ".class", ".exe", ".dll", ".so", ".dylib", ".keystore", ".jks",
    ".p12", ".pfx", ".pem", ".key", ".crt", ".der", ".bin",
}
SECRET_RE = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----|github_pat_[A-Za-z0-9_]+|gh[pousr]_[A-Za-z0-9]+|sk-[A-Za-z0-9_-]{20,}|nvapi-[A-Za-z0-9_-]{15,}")


def editable(path: str) -> bool:
    if not isinstance(path, str) or not path or "\\" in path or path.startswith("/") or len(path) > 220:
        return False
    p = PurePosixPath(path)
    if any(part in ("", ".", "..") or part in BLOCKED_PARTS for part in p.parts):
        return False
    if p.name in BLOCKED_NAMES or p.name.startswith(".env"):
        return False
    if p.suffix.lower() in BLOCKED_SUFFIXES:
        return False
    return True


def validate_patch(value: object) -> list[dict]:
    if not isinstance(value, dict) or set(value) != {"files"} or not isinstance(value["files"], list):
        raise ValueError("Generic patch must be {files:[{path,content}]}")
    if not 1 <= len(value["files"]) <= 80:
        raise ValueError("Generic patch file count invalid")
    seen = set()
    total = 0
    normalized = []
    for item in value["files"]:
        if not isinstance(item, dict) or set(item) != {"path", "content"}:
            raise ValueError("Generic patch entry malformed")
        path, content = item["path"], item["content"]
        if not editable(path) or path in seen or not isinstance(content, str) or "\x00" in content:
            raise ValueError("Generic patch path/content rejected")
        raw = content.encode("utf-8")
        if len(raw) > MAX_FILE_BYTES or SECRET_RE.search(content):
            raise ValueError("Generic patch file rejected")
        total += len(raw)
        if total > MAX_PATCH_BYTES:
            raise ValueError("Generic patch too large")
        seen.add(path)
        normalized.append({"path": path, "content": content})
    return normalized
