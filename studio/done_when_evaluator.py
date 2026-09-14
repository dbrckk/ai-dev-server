"""Deterministic evaluation for structured done_when criteria."""
from __future__ import annotations

import ast
import json
import re
from pathlib import Path

from generic_sandbox import run as run_command

_PREFIXES=("file:","symbol:","test:","build:","json:")


def classify(criterion: str) -> dict:
    text=str(criterion or "").strip()
    for prefix in _PREFIXES:
        if text.lower().startswith(prefix):
            return {"kind":prefix[:-1],"spec":text[len(prefix):].strip(),"raw":text}
    return {"kind":"review","spec":text,"raw":text}


def _safe_path(root: Path, rel: str) -> Path | None:
    root=root.resolve()
    target=(root/rel).resolve()
    try:
        target.relative_to(root)
    except ValueError:
        return None
    if target.is_symlink():
        return None
    return target


def _json_lookup(value, path: str):
    current=value
    if path=="":
        return current, True
    for part in path.split("."):
        if isinstance(current,dict) and part in current:
            current=current[part]
            continue
        if isinstance(current,list) and part.isdigit():
            index=int(part)
            if 0 <= index < len(current):
                current=current[index]
                continue
        return None, False
    return current, True


def _symbol_exists(path: Path, symbol: str) -> bool:
    try:
        text=path.read_text(encoding="utf-8")
    except (OSError,UnicodeError):
        return False
    if path.suffix==".py":
        try:
            tree=ast.parse(text)
        except SyntaxError:
            return False
        for node in ast.walk(tree):
            if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)) and node.name==symbol:
                return True
            if isinstance(node,(ast.Assign,ast.AnnAssign)):
                targets=node.targets if isinstance(node,ast.Assign) else [node.target]
                for target in targets:
                    if isinstance(target,ast.Name) and target.id==symbol:
                        return True
        return False
    pattern=re.compile(r"\b"+re.escape(symbol)+r"\b")
    return bool(pattern.search(text))


def evaluate_static(root: Path, criterion: str) -> dict | None:
    item=classify(criterion)
    kind=item["kind"]
    spec=item["spec"]
    if kind=="review":
        return None
    if kind=="file":
        target=_safe_path(root,spec)
        passed=bool(target and target.is_file())
        return {
            "criterion":item["raw"],"kind":"file","passed":passed,
            "evidence_refs":[spec] if passed else [],
            "evidence":f"file exists: {spec}" if passed else f"file missing: {spec}",
        }
    if kind=="symbol":
        if "#" not in spec:
            return {"criterion":item["raw"],"kind":"symbol","passed":False,"evidence_refs":[],"evidence":"symbol spec must be path#symbol"}
        rel,symbol=spec.split("#",1)
        rel=rel.strip(); symbol=symbol.strip()
        target=_safe_path(root,rel)
        passed=bool(target and target.is_file() and symbol and _symbol_exists(target,symbol))
        return {
            "criterion":item["raw"],"kind":"symbol","passed":passed,
            "evidence_refs":[rel] if passed else [],
            "evidence":f"symbol {symbol} found in {rel}" if passed else f"symbol {symbol} not found in {rel}",
        }
    if kind=="json":
        if "#" not in spec or "=" not in spec:
            return {
                "criterion":item["raw"],"kind":"json","passed":False,
                "evidence_refs":[],"evidence":"json spec must be path#dot.path=<json literal>",
            }
        rel,expectation=spec.split("#",1)
        key_path,raw_expected=expectation.split("=",1)
        rel=rel.strip(); key_path=key_path.strip(); raw_expected=raw_expected.strip()
        target=_safe_path(root,rel)
        try:
            expected=json.loads(raw_expected)
        except json.JSONDecodeError:
            return {
                "criterion":item["raw"],"kind":"json","passed":False,
                "evidence_refs":[],"evidence":"json expected value is not valid JSON",
            }
        try:
            document=json.loads(target.read_text(encoding="utf-8")) if target and target.is_file() else None
        except (OSError,UnicodeError,json.JSONDecodeError):
            document=None
        actual,found=_json_lookup(document,key_path) if document is not None else (None,False)
        passed=bool(found and actual==expected)
        return {
            "criterion":item["raw"],"kind":"json","passed":passed,
            "evidence_refs":[rel] if passed else [],
            "evidence":(
                f"json value matched at {rel}#{key_path}"
                if passed else
                f"json value mismatch at {rel}#{key_path}"
            ),
            "actual":actual if found else None,
            "expected":expected,
        }
    return None


def _known_test_command(root: Path, spec: str) -> list[str] | None:
    path=spec.strip()
    if not path:
        return None
    if path.endswith(".py") or "::" in path:
        if (root/".studio-venv/bin/pytest").is_file():
            return [str(root/".studio-venv/bin/pytest"),"-q",path]
        if (root/"uv.lock").is_file():
            return ["uv","run","pytest","-q",path]
        return ["pytest","-q",path]
    return None


def _build_command(root: Path, spec: str) -> list[str] | None:
    kind=spec.strip().lower()
    if kind not in {"default","project","build"}:
        return None
    package=root/"package.json"
    if package.is_file():
        try:
            data=json.loads(package.read_text(encoding="utf-8"))
        except (OSError,json.JSONDecodeError):
            data={}
        scripts=data.get("scripts",{}) if isinstance(data,dict) else {}
        if isinstance(scripts,dict) and "build" in scripts:
            return ["npm","run","build"]
    if (root/"Cargo.toml").is_file():
        return ["cargo","build","--all-targets"]
    if (root/"go.mod").is_file():
        return ["go","build","./..."]
    if (root/"gradlew").is_file():
        return ["bash","./gradlew","build","--no-daemon"]
    return None


def evaluate_command(root: Path, criterion: str, *, timeout: int=120) -> dict | None:
    item=classify(criterion)
    if item["kind"]=="test":
        command=_known_test_command(root,item["spec"])
        ref=item["spec"].split("::",1)[0].strip()
    elif item["kind"]=="build":
        command=_build_command(root,item["spec"])
        ref=None
    else:
        return None
    if command is None:
        return {
            "criterion":item["raw"],"kind":item["kind"],"passed":False,
            "evidence_refs":[],"evidence":"criterion is structured but unsupported by deterministic evaluator",
            "command":None,
        }
    result=run_command(command,root,timeout=max(30,min(300,int(timeout))),network=False)
    return {
        "criterion":item["raw"],"kind":item["kind"],"passed":result.get("passed") is True,
        "evidence_refs":[ref] if ref and result.get("passed") is True else [],
        "evidence":"deterministic command passed" if result.get("passed") is True else "deterministic command failed",
        "command":command,
        "result":result,
    }


def _reuse_verification(criterion: str, verification: dict | None) -> dict | None:
    if not isinstance(verification, dict) or verification.get("passed") is not True:
        return None
    item=classify(criterion)
    if item["kind"]=="test":
        targeted=verification.get("targeted_precheck")
        target_ref=item["spec"].split("::",1)[0].strip()
        if isinstance(targeted,dict) and targeted.get("passed") is True:
            impacted=targeted.get("impacted_tests",[])
            if isinstance(impacted,list) and target_ref in impacted:
                return {
                    "criterion":item["raw"],
                    "kind":"test",
                    "passed":True,
                    "evidence_refs":[target_ref],
                    "evidence":"reused trusted targeted precheck",
                    "source":"verification_reuse",
                    "command":targeted.get("command"),
                }
    if item["kind"]=="build":
        commands=verification.get("commands",[])
        results=verification.get("results",[])
        if isinstance(commands,list) and isinstance(results,list):
            for command,result in zip(commands,results):
                if not isinstance(command,list) or not isinstance(result,dict) or result.get("passed") is not True:
                    continue
                normalized=[str(x) for x in command]
                is_build=(
                    normalized[:3]==["npm","run","build"]
                    or normalized[:2]==["cargo","build"]
                    or normalized[:2]==["go","build"]
                    or ("gradlew" in " ".join(normalized) and "build" in normalized)
                    or ("cmake" in normalized[:1] and "--build" in normalized)
                )
                if is_build:
                    return {
                        "criterion":item["raw"],
                        "kind":"build",
                        "passed":True,
                        "evidence_refs":[],
                        "evidence":"reused trusted build verification",
                        "source":"verification_reuse",
                        "command":command,
                    }
    return None


def evaluate(root: Path, criteria: list[str], *, timeout: int=120, verification: dict | None = None) -> dict:
    deterministic=[]
    reviewer=[]
    for criterion in criteria:
        item=classify(criterion)
        if item["kind"]=="review":
            reviewer.append(item["raw"])
            continue
        evidence=evaluate_static(root,item["raw"])
        if evidence is None:
            evidence=_reuse_verification(item["raw"],verification)
        if evidence is None:
            evidence=evaluate_command(root,item["raw"],timeout=timeout)
        deterministic.append(evidence)
    return {
        "deterministic":deterministic,
        "reviewer":reviewer,
        "all_deterministic_passed":all(item and item.get("passed") is True for item in deterministic),
    }


def validate_contract(criteria: list[str], *, critical: bool = False) -> dict:
    """Validate structured acceptance criteria before implementation starts."""
    if not isinstance(criteria, list) or not criteria:
        return {
            "valid": False,
            "errors": ["done_when must contain at least one criterion"],
            "deterministic_count": 0,
            "review_count": 0,
        }

    errors = []
    deterministic_count = 0
    review_count = 0

    for raw in criteria:
        criterion = str(raw or "").strip()
        if not criterion:
            errors.append("empty done_when criterion")
            continue
        item = classify(criterion)
        kind = item["kind"]
        spec = item["spec"]

        if kind == "review":
            review_count += 1
            continue

        deterministic_count += 1

        if kind == "file":
            if not spec:
                errors.append(f"invalid file criterion: {criterion}")
            elif spec.startswith("/") or ".." in Path(spec).parts:
                errors.append(f"unsafe file criterion: {criterion}")

        elif kind == "symbol":
            if "#" not in spec:
                errors.append(f"invalid symbol criterion: {criterion}")
            else:
                rel, symbol = spec.split("#", 1)
                rel = rel.strip()
                symbol = symbol.strip()
                if not rel or not symbol:
                    errors.append(f"invalid symbol criterion: {criterion}")
                elif rel.startswith("/") or ".." in Path(rel).parts:
                    errors.append(f"unsafe symbol criterion: {criterion}")

        elif kind == "test":
            if not spec:
                errors.append(f"invalid test criterion: {criterion}")
            else:
                path = spec.split("::", 1)[0].strip()
                if not path or path.startswith("/") or ".." in Path(path).parts:
                    errors.append(f"unsafe test criterion: {criterion}")

        elif kind == "build":
            if spec.strip().lower() not in {"default", "project", "build"}:
                errors.append(f"unsupported build criterion: {criterion}")

        elif kind == "json":
            if "#" not in spec or "=" not in spec:
                errors.append(f"invalid json criterion: {criterion}")
            else:
                rel, expectation = spec.split("#", 1)
                key_path, raw_expected = expectation.split("=", 1)
                rel = rel.strip()
                key_path = key_path.strip()
                raw_expected = raw_expected.strip()
                if not rel or rel.startswith("/") or ".." in Path(rel).parts:
                    errors.append(f"unsafe json criterion: {criterion}")
                elif not key_path:
                    errors.append(f"invalid json criterion: {criterion}")
                else:
                    try:
                        json.loads(raw_expected)
                    except json.JSONDecodeError:
                        errors.append(f"invalid json expected value: {criterion}")

    if critical and deterministic_count < 1:
        errors.append("critical task requires at least one deterministic done_when criterion")

    return {
        "valid": not errors,
        "errors": errors,
        "deterministic_count": deterministic_count,
        "review_count": review_count,
    }
