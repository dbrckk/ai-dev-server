"""Single source of truth for replacement GitHub CI trust requirements."""
from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse

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


def _trusted_check_run(run: dict, repository: str) -> bool:
    if not isinstance(run,dict):
        return False
    app=run.get("app")
    if not isinstance(app,dict) or app.get("slug")!=TRUSTED_CHECK_APP:
        return False
    details=run.get("details_url")
    if not isinstance(details,str):
        return False
    parsed=urlparse(details)
    return (
        parsed.scheme=="https"
        and parsed.netloc=="github.com"
        and parsed.path.startswith("/"+repository+"/actions/runs/")
    )

def validate_check_runs(runs: list[dict], repository: str) -> dict:
    trusted=[run for run in runs if _trusted_check_run(run,repository)]
    by_name={run.get("name"):run for run in trusted if isinstance(run.get("name"),str)}
    missing=sorted(REQUIRED_GITHUB_CHECKS-set(by_name))
    incomplete=sorted(
        name for name in REQUIRED_GITHUB_CHECKS
        if name in by_name and by_name[name].get("status")!="completed"
    )
    failed=sorted(
        name for name in REQUIRED_GITHUB_CHECKS
        if name in by_name and by_name[name].get("status")=="completed"
        and by_name[name].get("conclusion")!="success"
    )
    passed=sorted(
        name for name in REQUIRED_GITHUB_CHECKS
        if name in by_name and by_name[name].get("status")=="completed"
        and by_name[name].get("conclusion")=="success"
    )
    return {
        "valid":not missing and not incomplete and not failed,
        "required_checks":sorted(REQUIRED_GITHUB_CHECKS),
        "passed_checks":passed,
        "missing_checks":missing,
        "incomplete_checks":incomplete,
        "failed_checks":failed,
    }
