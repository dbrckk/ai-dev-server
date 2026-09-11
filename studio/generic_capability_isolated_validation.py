"""Isolated validation for synthesized generic capability candidates."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

try:
    from .capability_candidate_validator import validate_candidate
    from .capability_synthesis import validate_candidate_envelope
    from .core import IMAGE
except ImportError:
    from capability_candidate_validator import validate_candidate
    from capability_synthesis import validate_candidate_envelope
    from core import IMAGE


class IsolatedCapabilityValidationError(RuntimeError):
    pass


FORBIDDEN_IMPORTS={"socket","ctypes","subprocess"}
FORBIDDEN_CALLS={"eval","exec","compile","__import__","open","os.system","os.popen"}
PROVIDER_RE=re.compile(r"studio\.capabilities\.([a-z][a-z0-9_]{2,120})")


def _canon(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()


def _seal(value):
    return hashlib.sha256(_canon(value)).hexdigest()


def _call_name(node):
    target=node.func
    if isinstance(target,ast.Name):
        return target.id
    parts=[]
    while isinstance(target,ast.Attribute):
        parts.append(target.attr)
        target=target.value
    if isinstance(target,ast.Name):
        parts.append(target.id)
        return ".".join(reversed(parts))
    return ""


def _static_check(source,label):
    try:
        tree=ast.parse(source,filename=label)
    except SyntaxError:
        raise IsolatedCapabilityValidationError(label+" does not parse") from None
    for node in ast.walk(tree):
        if isinstance(node,ast.Import):
            if any(alias.name.split(".",1)[0] in FORBIDDEN_IMPORTS for alias in node.names):
                raise IsolatedCapabilityValidationError(label+" imports forbidden module")
        elif isinstance(node,ast.ImportFrom):
            if isinstance(node.module,str) and node.module.split(".",1)[0] in FORBIDDEN_IMPORTS:
                raise IsolatedCapabilityValidationError(label+" imports forbidden module")
        elif isinstance(node,ast.Call):
            name=_call_name(node)
            if name in FORBIDDEN_CALLS:
                raise IsolatedCapabilityValidationError(label+" uses forbidden call")
        elif isinstance(node,(ast.Global,ast.Nonlocal)):
            raise IsolatedCapabilityValidationError(label+" uses global mutation")


def _docker(root,args,timeout=180):
    if shutil.which("docker") is None:
        raise IsolatedCapabilityValidationError("docker unavailable")
    cmd=[
        "docker","run","--rm","--network","none","--read-only","--cap-drop","ALL",
        "--security-opt","no-new-privileges","--pids-limit","96","--memory","512m","--cpus","1",
        "--tmpfs","/tmp:rw,noexec,nosuid,size=128m",
        "-e","HOME=/tmp/home","-e","PYTHONDONTWRITEBYTECODE=1","-e","PYTHONUNBUFFERED=1",
        "-v",str(Path(root).resolve())+":/workspace:ro","-w","/workspace",
        IMAGE,"python3",*args,
    ]
    result=subprocess.run(cmd,text=True,capture_output=True,timeout=timeout)
    return result.returncode,(result.stdout or "")+"\n"+(result.stderr or "")


def _test_count(output):
    match=re.search(r"Ran\s+(\d+)\s+tests?",output)
    return int(match.group(1)) if match else 0


def _proof(kind,candidate_sha,passed,**extra):
    value={"kind":kind,"candidate_sha256":candidate_sha,"passed":bool(passed),**extra}
    value["evidence_sha256"]=_seal(value)
    return value


def validate_in_isolation(envelope,repo_root=Path(".")):
    validate_candidate_envelope(envelope)
    candidate=envelope["candidate"]
    provider=candidate.get("provider")
    match=PROVIDER_RE.fullmatch(provider) if isinstance(provider,str) else None
    if match is None:
        raise IsolatedCapabilityValidationError("provider invalid")
    implementation=candidate.get("implementation")
    tests=candidate.get("tests")
    if not isinstance(implementation,str) or not isinstance(tests,str):
        raise IsolatedCapabilityValidationError("candidate sources invalid")
    _static_check(implementation,"implementation")
    _static_check(tests,"tests")

    candidate_sha=envelope["candidate_sha256"]
    with tempfile.TemporaryDirectory(prefix="generic-capability-") as td:
        root=Path(td)
        module=match.group(1)
        (root/"studio/capabilities").mkdir(parents=True)
        (root/"tests").mkdir()
        (root/"studio/__init__.py").write_text("")
        (root/"studio/capabilities/__init__.py").write_text("")
        (root/"tests/__init__.py").write_text("")
        (root/"tests/test_candidate.py").write_text(tests)

        baseline_rc,baseline_output=_docker(root,["-m","unittest","discover","-s","tests","-v"])
        baseline_count=_test_count(baseline_output)

        (root/"studio/capabilities"/(module+".py")).write_text(implementation)
        compile_rc,_=_docker(root,["-m","compileall","-q","studio","tests"])
        candidate_rc,candidate_output=_docker(root,["-m","unittest","discover","-s","tests","-v"])
        candidate_count=_test_count(candidate_output)

    targeted_passed=(compile_rc==0 and candidate_rc==0 and candidate_count>0)
    differential_passed=(baseline_rc!=0 and candidate_rc==0 and candidate_count>0)
    targeted=_proof(
        "targeted_test",candidate_sha,targeted_passed,
        tests_collected=candidate_count,
        compile_passed=compile_rc==0,
    )
    benchmark=_proof(
        "benchmark",candidate_sha,targeted_passed and differential_passed,
        score=candidate_count if candidate_rc==0 else 0,
        baseline_score=baseline_count if baseline_rc==0 else 0,
        differential_improvement=differential_passed,
    )

    repo_root=Path(repo_root)
    if not (repo_root/"studio").is_dir() or not (repo_root/"tests").is_dir():
        raise IsolatedCapabilityValidationError("trusted regression root invalid")
    regression_rc,regression_output=_docker(repo_root,["-m","unittest","discover","-s","tests","-v"],timeout=900)
    regression=_proof(
        "regression",candidate_sha,regression_rc==0,
        tests_collected=_test_count(regression_output),
    )
    validation=validate_candidate(envelope,targeted,benchmark,regression)
    return {
        "status":"isolated_validation_complete",
        "candidate_id":envelope["candidate_id"],
        "candidate_sha256":candidate_sha,
        "targeted_test":targeted,
        "benchmark":benchmark,
        "regression":regression,
        "validation":validation,
        "candidate_materialized_in_trusted_repo":False,
        "network":"disabled",
        "capabilities":"dropped",
    }


def validate_isolated_validation_result(value):
    if not isinstance(value,dict):
        raise IsolatedCapabilityValidationError("validation report invalid")
    required={
        "status","candidate_id","candidate_sha256","targeted_test","benchmark",
        "regression","validation","candidate_materialized_in_trusted_repo",
        "network","capabilities",
    }
    if set(value)!=required or value.get("status")!="isolated_validation_complete":
        raise IsolatedCapabilityValidationError("validation report fields invalid")
    sha=value.get("candidate_sha256")
    if not isinstance(sha,str) or not re.fullmatch(r"[0-9a-f]{64}",sha):
        raise IsolatedCapabilityValidationError("validation candidate digest invalid")
    for key in ("targeted_test","benchmark","regression"):
        proof=value.get(key)
        if not isinstance(proof,dict) or proof.get("candidate_sha256")!=sha:
            raise IsolatedCapabilityValidationError("validation proof mismatch")
        digest=proof.get("evidence_sha256")
        unsigned=dict(proof); unsigned.pop("evidence_sha256",None)
        if not isinstance(digest,str) or digest!=_seal(unsigned):
            raise IsolatedCapabilityValidationError("validation proof integrity failure")
    validation=value.get("validation")
    if not isinstance(validation,dict) or validation.get("candidate_sha256")!=sha:
        raise IsolatedCapabilityValidationError("validation decision mismatch")
    if validation.get("status") not in {"candidate_validated","candidate_rejected"}:
        raise IsolatedCapabilityValidationError("validation decision invalid")
    if value.get("candidate_materialized_in_trusted_repo") is not False:
        raise IsolatedCapabilityValidationError("trusted repository mutation claimed")
    if value.get("network")!="disabled" or value.get("capabilities")!="dropped":
        raise IsolatedCapabilityValidationError("isolation evidence invalid")
    return value
