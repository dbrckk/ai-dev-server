"""Execute an explicitly supplied replacement candidate in an isolated worktree.

This executor does not synthesize migrations and never touches the default branch.
Candidate code is materialized only in a detached worktree. Validation commands run
inside the pinned container with networking disabled and no production credentials.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

from core import IMAGE, canonical

class ReplacementExecutionError(RuntimeError):
    pass

SAFE_ENV={
    "PATH":"/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
    "HOME":"/tmp/home",
    "LANG":"C.UTF-8",
    "LC_ALL":"C.UTF-8",
    "PYTHONDONTWRITEBYTECODE":"1",
    "PYTHONUNBUFFERED":"1",
}

PROTECTED_PREFIXES=(
    ".git/",
    ".github/workflows/",
    "studio/",
    "tests/test_architecture_",
)
PROTECTED_FILES={
    ".env",
    ".env.local",
    ".env.production",
}
MAX_FILES=64
MAX_FILE_BYTES=256*1024
MAX_TOTAL_BYTES=2*1024*1024

def _run(args, *, cwd=None, timeout=600, env=None, check=False):
    result=subprocess.run(
        args,cwd=cwd,env=env,text=True,capture_output=True,timeout=timeout
    )
    if check and result.returncode:
        raise ReplacementExecutionError("trusted command failed: "+str(args[0]))
    return result

def _sha(value, label):
    if not isinstance(value,str) or not re.fullmatch(r"[0-9a-f]{40}",value):
        raise ReplacementExecutionError(label+" SHA invalid")
    return value

def _safe_path(value: str) -> str:
    if not isinstance(value,str) or not value or value.startswith("/"):
        raise ReplacementExecutionError("candidate path invalid")
    normalized=value.replace("\\","/")
    if ".." in Path(normalized).parts:
        raise ReplacementExecutionError("candidate path escapes project")
    if normalized in PROTECTED_FILES or any(normalized.startswith(x) for x in PROTECTED_PREFIXES):
        raise ReplacementExecutionError("candidate path is protected")
    return normalized

def _validate_candidate(order: dict, candidate: dict) -> list[dict]:
    if not isinstance(order,dict) or not isinstance(candidate,dict):
        raise ReplacementExecutionError("replacement input malformed")
    if candidate.get("status")!="replacement_candidate_validated":
        raise ReplacementExecutionError("replacement candidate is not validated")
    if candidate.get("work_order_id")!=order.get("id"):
        raise ReplacementExecutionError("replacement candidate identity mismatch")
    if candidate.get("current_repo")!=order.get("current_repo"):
        raise ReplacementExecutionError("current repository mismatch")
    if candidate.get("replacement_repo")!=order.get("replacement_repo"):
        raise ReplacementExecutionError("replacement repository mismatch")

    files=candidate.get("files")
    if not isinstance(files,list) or not files or len(files)>MAX_FILES:
        raise ReplacementExecutionError("candidate file set invalid")

    total=0
    normalized=[]
    seen=set()
    for item in files:
        if not isinstance(item,dict) or set(item)!={"path","content"}:
            raise ReplacementExecutionError("candidate file entry malformed")
        path=_safe_path(item["path"])
        content=item["content"]
        if not isinstance(content,str):
            raise ReplacementExecutionError("candidate content must be text")
        size=len(content.encode("utf-8"))
        if size>MAX_FILE_BYTES:
            raise ReplacementExecutionError("candidate file too large")
        total+=size
        if total>MAX_TOTAL_BYTES:
            raise ReplacementExecutionError("candidate bundle too large")
        if path in seen:
            raise ReplacementExecutionError("duplicate candidate path")
        seen.add(path)
        normalized.append({"path":path,"content":content})
    return normalized

def _materialize(root: Path, files: list[dict]) -> None:
    base=root.resolve()
    for item in files:
        target=root/item["path"]
        resolved=target.resolve()
        if not resolved.is_relative_to(base):
            raise ReplacementExecutionError("candidate path escaped worktree")
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(item["content"],encoding="utf-8")

def _hash_files(root: Path, paths: list[str]) -> dict[str,str]:
    out={}
    for path in paths:
        target=root/path
        if target.is_file():
            out[path]=hashlib.sha256(target.read_bytes()).hexdigest()
    return out

def _commit_candidate(root: Path, baseline_sha: str, paths: list[str]) -> str:
    _run(["git","add","--",*paths],cwd=root,check=True)
    env=dict(SAFE_ENV)
    env["GIT_AUTHOR_NAME"]=env["GIT_COMMITTER_NAME"]="ai-dev-server replacement"
    env["GIT_AUTHOR_EMAIL"]=env["GIT_COMMITTER_EMAIL"]="replacement@localhost"
    _run(
        ["git","commit","--no-gpg-sign","-m","Isolated architecture replacement candidate"],
        cwd=root,env=env,check=True,
    )
    sha=_run(["git","rev-parse","HEAD"],cwd=root,check=True).stdout.strip()
    if sha==baseline_sha:
        raise ReplacementExecutionError("candidate did not advance baseline")
    return _sha(sha,"Candidate")

def _docker_command(root: Path, command: list[str], timeout: int=1200):
    if shutil.which("docker") is None:
        raise ReplacementExecutionError("Docker unavailable for replacement isolation")
    if not isinstance(command,list) or not command or not all(isinstance(x,str) and x for x in command):
        raise ReplacementExecutionError("validation command malformed")
    allowed={
        "python3","python","flutter","dart",
    }
    if command[0] not in allowed:
        raise ReplacementExecutionError("validation command not allowlisted")

    docker=[
        "docker","run","--rm",
        "--network","none",
        "--cap-drop","ALL",
        "--security-opt","no-new-privileges",
        "--pids-limit","256",
        "--memory","2048m",
        "--cpus","2",
        "--tmpfs","/tmp:rw,nosuid,size=512m",
        "-e","HOME=/tmp/home",
        "-e","LANG=C.UTF-8",
        "-e","LC_ALL=C.UTF-8",
        "-e","PYTHONDONTWRITEBYTECODE=1",
        "-e","PYTHONUNBUFFERED=1",
        "-v",str(root.resolve())+":/workspace:rw",
        "-w","/workspace",
        IMAGE,
        *command,
    ]
    return _run(docker,timeout=timeout,env=SAFE_ENV)

def _commands(candidate: dict) -> list[list[str]]:
    commands=candidate.get("validation_commands")
    if not isinstance(commands,list) or not commands:
        return [
            ["python3","-m","compileall","-q","studio","tests"],
            ["python3","-m","unittest","discover","-s","tests","-v"],
        ]
    result=[]
    for command in commands[:8]:
        if not isinstance(command,list) or not command:
            raise ReplacementExecutionError("validation command malformed")
        result.append([str(x) for x in command])
    return result

def _validate_tree(root: Path, commands: list[list[str]]) -> dict:
    results=[]
    for command in commands:
        run=_docker_command(root,command)
        results.append({
            "command":command,
            "returncode":run.returncode,
            "passed":run.returncode==0,
            "stdout_sha256":hashlib.sha256((run.stdout or "").encode()).hexdigest(),
            "stderr_sha256":hashlib.sha256((run.stderr or "").encode()).hexdigest(),
        })
    return {
        "passed":all(x["passed"] for x in results),
        "commands":results,
    }

def execute(repo_root: Path, order: dict, candidate: dict, out: Path) -> dict:
    files=_validate_candidate(order,candidate)
    baseline_sha=_sha(candidate.get("baseline_sha"),"Baseline")
    if _run(["git","cat-file","-e",baseline_sha+"^{commit}"],cwd=repo_root).returncode:
        raise ReplacementExecutionError("baseline commit unavailable")

    out.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="replacement-run-") as tmp:
        temp=Path(tmp)
        baseline=temp/"baseline"
        replacement=temp/"replacement"
        _run(["git","worktree","add","--detach",str(baseline),baseline_sha],cwd=repo_root,check=True)
        try:
            _run(["git","worktree","add","--detach",str(replacement),baseline_sha],cwd=repo_root,check=True)
            try:
                paths=[x["path"] for x in files]
                before_hashes=_hash_files(baseline,paths)
                commands=_commands(candidate)
                baseline_validation=_validate_tree(baseline,commands)

                _materialize(replacement,files)
                candidate_sha=_commit_candidate(replacement,baseline_sha,paths)
                candidate_validation=_validate_tree(replacement,commands)
                after_hashes=_hash_files(replacement,paths)

                reversible=(
                    _run(["git","rev-parse","HEAD^"],cwd=replacement).stdout.strip()==baseline_sha
                )
                diff=_run(["git","diff","--stat",baseline_sha,candidate_sha],cwd=replacement)
                changed=_run(["git","diff","--name-only",baseline_sha,candidate_sha],cwd=replacement)

                baseline_ok=baseline_validation["passed"]
                candidate_ok=candidate_validation["passed"]
                all_gates=baseline_ok and candidate_ok and reversible
                verdict="GO_FOR_MANUAL_PROMOTION_REVIEW" if all_gates else "NO_GO"

                evidence={
                    "version":1,
                    "status":"replacement_isolated_benchmark_complete",
                    "work_order_id":order.get("id"),
                    "current_repo":order.get("current_repo"),
                    "replacement_repo":order.get("replacement_repo"),
                    "baseline_sha":baseline_sha,
                    "candidate_sha":candidate_sha,
                    "network":"disabled",
                    "credentials_exposed_to_candidate":False,
                    "default_branch_modified":False,
                    "baseline_validation":baseline_validation,
                    "candidate_validation":candidate_validation,
                    "reversible":reversible,
                    "before_hashes":before_hashes,
                    "after_hashes":after_hashes,
                    "changed_files":[x for x in changed.stdout.splitlines() if x][:128],
                    "diff_stat_sha256":hashlib.sha256((diff.stdout or "").encode()).hexdigest(),
                    "go_no_go":verdict,
                    "policy":{
                        "auto_promote":False,
                        "manual_or_existing_dependency_policy_review_required":True,
                    },
                }
                (out/"architecture-replacement-execution.json").write_text(
                    canonical(evidence)+"\n",encoding="utf-8"
                )
                return evidence
            finally:
                _run(["git","worktree","remove","--force",str(replacement)],cwd=repo_root)
        finally:
            _run(["git","worktree","remove","--force",str(baseline)],cwd=repo_root)

def main(argv=None) -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("work_order")
    parser.add_argument("candidate")
    parser.add_argument("--repo-root",default=".")
    parser.add_argument("--out",default="studio-output")
    args=parser.parse_args(argv)
    out=Path(args.out)
    try:
        order=json.loads(Path(args.work_order).read_text(encoding="utf-8"))
        candidate=json.loads(Path(args.candidate).read_text(encoding="utf-8"))
        evidence=execute(Path(args.repo_root),order,candidate,out)
        print(canonical({"status":evidence["status"],"go_no_go":evidence["go_no_go"]}))
        return 0 if evidence["go_no_go"]=="GO_FOR_MANUAL_PROMOTION_REVIEW" else 1
    except (OSError,ValueError,json.JSONDecodeError,subprocess.SubprocessError,ReplacementExecutionError):
        out.mkdir(parents=True,exist_ok=True)
        (out/"architecture-replacement-execution-error.json").write_text(
            canonical({"status":"replacement_execution_blocked"})+"\n",encoding="utf-8"
        )
        return 1

if __name__=="__main__":
    sys.exit(main())
