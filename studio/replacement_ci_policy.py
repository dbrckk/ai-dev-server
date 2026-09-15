"""Single source of truth for replacement GitHub CI trust requirements."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlparse

REQUIRED_GITHUB_CHECKS=frozenset({"validate","python-tests"})
TRUSTED_CHECK_APP="github-actions"
REQUIRED_WORKFLOW_NAME="CI"
REQUIRED_WORKFLOW_PATH=".github/workflows/ci.yml"
CI_TRUST_POLICY_VERSION=9
REQUIRED_WORKFLOW_PERMISSIONS={"contents":"read"}
REQUIRED_JOB_RUNNER="ubuntu-latest"
REQUIRED_JOB_TIMEOUTS={"validate":5,"python-tests":20}
FORBIDDEN_WORKFLOW_TRIGGERS=frozenset({"pull_request_target","workflow_run"})
FORBIDDEN_JOB_KEYS=frozenset({"strategy","needs","if","continue-on-error","environment","container","services"})
FORBIDDEN_STEP_KEYS=frozenset({"if","continue-on-error","timeout-minutes"})
FORBIDDEN_EXPRESSION_CONTEXTS=frozenset({"secrets","github.event","github.token","github.actor","github.triggering_actor","vars","inputs","matrix","strategy","needs"})
FORBIDDEN_RUN_TOKENS=frozenset({"curl","wget","sudo","docker","podman","GITHUB_ENV","GITHUB_PATH","GITHUB_OUTPUT","GITHUB_STATE","GITHUB_STEP_SUMMARY"})
FORBIDDEN_RUN_PREFIXES=("pip install","pip3 install","npm install","npm ci","npx ","yarn ","pnpm ","apt install","apt-get install","git clone","git fetch","git pull","gh ")
REQUIRED_RUN_SHELL="bash"
FORBIDDEN_YAML_FEATURES=frozenset({"anchor","alias","tag","merge_key","tab_indentation","duplicate_key"})
ALLOWED_ROOT_KEYS=frozenset({"name","on","permissions","concurrency","jobs"})
ALLOWED_JOB_KEYS=frozenset({"name","runs-on","timeout-minutes","steps"})
ALLOWED_STEP_KEYS=frozenset({"name","uses","with","run","shell","env"})
ACTION_WITH_ALLOWLIST={
    "actions/checkout":frozenset(),
    "actions/setup-python":frozenset({"python-version"}),
}
RUN_ENV_ALLOWLIST={"PYTHONPATH":"studio"}
REQUIRED_WORKFLOW_TRIGGERS={"push":{"branches":("main",)},"pull_request":{}}
REQUIRED_CONCURRENCY_GROUP="ci-${{ github.workflow }}-${{ github.ref }}"
REQUIRED_CONCURRENCY_CANCEL=True

# Explicit allowlist: third-party actions and mutable refs are fail-closed.
TRUSTED_ACTION_REVISIONS={
    "actions/checkout":"11d5960a326750d5838078e36cf38b85af677262",
    "actions/setup-python":"a26af69be951a213d495a4c3e4e4022e16d87065",
}

def ci_trust_policy_digest() -> str:
    payload={
        "version":CI_TRUST_POLICY_VERSION,
        "required_checks":sorted(REQUIRED_GITHUB_CHECKS),
        "trusted_check_app":TRUSTED_CHECK_APP,
        "workflow_name":REQUIRED_WORKFLOW_NAME,
        "workflow_path":REQUIRED_WORKFLOW_PATH,
        "trusted_action_revisions":dict(sorted(TRUSTED_ACTION_REVISIONS.items())),
        "required_workflow_permissions":dict(sorted(REQUIRED_WORKFLOW_PERMISSIONS.items())),
        "required_job_runner":REQUIRED_JOB_RUNNER,
        "required_job_timeouts":dict(sorted(REQUIRED_JOB_TIMEOUTS.items())),
        "forbidden_workflow_triggers":sorted(FORBIDDEN_WORKFLOW_TRIGGERS),
        "forbidden_job_keys":sorted(FORBIDDEN_JOB_KEYS),
        "forbidden_step_keys":sorted(FORBIDDEN_STEP_KEYS),
        "forbidden_expression_contexts":sorted(FORBIDDEN_EXPRESSION_CONTEXTS),
        "forbidden_run_tokens":sorted(FORBIDDEN_RUN_TOKENS),
        "forbidden_run_prefixes":list(FORBIDDEN_RUN_PREFIXES),
        "required_run_shell":REQUIRED_RUN_SHELL,
        "forbidden_yaml_features":sorted(FORBIDDEN_YAML_FEATURES),
        "allowed_root_keys":sorted(ALLOWED_ROOT_KEYS),
        "allowed_job_keys":sorted(ALLOWED_JOB_KEYS),
        "allowed_step_keys":sorted(ALLOWED_STEP_KEYS),
        "action_with_allowlist":{k:sorted(v) for k,v in sorted(ACTION_WITH_ALLOWLIST.items())},
        "run_env_allowlist":dict(sorted(RUN_ENV_ALLOWLIST.items())),
        "required_workflow_triggers":{"push":{"branches":["main"]},"pull_request":{}},
        "required_concurrency_group":REQUIRED_CONCURRENCY_GROUP,
        "required_concurrency_cancel":REQUIRED_CONCURRENCY_CANCEL,
    }
    return hashlib.sha256(
        json.dumps(payload,sort_keys=True,separators=(",",":")).encode("utf-8")
    ).hexdigest()

def validate_yaml_surface_text(text: str) -> dict:
    violations=[]
    seen_by_indent={}
    for lineno,line in enumerate(text.splitlines(),start=1):
        if "\t" in line[:len(line)-len(line.lstrip())]:
            violations.append({"reason":"tab_indentation","line":lineno})
        code=line.split("#",1)[0]
        if re.search(r"(^|[\s:\[,])&[A-Za-z0-9_-]+",code):
            violations.append({"reason":"anchor","line":lineno})
        if re.search(r"(^|[\s:\[,])\*[A-Za-z0-9_-]+",code):
            violations.append({"reason":"alias","line":lineno})
        if re.search(r"(^|\s)![A-Za-z0-9_!/-]+",code):
            violations.append({"reason":"tag","line":lineno})
        if re.match(r"^\s*<<\s*:",code):
            violations.append({"reason":"merge_key","line":lineno})
        match=re.match(r"^(\s*)([A-Za-z0-9_-]+):(?:\s|$)",code)
        if match:
            indent=len(match.group(1))
            key=match.group(2)
            for depth in list(seen_by_indent):
                if depth>indent:
                    seen_by_indent.pop(depth,None)
            bucket=seen_by_indent.setdefault(indent,set())
            if key in bucket:
                violations.append({"reason":"duplicate_key","line":lineno,"key":key,"indent":indent})
            else:
                bucket.add(key)
    return {"valid":not violations,"violations":violations}

def validate_workflow_schema_text(text: str) -> dict:
    violations=[]
    current_job=None
    in_jobs=False
    in_steps=False
    for lineno,line in enumerate(text.splitlines(),start=1):
        code=line.split("#",1)[0].rstrip()
        if not code.strip():
            continue
        root=re.match(r"^([A-Za-z0-9_-]+):",code)
        if root:
            key=root.group(1)
            in_jobs=(key=="jobs")
            current_job=None
            in_steps=False
            if key not in ALLOWED_ROOT_KEYS:
                violations.append({"reason":"unknown_root_key","line":lineno,"key":key})
            continue
        if not in_jobs:
            continue
        job=re.match(r"^  ([A-Za-z0-9_-]+):\s*$",code)
        if job:
            current_job=job.group(1)
            in_steps=False
            continue
        if current_job is None:
            continue
        job_key=re.match(r"^    ([A-Za-z0-9_-]+):",code)
        if job_key:
            key=job_key.group(1)
            in_steps=(key=="steps")
            if key not in ALLOWED_JOB_KEYS:
                violations.append({"reason":"unknown_job_key","line":lineno,"job":current_job,"key":key})
            continue
        if in_steps:
            step_key=re.match(r"^      -\s+([A-Za-z0-9_-]+):",code)
            if step_key and step_key.group(1) not in ALLOWED_STEP_KEYS:
                violations.append({"reason":"unknown_step_key","line":lineno,"job":current_job,"key":step_key.group(1)})
            nested_step_key=re.match(r"^        ([A-Za-z0-9_-]+):",code)
            if nested_step_key and nested_step_key.group(1) not in ALLOWED_STEP_KEYS:
                violations.append({"reason":"unknown_step_key","line":lineno,"job":current_job,"key":nested_step_key.group(1)})
    return {"valid":not violations,"allowed_root_keys":sorted(ALLOWED_ROOT_KEYS),"allowed_job_keys":sorted(ALLOWED_JOB_KEYS),"allowed_step_keys":sorted(ALLOWED_STEP_KEYS),"violations":violations}

def validate_trigger_concurrency_text(text: str) -> dict:
    violations=[]
    lines=text.splitlines()
    triggers=set()
    push_branches=[]
    in_on=False
    in_push=False
    concurrency={}
    in_concurrency=False
    for lineno,line in enumerate(lines,start=1):
        code=line.split("#",1)[0].rstrip()
        if code=="on:":
            in_on=True; in_push=False; in_concurrency=False; continue
        if code=="concurrency:":
            in_concurrency=True; in_on=False; in_push=False; continue
        if code and not code.startswith(" "):
            in_on=False; in_push=False; in_concurrency=False
        if in_on:
            m=re.match(r"^  ([A-Za-z0-9_-]+):\s*(.*)$",code)
            if m:
                trigger=m.group(1); triggers.add(trigger); in_push=(trigger=="push"); continue
            if in_push:
                b=re.match(r"^    branches:\s*\[\s*['\"]?([^'\"\], ]+)['\"]?\s*\]\s*$",code)
                if b: push_branches=[b.group(1)]
        if in_concurrency:
            m=re.match(r"^  (group|cancel-in-progress):\s*(.+?)\s*$",code)
            if m: concurrency[m.group(1)]=m.group(2).strip().strip("'\\"")
    expected_triggers={"push","pull_request"}
    if triggers!=expected_triggers:
        violations.append({"reason":"workflow_triggers_not_exact","expected":sorted(expected_triggers),"actual":sorted(triggers)})
    if push_branches!=["main"]:
        violations.append({"reason":"push_branches_not_exact","expected":["main"],"actual":push_branches})
    if concurrency.get("group")!=REQUIRED_CONCURRENCY_GROUP:
        violations.append({"reason":"concurrency_group_not_exact","expected":REQUIRED_CONCURRENCY_GROUP,"actual":concurrency.get("group")})
    if concurrency.get("cancel-in-progress")!="true":
        violations.append({"reason":"concurrency_cancel_not_true","actual":concurrency.get("cancel-in-progress")})
    return {"valid":not violations,"triggers":sorted(triggers),"push_branches":push_branches,"concurrency":concurrency,"violations":violations}

def validate_step_inputs_env_text(text: str) -> dict:
    violations=[]
    lines=text.splitlines()
    current_action=None
    current_run=False
    mode=None
    mode_indent=None
    for lineno,line in enumerate(lines,start=1):
        code=line.split("#",1)[0].rstrip()
        step=re.match(r"^      -\s+(?:name:\s*.*)?$",code)
        if step:
            current_action=None
            current_run=False
            mode=None
        uses=re.match(r"^        uses:\s*([^#\s]+)",code)
        if not uses:
            uses=re.match(r"^      -\s+uses:\s*([^#\s]+)",code)
        if uses:
            value=uses.group(1).strip().strip("'\\\"")
            current_action=value.rsplit("@",1)[0] if "@" in value else value
            current_run=False
            mode=None
            continue
        if re.match(r"^        run:\s*",code) or re.match(r"^      -\s+run:\s*",code):
            current_run=True
            current_action=None
            mode=None
        block=re.match(r"^        (with|env):\s*$",code)
        if block:
            mode=block.group(1)
            mode_indent=8
            if mode=="with" and current_action is None:
                violations.append({"reason":"with_without_action","line":lineno})
            if mode=="env" and not current_run:
                violations.append({"reason":"env_on_non_run_step","line":lineno})
            continue
        if mode:
            item=re.match(r"^          ([A-Za-z0-9_-]+):\s*([^#\n]+?)\s*$",code)
            if item:
                key=item.group(1)
                value=item.group(2).strip().strip("'\\\"")
                if mode=="with":
                    allowed=ACTION_WITH_ALLOWLIST.get(current_action,frozenset())
                    if key not in allowed:
                        violations.append({"reason":"unapproved_action_input","line":lineno,"action":current_action,"key":key})
                    elif current_action=="actions/setup-python" and key=="python-version" and value!="3.12":
                        violations.append({"reason":"unapproved_action_input_value","line":lineno,"action":current_action,"key":key,"actual":value,"expected":"3.12"})
                else:
                    expected=RUN_ENV_ALLOWLIST.get(key)
                    if expected is None:
                        violations.append({"reason":"unapproved_run_env","line":lineno,"key":key})
                    elif value!=expected:
                        violations.append({"reason":"unapproved_run_env_value","line":lineno,"key":key,"actual":value,"expected":expected})
                continue
            if code.strip() and len(code)-len(code.lstrip(" "))<=mode_indent:
                mode=None
    return {"valid":not violations,"action_with_allowlist":{k:sorted(v) for k,v in ACTION_WITH_ALLOWLIST.items()},"run_env_allowlist":dict(RUN_ENV_ALLOWLIST),"violations":violations}

def _scalar_yaml_value(value: str):
    value=value.split("#",1)[0].strip().strip("'\"").lower()
    if value in {"read","write","none"}:
        return value
    if value=="{}":
        return {}
    return value

def validate_workflow_permissions_text(text: str) -> dict:
    lines=text.splitlines()
    top_permissions=None
    job_permissions=[]
    i=0
    while i<len(lines):
        line=lines[i]
        match=re.match(r"^(\s*)permissions:\s*(.*?)\s*$",line)
        if not match:
            i+=1
            continue
        indent=len(match.group(1))
        tail=match.group(2)
        block={}
        if tail:
            parsed=_scalar_yaml_value(tail)
            block=parsed
            i+=1
        else:
            i+=1
            while i<len(lines):
                child=lines[i]
                if not child.strip() or child.lstrip().startswith("#"):
                    i+=1
                    continue
                child_indent=len(child)-len(child.lstrip(" "))
                if child_indent<=indent:
                    break
                item=re.match(r"^\s+([A-Za-z0-9_-]+):\s*([^#\n]+?)\s*(?:#.*)?$",child)
                if item:
                    block[item.group(1)]=_scalar_yaml_value(item.group(2))
                i+=1
        if indent==0:
            top_permissions=block
        else:
            job_permissions.append({"indent":indent,"permissions":block})
    violations=[]
    if top_permissions!=REQUIRED_WORKFLOW_PERMISSIONS:
        violations.append({
            "scope":"workflow",
            "reason":"workflow_permissions_not_exact",
            "expected":dict(REQUIRED_WORKFLOW_PERMISSIONS),
            "actual":top_permissions,
        })
    for row in job_permissions:
        violations.append({
            "scope":"job",
            "reason":"job_permissions_override_forbidden",
            "actual":row["permissions"],
        })
    return {
        "valid":not violations,
        "required_permissions":dict(REQUIRED_WORKFLOW_PERMISSIONS),
        "workflow_permissions":top_permissions,
        "job_permission_overrides":job_permissions,
        "violations":violations,
    }

def validate_workflow_runtime_text(text: str) -> dict:
    violations=[]
    forbidden_triggers=sorted(
        trigger for trigger in FORBIDDEN_WORKFLOW_TRIGGERS
        if re.search(r"(?m)^\s{0,2}"+re.escape(trigger)+r"\s*:",text)
    )
    for trigger in forbidden_triggers:
        violations.append({"reason":"forbidden_workflow_trigger","trigger":trigger})
    if re.search(r"(?m)^\s*(container|services)\s*:",text):
        violations.append({"reason":"container_or_services_forbidden"})
    if re.search(r"(?m)^\s*environment\s*:",text):
        violations.append({"reason":"deployment_environment_forbidden"})
    if re.search(r"(?m)^\s*secrets\s*:",text):
        violations.append({"reason":"explicit_secrets_mapping_forbidden"})
    if re.search(r"\$\{\{\s*secrets\.",text):
        violations.append({"reason":"secret_expression_forbidden"})
    if re.search(r"(?m)^\s*runs-on:\s*\$\{\{",text):
        violations.append({"reason":"dynamic_runner_forbidden"})

    jobs={}
    lines=text.splitlines()
    in_jobs=False
    current=None
    for line in lines:
        if line=="jobs:":
            in_jobs=True
            current=None
            continue
        if in_jobs and line and not line.startswith(" "):
            break
        if not in_jobs:
            continue
        job_match=re.match(r"^  ([A-Za-z0-9_-]+):\s*$",line)
        if job_match:
            current=job_match.group(1)
            jobs[current]={"runs_on":None,"timeout_minutes":None}
            continue
        if current is None:
            continue
        runner=re.match(r"^    runs-on:\s*([^#\n]+?)\s*(?:#.*)?$",line)
        if runner:
            jobs[current]["runs_on"]=runner.group(1).strip().strip("'\"")
        timeout=re.match(r"^    timeout-minutes:\s*(\d+)\s*(?:#.*)?$",line)
        if timeout:
            jobs[current]["timeout_minutes"]=int(timeout.group(1))

    for job in sorted(REQUIRED_GITHUB_CHECKS):
        row=jobs.get(job)
        if row is None:
            continue
        if row["runs_on"]!=REQUIRED_JOB_RUNNER:
            violations.append({
                "reason":"untrusted_job_runner","job":job,
                "expected":REQUIRED_JOB_RUNNER,"actual":row["runs_on"],
            })
        expected_timeout=REQUIRED_JOB_TIMEOUTS[job]
        if row["timeout_minutes"]!=expected_timeout:
            violations.append({
                "reason":"job_timeout_not_exact","job":job,
                "expected":expected_timeout,"actual":row["timeout_minutes"],
            })
    return {
        "valid":not violations,
        "required_runner":REQUIRED_JOB_RUNNER,
        "required_timeouts":dict(REQUIRED_JOB_TIMEOUTS),
        "jobs":jobs,
        "forbidden_triggers":forbidden_triggers,
        "violations":violations,
    }

def validate_workflow_expression_policy_text(text: str) -> dict:
    violations=[]
    expressions=re.findall(r"\$\{\{(.*?)\}\}",text,flags=re.DOTALL)
    for expression in expressions:
        normalized=re.sub(r"\s+","",expression).lower()
        for context in sorted(FORBIDDEN_EXPRESSION_CONTEXTS):
            if context.lower() in normalized:
                violations.append({
                    "reason":"forbidden_expression_context",
                    "context":context,
                })
    lines=text.splitlines()
    in_jobs=False
    current_job=None
    in_steps=False
    step_indent=None
    for line in lines:
        if line=="jobs:":
            in_jobs=True
            current_job=None
            in_steps=False
            continue
        if in_jobs and line and not line.startswith(" "):
            break
        if not in_jobs:
            continue
        job_match=re.match(r"^  ([A-Za-z0-9_-]+):\s*$",line)
        if job_match:
            current_job=job_match.group(1)
            in_steps=False
            step_indent=None
            continue
        if current_job is None:
            continue
        key_match=re.match(r"^    ([A-Za-z0-9_-]+):",line)
        if key_match and key_match.group(1) in FORBIDDEN_JOB_KEYS:
            violations.append({
                "reason":"forbidden_job_key",
                "job":current_job,
                "key":key_match.group(1),
            })
        if re.match(r"^    steps:\s*$",line):
            in_steps=True
            step_indent=4
            continue
        if in_steps:
            step_key=re.match(r"^      (?:-\s+)?([A-Za-z0-9_-]+):",line)
            if step_key and step_key.group(1) in FORBIDDEN_STEP_KEYS:
                violations.append({
                    "reason":"forbidden_step_key",
                    "job":current_job,
                    "key":step_key.group(1),
                })
    return {
        "valid":not violations,
        "expression_count":len(expressions),
        "forbidden_expression_contexts":sorted(FORBIDDEN_EXPRESSION_CONTEXTS),
        "forbidden_job_keys":sorted(FORBIDDEN_JOB_KEYS),
        "forbidden_step_keys":sorted(FORBIDDEN_STEP_KEYS),
        "violations":violations,
    }

def validate_workflow_run_commands_text(text: str) -> dict:
    violations=[]
    run_commands=[]
    for lineno,line in enumerate(text.splitlines(),start=1):
        match=re.match(r"^\s*run:\s*(.+?)\s*$",line)
        if match:
            command=match.group(1).strip().strip("'\\\"")
            run_commands.append({"line":lineno,"command":command})
            lowered=command.lower()
            if "${{" in command:
                violations.append({"reason":"expression_in_run_command_forbidden","line":lineno})
            for token in sorted(FORBIDDEN_RUN_TOKENS):
                if token.lower() in lowered:
                    violations.append({"reason":"forbidden_run_token","line":lineno,"token":token})
            for prefix in FORBIDDEN_RUN_PREFIXES:
                if prefix.lower() in lowered:
                    violations.append({"reason":"forbidden_run_prefix","line":lineno,"prefix":prefix})
        shell=re.match(r"^\s*shell:\s*([^#\\n]+?)\s*(?:#.*)?$",line)
        if shell:
            value=shell.group(1).strip().strip("'\\\"")
            if value!=REQUIRED_RUN_SHELL:
                violations.append({"reason":"untrusted_shell","line":lineno,"actual":value})
    for marker in ("GITHUB_ENV","GITHUB_PATH","GITHUB_OUTPUT","GITHUB_STATE","GITHUB_STEP_SUMMARY"):
        if marker in text:
            violations.append({"reason":"github_command_file_reference_forbidden","marker":marker})
    return {"valid":not violations,"required_shell":REQUIRED_RUN_SHELL,"run_commands":run_commands,"violations":violations}

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
    yaml_surface=validate_yaml_surface_text(text)
    schema_policy=validate_workflow_schema_text(text)
    input_env_policy=validate_step_inputs_env_text(text)
    trigger_concurrency_policy=validate_trigger_concurrency_text(text)
    jobs=workflow_job_ids_text(text)
    missing=sorted(REQUIRED_GITHUB_CHECKS-jobs)
    name_match=re.search(r"(?m)^name:\s*([^#\n]+?)\s*$",text)
    workflow_name=name_match.group(1).strip().strip("'\"") if name_match else None
    action_policy=validate_action_pinning_text(text)
    permission_policy=validate_workflow_permissions_text(text)
    runtime_policy=validate_workflow_runtime_text(text)
    expression_policy=validate_workflow_expression_policy_text(text)
    run_policy=validate_workflow_run_commands_text(text)
    return {
        "valid":(
            yaml_surface["valid"]
            and schema_policy["valid"]
            and input_env_policy["valid"]
            and trigger_concurrency_policy["valid"]
            and not missing
            and workflow_name==REQUIRED_WORKFLOW_NAME
            and action_policy["valid"]
            and permission_policy["valid"]
            and runtime_policy["valid"]
            and expression_policy["valid"]
            and run_policy["valid"]
        ),
        "required_checks":sorted(REQUIRED_GITHUB_CHECKS),
        "workflow_jobs":sorted(jobs),
        "missing_checks":missing,
        "workflow_name":workflow_name,
        "expected_workflow_name":REQUIRED_WORKFLOW_NAME,
        "action_pinning":action_policy,
        "permissions":permission_policy,
        "runtime":runtime_policy,
        "expressions":expression_policy,
        "run_commands":run_policy,
        "ci_trust_policy_version":CI_TRUST_POLICY_VERSION,
        "ci_trust_policy_digest":ci_trust_policy_digest(),
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
