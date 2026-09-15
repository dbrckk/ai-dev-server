"""CI trust policy v12: v11 plus fail-closed checkout credential handling."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import replacement_ci_policy_v11 as _base
from replacement_ci_policy_v11 import *

CI_TRUST_POLICY_VERSION=12
REQUIRED_ACTION_INPUT_VALUES={"actions/checkout":{"persist-credentials":"false"}}
ACTION_WITH_ALLOWLIST=dict(_base.ACTION_WITH_ALLOWLIST)
ACTION_WITH_ALLOWLIST["actions/checkout"]=frozenset({"persist-credentials"})


def ci_trust_policy_digest() -> str:
    payload={
        "version":CI_TRUST_POLICY_VERSION,
        "base_policy_digest":_base.ci_trust_policy_digest(),
        "action_with_allowlist":{k:sorted(v) for k,v in sorted(ACTION_WITH_ALLOWLIST.items())},
        "required_action_input_values":REQUIRED_ACTION_INPUT_VALUES,
    }
    return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode("utf-8")).hexdigest()


def _checkout_input_violations(text: str) -> list[dict]:
    violations=[]
    current_action=None
    inputs={}
    action_line=None
    in_with=False

    def finish():
        if current_action!="actions/checkout":
            return
        value=inputs.get("persist-credentials")
        if value is None:
            violations.append({"reason":"required_action_input_missing","line":action_line,"action":"actions/checkout","key":"persist-credentials","expected":"false"})
        elif value.strip().strip("'\"").lower()!="false":
            violations.append({"reason":"unapproved_action_input_value","line":action_line,"action":"actions/checkout","key":"persist-credentials","actual":value.strip().strip("'\""),"expected":"false"})

    for lineno,line in enumerate(text.splitlines(),start=1):
        code=_base._yaml_code(line)
        if re.match(r"^      -\s+",code):
            finish()
            current_action=None;inputs={};action_line=None;in_with=False
        uses=re.match(r"^        uses:\s*([^#\s]+)",code) or re.match(r"^      -\s+uses:\s*([^#\s]+)",code)
        if uses:
            value=uses.group(1).strip().strip("'\"")
            current_action=value.rsplit("@",1)[0] if "@" in value else value
            action_line=lineno
            in_with=False
            continue
        if re.match(r"^        with:\s*$",code):
            in_with=True
            continue
        if in_with:
            item=re.match(r"^          ([A-Za-z0-9_-]+):\s*([^#\n]+?)\s*$",code)
            if item:
                inputs[item.group(1)]=item.group(2).strip()
                continue
            if code.strip() and len(code)-len(code.lstrip(" "))<=8:
                in_with=False
    finish()
    return violations


def validate_step_inputs_env_text(text: str) -> dict:
    base=_base.validate_step_inputs_env_text(text)
    violations=[
        row for row in base["violations"]
        if not (
            row.get("reason")=="unapproved_action_input"
            and row.get("action")=="actions/checkout"
            and row.get("key")=="persist-credentials"
        )
    ]
    violations.extend(_checkout_input_violations(text))
    return {
        "valid":not violations,
        "action_with_allowlist":{k:sorted(v) for k,v in ACTION_WITH_ALLOWLIST.items()},
        "required_action_input_values":REQUIRED_ACTION_INPUT_VALUES,
        "run_env_allowlist":dict(RUN_ENV_ALLOWLIST),
        "violations":violations,
    }


def workflow_semantic_manifest_text(text: str) -> dict:
    validation=validate_workflow_text(text,include_semantic=False)
    if not validation["valid"]:
        return {"valid":False,"manifest":None,"digest":None,"violations":["workflow_not_trusted"]}
    manifest={
        "workflow_name":validation["workflow_name"],
        "jobs":validation["exact_job_steps"]["jobs"],
        "permissions":validation["permissions"]["workflow_permissions"],
        "runtime":validation["runtime"]["jobs"],
        "triggers":validation["trigger_concurrency"]["triggers"],
        "push_branches":validation["trigger_concurrency"]["push_branches"],
        "concurrency":validation["trigger_concurrency"]["concurrency"],
        "actions":validation["action_pinning"]["uses"],
        "step_inputs_env":{
            "action_with_allowlist":validation["step_inputs_env"]["action_with_allowlist"],
            "required_action_input_values":validation["step_inputs_env"]["required_action_input_values"],
            "run_env_allowlist":validation["step_inputs_env"]["run_env_allowlist"],
        },
    }
    encoded=json.dumps(manifest,sort_keys=True,separators=(",",":")).encode("utf-8")
    return {"valid":True,"manifest":manifest,"digest":hashlib.sha256(encoded).hexdigest(),"violations":[]}


def validate_workflow_text(text: str, *, include_semantic: bool=True) -> dict:
    yaml_surface=validate_yaml_surface_text(text)
    schema=validate_workflow_schema_text(text)
    step_env=validate_step_inputs_env_text(text)
    trigger=validate_trigger_concurrency_text(text)
    exact=validate_exact_job_steps_text(text)
    jobs=workflow_job_ids_text(text)
    missing=sorted(REQUIRED_GITHUB_CHECKS-jobs)
    match=re.search(r"(?m)^name:\s*([^#\n]+?)\s*$",text)
    workflow_name=match.group(1).strip().strip("'\"") if match else None
    actions=validate_action_pinning_text(text)
    permissions=validate_workflow_permissions_text(text)
    runtime=validate_workflow_runtime_text(text)
    expressions=validate_workflow_expression_policy_text(text)
    commands=validate_workflow_run_commands_text(text)
    valid=(
        yaml_surface["valid"] and schema["valid"] and step_env["valid"]
        and trigger["valid"] and exact["valid"] and not missing
        and workflow_name==REQUIRED_WORKFLOW_NAME and actions["valid"]
        and permissions["valid"] and runtime["valid"]
        and expressions["valid"] and commands["valid"]
    )
    result={
        "valid":valid,"required_checks":sorted(REQUIRED_GITHUB_CHECKS),
        "workflow_jobs":sorted(jobs),"missing_checks":missing,
        "workflow_name":workflow_name,"expected_workflow_name":REQUIRED_WORKFLOW_NAME,
        "yaml_surface":yaml_surface,"schema":schema,"step_inputs_env":step_env,
        "trigger_concurrency":trigger,"exact_job_steps":exact,
        "action_pinning":actions,"permissions":permissions,"runtime":runtime,
        "expressions":expressions,"run_commands":commands,
        "ci_trust_policy_version":CI_TRUST_POLICY_VERSION,
        "ci_trust_policy_digest":ci_trust_policy_digest(),
    }
    if include_semantic:
        semantic=workflow_semantic_manifest_text(text) if valid else {"manifest":None,"digest":None}
        result["semantic_manifest"]=semantic["manifest"]
        result["semantic_digest"]=semantic["digest"]
    return result


def validate_workflow(path: Path) -> dict:
    return validate_workflow_text(path.read_text(encoding="utf-8"))
