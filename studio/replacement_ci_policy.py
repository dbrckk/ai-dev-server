"""Single source of truth for replacement GitHub CI trust requirements."""
from __future__ import annotations

import re
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlparse

REQUIRED_GITHUB_CHECKS=frozenset({"validate","python-tests"})
TRUSTED_CHECK_APP="github-actions"
REQUIRED_WORKFLOW_NAME="CI"
REQUIRED_WORKFLOW_PATH=".github/workflows/ci.yml"

# Explicit allowlist: third-party actions and mutable refs are fail-closed.
TRUSTED_ACTION_REVISIONS={
    "actions/checkout":"11d5960a326750d5838078e36cf38b85af677262",
    "actions/setup-python":"a26af69be951a213d495a4c3e4e4022e16d87065",
}

def workflow_action_uses_text(text: str) -> list[dict]:
    rows=[]
    pattern=re.compile(r"(?m)^\s*(?:-\s*)?uses:\s*([^#\s]+)\s*(?:#.*)?$")
    for match in pattern.finditer(text):
        value=match.group(1).strip().strip("'\"")
        if value.startswith("./"):
            rows.append({
                "uses":value,
                "action":value,
                "revision":None,
                "kind":"local",
            })
            continue
        if "@" not in value:
            rows.append({
                "uses":value,
                "action":value,
                "revision":None,
                "kind":"remote",
            })
            continue
        action,revision=value.rsplit("@",1)
        rows.append({
            "uses":value,
            "action":action,
            "revision":revision,
            "kind":"remote",
        })
    return rows

def validate_action_pinning_text(text: str) -> dict:
    uses=workflow_action_uses_text(text)
    violations=[]
    trusted=[]
    for row in uses:
        action=row["action"]
        revision=row["revision"]
        if row["kind"]=="local":
            violations.append({
                "uses":row["uses"],
                "reason":"local_action_not_allowlisted",
            })
            continue
        expected=TRUSTED_ACTION_REVISIONS.get(action)
        if expected is None:
            violations.append({
                "uses":row["uses"],
                "reason":"action_not_allowlisted",
            })
            continue
        if not isinstance(revision,str) or re.fullmatch(r"[0-9a-fA-F]{40}",revision) is None:
            violations.append({
                "uses":row["uses"],
                "reason":"mutable_or_non_sha_revision",
            })
            continue
        if revision.lower()!=expected.lower():
            violations.append({
                "uses":row["uses"],
                "reason":"unapproved_action_revision",
                "expected_revision":expected,
            })
            continue
        trusted.append({
            "action":action,
            "revision":revision.lower(),
        })
    return {
        "valid":not violations,
        "trusted_actions":trusted,
        "violations":violations,
        "allowlist":dict(sorted(TRUSTED_ACTION_REVISIONS.items())),
    }

def workflow_job_ids_text(text: str) -> set[str]:
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

def workflow_job_ids(path: Path) -> set[str]:
    return workflow_job_ids_text(path.read_text(encoding="utf-8"))

def validate_workflow_text(text: str) -> dict:
    jobs=workflow_job_ids_text(text)
    missing=sorted(REQUIRED_GITHUB_CHECKS-jobs)
    name_match=re.search(r"(?m)^name:\s*([^#\n]+?)\s*$",text)
    workflow_name=name_match.group(1).strip().strip("'\"") if name_match else None
    action_policy=validate_action_pinning_text(text)
    return {
        "valid":not missing and workflow_name==REQUIRED_WORKFLOW_NAME and action_policy["valid"],
        "required_checks":sorted(REQUIRED_GITHUB_CHECKS),
        "workflow_jobs":sorted(jobs),
        "missing_checks":missing,
        "workflow_name":workflow_name,
        "expected_workflow_name":REQUIRED_WORKFLOW_NAME,
        "action_pinning":action_policy,
    }

def validate_workflow(path: Path) -> dict:
    return validate_workflow_text(path.read_text(encoding="utf-8"))


def _workflow_run_id_from_details(run: dict, repository: str) -> int | None:
    if not isinstance(run,dict):
        return None
    details=run.get("details_url")
    if not isinstance(details,str):
        return None
    parsed=urlparse(details)
    if parsed.scheme!="https" or parsed.netloc!="github.com":
        return None
    prefix="/"+repository+"/actions/runs/"
    if not parsed.path.startswith(prefix):
        return None
    suffix=parsed.path[len(prefix):]
    token=suffix.split("/",1)[0]
    try:
        value=int(token)
    except (TypeError,ValueError):
        return None
    return value if value>0 else None

def _trusted_check_run(run: dict, repository: str) -> bool:
    if not isinstance(run,dict):
        return False
    app=run.get("app")
    if not isinstance(app,dict) or app.get("slug")!=TRUSTED_CHECK_APP:
        return False
    return _workflow_run_id_from_details(run,repository) is not None

def _timestamp(value) -> float | None:
    if isinstance(value,(int,float)):
        return float(value)
    if not isinstance(value,str) or not value:
        return None
    try:
        text=value[:-1]+"+00:00" if value.endswith("Z") else value
        dt=datetime.fromisoformat(text)
        if dt.tzinfo is None:
            dt=dt.replace(tzinfo=timezone.utc)
        return dt.timestamp()
    except ValueError:
        return None

def _check_timestamp(run: dict) -> float | None:
    if not isinstance(run,dict):
        return None
    for key in ("started_at","completed_at","created_at","updated_at"):
        ts=_timestamp(run.get(key))
        if ts is not None:
            return ts
    return None

def validate_check_runs(runs: list[dict], repository: str, *, commit_sha: str | None=None, head_commit_timestamp: float | None=None) -> dict:
    trusted=[run for run in runs if _trusted_check_run(run,repository)]
    if commit_sha is not None:
        trusted=[
            run for run in trusted
            if run.get("head_sha") in (None,commit_sha)
        ]
    by_name={}
    for run in trusted:
        name=run.get("name")
        if not isinstance(name,str):
            continue
        current=by_name.get(name)
        current_ts=_check_timestamp(current) if current else None
        run_ts=_check_timestamp(run)
        current_id=int(current.get("id") or 0) if isinstance(current,dict) else -1
        run_id=int(run.get("id") or 0)
        current_key=(current_ts if current_ts is not None else float("-inf"),current_id)
        run_key=(run_ts if run_ts is not None else float("-inf"),run_id)
        if current is None or run_key>=current_key:
            by_name[name]=run
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
    stale=sorted(
        name for name in REQUIRED_GITHUB_CHECKS
        if name in by_name and head_commit_timestamp is not None
        and (
            _check_timestamp(by_name[name]) is None
            or _check_timestamp(by_name[name])<float(head_commit_timestamp)
        )
    )
    passed=sorted(
        name for name in REQUIRED_GITHUB_CHECKS
        if name in by_name and by_name[name].get("status")=="completed"
        and by_name[name].get("conclusion")=="success"
        and name not in stale
    )
    evidence={
        name:{
            "id":by_name[name].get("id"),
            "head_sha":by_name[name].get("head_sha"),
            "timestamp":_check_timestamp(by_name[name]),
            "status":by_name[name].get("status"),
            "conclusion":by_name[name].get("conclusion"),
            "workflow_run_id":_workflow_run_id_from_details(by_name[name],repository),
        }
        for name in sorted(REQUIRED_GITHUB_CHECKS)
        if name in by_name
    }
    workflow_run_ids=sorted({
        row.get("workflow_run_id")
        for row in evidence.values()
        if isinstance(row.get("workflow_run_id"),int)
    })
    mixed_workflow_runs=(
        len(workflow_run_ids)>1
        or (not missing and len(workflow_run_ids)!=1)
    )
    return {
        "valid":not missing and not incomplete and not failed and not stale and not mixed_workflow_runs,
        "required_checks":sorted(REQUIRED_GITHUB_CHECKS),
        "passed_checks":passed,
        "missing_checks":missing,
        "incomplete_checks":incomplete,
        "failed_checks":failed,
        "stale_checks":stale,
        "check_evidence":evidence,
        "workflow_run_ids":workflow_run_ids,
        "common_workflow_run_id":workflow_run_ids[0] if len(workflow_run_ids)==1 else None,
        "mixed_workflow_runs":mixed_workflow_runs,
    }
