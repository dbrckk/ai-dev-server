"""Bound telemetry retention for long-running autonomous projects."""
from __future__ import annotations

from pathlib import Path

from atomic_file import write_text as atomic_write_text
from file_lock import exclusive

MAX_BYTES = 8 * 1024 * 1024
TARGET_BYTES = 4 * 1024 * 1024


def compact(path: Path) -> dict:
    path = Path(path)
    if not path.is_file():
        return {"compacted": False, "bytes_before": 0, "bytes_after": 0}

    before = path.stat().st_size
    if before <= MAX_BYTES:
        return {"compacted": False, "bytes_before": before, "bytes_after": before}

    with exclusive(path):
        try:
            raw = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            return {"compacted": False, "bytes_before": before, "bytes_after": before}

        lines = raw.splitlines()
        kept = []
        used = 0
        for line in reversed(lines):
            encoded = (line + "\n").encode("utf-8")
            if used + len(encoded) > TARGET_BYTES and kept:
                break
            kept.append(line)
            used += len(encoded)
        kept.reverse()
        text = "\n".join(kept)
        if text:
            text += "\n"
        atomic_write_text(path, text, encoding="utf-8")
        after = path.stat().st_size if path.is_file() else 0

    return {
        "compacted": True,
        "bytes_before": before,
        "bytes_after": after,
    }
