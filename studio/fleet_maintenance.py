"""Safe maintenance for long-running autonomous project outputs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from telemetry_maintenance import compact as compact_telemetry

TMP_SUFFIXES = (".tmp", ".partial")


def _cleanup_temps(root: Path) -> dict:
    removed = 0
    bytes_removed = 0
    for path in root.rglob("*"):
        if not path.is_file() or path.is_symlink():
            continue
        if not path.name.endswith(TMP_SUFFIXES):
            continue
        size = path.stat().st_size
        path.unlink(missing_ok=True)
        removed += 1
        bytes_removed += size
    return {"removed": removed, "bytes_removed": bytes_removed}


def maintain_project(project_out: Path) -> dict:
    autonomy = project_out / ".autonomy"
    result = {
        "id": project_out.name,
        "telemetry": {"compacted": False, "bytes_before": 0, "bytes_after": 0},
        "temporary_files": {"removed": 0, "bytes_removed": 0},
    }
    if not autonomy.is_dir():
        return result
    result["telemetry"] = compact_telemetry(autonomy / "telemetry.jsonl")
    result["temporary_files"] = _cleanup_temps(autonomy)
    return result


def run(root: Path | str = "studio-output") -> dict:
    root = Path(root)
    projects = []
    if root.is_dir():
        for project in sorted(root.iterdir()):
            if project.is_dir() and (project / ".autonomy").is_dir():
                projects.append(maintain_project(project))
    return {
        "projects": projects,
        "summary": {
            "projects": len(projects),
            "telemetry_compacted": sum(1 for p in projects if p["telemetry"]["compacted"]),
            "temporary_files_removed": sum(p["temporary_files"]["removed"] for p in projects),
            "bytes_removed": sum(p["temporary_files"]["bytes_removed"] for p in projects),
        },
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="AI Dev Server fleet maintenance")
    parser.add_argument("--root", default="studio-output")
    args = parser.parse_args(argv)
    report = run(args.root)
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
