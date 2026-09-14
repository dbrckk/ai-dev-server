"""Single source of truth for replacement GitHub CI trust requirements."""
from __future__ import annotations

import re
from pathlib import Path

REQUIRED_GITHUB_CHECKS=frozenset({"validate","python-tests"})
TRUSTED_CHECK_APP="github-actions"

def workflow_job_ids(path: Path) -> set[str]:
    text=path.read_text(encoding="utf-8")
    jobs=set()
    in_jobs=False
    for line in text.splitlines():
        if line.strip()=="jobs:" and not line.startswith(" "):
            in_jobs=True
            continue
        if not in_jobs:
            continue
        if line and not line.startswith(" "):
            break
        match=re.match(r"^  ([A-Za-z0-9_-]+):\s*$",line)
        if match:
            jobs.add(match.group(1))
    return jobs

def validate_workflow(path: Path) -> dict:
    jobs=workflow_job_ids(path)
    missing=sorted(REQUIRED_GITHUB_CHECKS-jobs)
    return {
        "valid":not missing,
        "required_checks":sorted(REQUIRED_GITHUB_CHECKS),
        "workflow_jobs":sorted(jobs),
        "missing_checks":missing,
    }
