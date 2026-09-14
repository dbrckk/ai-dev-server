"""Deterministic evaluation for structured done_when criteria."""
from __future__ import annotations

import ast
import json
import re
from pathlib import Path

from generic_sandbox import run as run_command

_PREFIXES=("file:","symbol:","test:","build:")


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


def evaluate(root: Path, criteria: list[str], *, timeout: int=120) -> dict:
    deterministic=[]
    reviewer=[]
    for criterion in criteria:
        item=classify(criterion)
        if item["kind"]=="review":
            reviewer.append(item["raw"])
            continue
        evidence=evaluate_static(root,item["raw"])
        if evidence is None:
            evidence=evaluate_command(root,item["raw"],timeout=timeout)
        deterministic.append(evidence)
    return {
        "deterministic":deterministic,
        "reviewer":reviewer,
        "all_deterministic_passed":all(item and item.get("passed") is True for item in deterministic),
    }
