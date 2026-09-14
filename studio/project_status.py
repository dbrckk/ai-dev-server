"""Read-only status view for autonomous project state."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from objective_dag import ObjectiveDagError, load as load_objective_dag, summary as objective_dag_summary
from release_proof_manifest import ReleaseProofError, load as load_release_proof
from task_semantic_checkpoint import TaskSemanticCheckpointError, load as load_task_semantic_checkpoint
from user_input_required import UserInputRequiredError, load as load_user_input_state, missing_env as missing_user_input_env


def _read_json(path: Path) -> dict | None:
    try:
        value=json.loads(path.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError):
        return None
    return value if isinstance(value,dict) else None


def inspect(root: Path) -> dict:
    root=Path(root).resolve()
    autonomy=root/".autonomy"
    report=_read_json(root/"generic-report.json") or {}

    dag_summary=None
    dag_error=None
    dag_path=autonomy/"objective-dag.json"
    if dag_path.is_file():
        try:
            dag_summary=objective_dag_summary(load_objective_dag(dag_path))
        except ObjectiveDagError as exc:
            dag_error=str(exc)

    semantic_tasks=0
    semantic_error=None
    semantic_path=autonomy/"task-semantic-checkpoint.json"
    if semantic_path.is_file():
        try:
            semantic=load_task_semantic_checkpoint(semantic_path)
            semantic_tasks=len(semantic.get("tasks",{}))
        except TaskSemanticCheckpointError as exc:
            semantic_error=str(exc)

    release_proof=None
    release_proof_error=None
    release_path=autonomy/"release-proof.json"
    if release_path.is_file():
        try:
            proof=load_release_proof(release_path)
            release_proof={
                "sha256":proof.get("sha256"),
                "release_commit":proof.get("release_commit"),
                "task_count":proof.get("task_count"),
            }
        except ReleaseProofError as exc:
            release_proof_error=str(exc)

    proof_count=0
    proof_dir=autonomy/"proofs"
    if proof_dir.is_dir():
        proof_count=sum(1 for item in proof_dir.glob("*.json") if item.is_file())

    user_input=None
    user_input_error=None
    user_input_path=root/"user-input-required.json"
    if user_input_path.is_file():
        try:
            pending=load_user_input_state(user_input_path)
            user_input={
                "required_env":pending.get("required_env",[]),
                "missing_env":missing_user_input_env(pending),
                "reason":pending.get("reason"),
            }
        except UserInputRequiredError as exc:
            user_input_error=str(exc)

    blockers=[]
    completion=report.get("completion") if isinstance(report.get("completion"),dict) else {}
    for blocker in completion.get("blockers",[]) if isinstance(completion.get("blockers"),list) else []:
        if isinstance(blocker,str) and blocker:
            blockers.append(blocker)
    if dag_summary:
        for item in dag_summary.get("stalled_tasks",[]):
            if isinstance(item,dict):
                blockers.append(
                    "stalled task "
                    + str(item.get("id"))
                    + ": "
                    + str(item.get("last_error") or "retry budget exhausted")
                )
        for item in dag_summary.get("confidence_blockers",[]):
            if isinstance(item,dict):
                blockers.append(
                    "confidence blocker "
                    + str(item.get("dependency"))
                    + " -> "
                    + str(item.get("critical_task"))
                )
    if dag_error:
        blockers.append("objective DAG invalid: "+dag_error)
    if semantic_error:
        blockers.append("semantic checkpoint invalid: "+semantic_error)
    if release_proof_error:
        blockers.append("release proof invalid: "+release_proof_error)
    if user_input_error:
        blockers.append("user input state invalid: "+user_input_error)
    if user_input and user_input.get("missing_env"):
        blockers.append(
            "external input required: "
            + ", ".join(str(item) for item in user_input["missing_env"])
        )

    next_task=dag_summary.get("next_task") if isinstance(dag_summary,dict) else None
    report_status=str(report.get("status") or "").strip()
    dag_complete=bool(dag_summary and dag_summary.get("complete"))

    if release_proof and dag_complete and not blockers:
        status="complete"
    elif user_input and user_input.get("missing_env"):
        status="user_input_required"
    elif blockers:
        status="blocked"
    elif next_task:
        status="working"
    elif report_status:
        status=report_status
    else:
        status="unknown"

    latest_round=None
    rounds=report.get("rounds") if isinstance(report.get("rounds"),list) else []
    if rounds and isinstance(rounds[-1],dict):
        row=rounds[-1]
        latest_round={
            "round":row.get("round"),
            "changed_files":row.get("changed_files",[]),
            "verification":(
                {
                    "status":row.get("verification",{}).get("status"),
                    "passed":row.get("verification",{}).get("passed"),
                }
                if isinstance(row.get("verification"),dict)
                else None
            ),
            "objective_task":row.get("objective_task"),
        }

    return {
        "status":status,
        "path":str(root),
        "objective_dag":dag_summary,
        "next_task":next_task,
        "release_confidence":report.get("release_confidence"),
        "task_confidence":report.get("task_confidence"),
        "latest_round":latest_round,
        "proofs":{
            "task_proof_count":proof_count,
            "release_proof":release_proof,
        },
        "semantic_task_count":semantic_tasks,
        "user_input_required":user_input,
        "blockers":blockers,
    }


def main(argv: list[str] | None = None) -> int:
    parser=argparse.ArgumentParser(description="Read autonomous project status")
    parser.add_argument("path",nargs="?",default=".",help="project output directory")
    parser.add_argument("--compact",action="store_true",help="emit compact JSON")
    args=parser.parse_args(argv)
    status=inspect(Path(args.path))
    if args.compact:
        print(json.dumps(status,sort_keys=True,ensure_ascii=False,separators=(",",":")))
    else:
        print(json.dumps(status,sort_keys=True,ensure_ascii=False,indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
