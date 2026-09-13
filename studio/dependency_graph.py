"""Lightweight local dependency graph for generic repositories."""
from __future__ import annotations

import ast
import re
from pathlib import Path

_SOURCE_SUFFIXES={".py",".js",".jsx",".ts",".tsx",".mjs",".cjs"}
_TEST_HINTS=("test","tests","spec","__tests__")

_JS_SPEC_RE=re.compile(
    r"""(?:import\s+(?:[^'"]+?\s+from\s+)?|export\s+[^'"]+?\s+from\s+|require\s*\()\s*['"]([^'"]+)['"]"""
)


def _is_test(path:str)->bool:
    low=path.lower()
    return any(part in low for part in _TEST_HINTS)


def _candidate_paths(base:Path,spec:str)->list[Path]:
    target=(base/spec).resolve()
    out=[target]
    if target.suffix:
        return out
    for suffix in (".py",".js",".jsx",".ts",".tsx",".mjs",".cjs"):
        out.append(target.with_suffix(suffix))
    for name in ("__init__.py","index.js","index.jsx","index.ts","index.tsx"):
        out.append(target/name)
    return out


def _resolve_relative(root:Path,source:Path,spec:str)->str|None:
    if not spec.startswith("."):
        return None
    for candidate in _candidate_paths(source.parent,spec):
        try:
            rel=candidate.relative_to(root.resolve()).as_posix()
        except ValueError:
            continue
        if candidate.is_file():
            return rel
    return None


def _python_imports(root:Path,source:Path,text:str)->set[str]:
    try:
        tree=ast.parse(text)
    except SyntaxError:
        return set()
    out=set()
    rel=source.relative_to(root).with_suffix("")
    package=list(rel.parts[:-1])
    for node in ast.walk(tree):
        if isinstance(node,ast.ImportFrom) and node.level>0:
            ascend=max(0,node.level-1)
            base=package[:max(0,len(package)-ascend)]
            module=(node.module or "").split(".") if node.module else []
            targets=[[*base,*module]] if module else [
                [*base,*alias.name.split(".")] for alias in node.names
            ]
            for parts in targets:
                candidates=[]
                if parts:
                    candidates.append(root.joinpath(*parts).with_suffix(".py"))
                    candidates.append(root.joinpath(*parts,"__init__.py"))
                for candidate in candidates:
                    if candidate.is_file():
                        out.add(candidate.relative_to(root).as_posix())
                        break
        elif isinstance(node,ast.Import):
            for alias in node.names:
                parts=alias.name.split(".")
                candidates=[
                    root.joinpath(*parts).with_suffix(".py"),
                    root.joinpath(*parts,"__init__.py"),
                ]
                for candidate in candidates:
                    if candidate.is_file():
                        out.add(candidate.relative_to(root).as_posix())
                        break
        elif isinstance(node,ast.ImportFrom) and node.level==0 and node.module:
            base=node.module.split(".")
            targets=[base]
            targets.extend([*base,*alias.name.split(".")] for alias in node.names)
            for parts in targets:
                candidates=[
                    root.joinpath(*parts).with_suffix(".py"),
                    root.joinpath(*parts,"__init__.py"),
                ]
                for candidate in candidates:
                    if candidate.is_file():
                        out.add(candidate.relative_to(root).as_posix())
                        break
    return out


def _js_imports(root:Path,source:Path,text:str)->set[str]:
    out=set()
    for spec in _JS_SPEC_RE.findall(text):
        resolved=_resolve_relative(root,source,spec)
        if resolved:
            out.add(resolved)
    return out


def build(root:Path)->dict:
    root=Path(root).resolve()
    files=[]
    for p in sorted(root.rglob("*")):
        if not p.is_file() or p.is_symlink() or p.suffix.lower() not in _SOURCE_SUFFIXES:
            continue
        parts=set(p.relative_to(root).parts)
        if parts & {".git","node_modules","dist","build","target",".studio-venv","__pycache__"}:
            continue
        files.append(p)

    edges={}
    reverse={}
    tests=[]
    for source in files:
        rel=source.relative_to(root).as_posix()
        try:
            text=source.read_text(encoding="utf-8")
        except (OSError,UnicodeError):
            continue
        deps=(
            _python_imports(root,source,text)
            if source.suffix.lower()==".py"
            else _js_imports(root,source,text)
        )
        deps.discard(rel)
        edges[rel]=sorted(deps)
        if _is_test(rel):
            tests.append(rel)
        for dep in deps:
            reverse.setdefault(dep,[]).append(rel)

    return {
        "files":sorted(edges),
        "edges":edges,
        "reverse":{k:sorted(set(v)) for k,v in reverse.items()},
        "tests":sorted(tests),
        "edge_count":sum(len(v) for v in edges.values()),
    }


def assess(graph:dict,focus_files:list[str]|None=None)->dict:
    edges=graph.get("edges",{}) if isinstance(graph,dict) else {}
    reverse=graph.get("reverse",{}) if isinstance(graph,dict) else {}
    tests=set(graph.get("tests",[])) if isinstance(graph,dict) else set()
    focus=[f for f in (focus_files or []) if f in edges or f in reverse]
    if not focus:
        candidates=sorted(
            set(edges)|set(reverse),
            key=lambda rel:(-(len(edges.get(rel,[]))+len(reverse.get(rel,[]))),rel),
        )
        focus=candidates[:8]

    impacted=set(focus)
    frontier=list(focus)
    depth=0
    while frontier and depth<3 and len(impacted)<200:
        nxt=[]
        for rel in frontier:
            for parent in reverse.get(rel,[]):
                if parent not in impacted:
                    impacted.add(parent)
                    nxt.append(parent)
        frontier=nxt
        depth+=1

    impacted_tests=sorted(t for t in impacted if t in tests)
    scores=[]
    for rel in focus:
        fan_in=len(reverse.get(rel,[]))
        fan_out=len(edges.get(rel,[]))
        scores.append({
            "path":rel,
            "fan_in":fan_in,
            "fan_out":fan_out,
            "coupling":fan_in+fan_out,
        })
    scores.sort(key=lambda x:(-x["coupling"],x["path"]))
    max_coupling=scores[0]["coupling"] if scores else 0
    if max_coupling>=8:
        level="high"; max_patch_files=2
    elif max_coupling>=4:
        level="medium"; max_patch_files=4
    else:
        level="low"; max_patch_files=8

    return {
        "level":level,
        "max_coupling":max_coupling,
        "max_patch_files":max_patch_files,
        "focus":scores[:20],
        "impacted_files":sorted(impacted)[:100],
        "impacted_tests":impacted_tests[:50],
        "edge_count":int(graph.get("edge_count",0)) if isinstance(graph,dict) else 0,
    }


def patch_guard(graph:dict,files:list[str])->dict:
    """Assess whether a multi-file patch crosses a highly coupled local boundary."""
    unique=sorted(set(str(f) for f in files if f))
    edges=graph.get("edges",{}) if isinstance(graph,dict) else {}
    reverse=graph.get("reverse",{}) if isinstance(graph,dict) else {}
    direct_pairs=[]
    for left in unique:
        for right in unique:
            if left>=right:
                continue
            if right in edges.get(left,[]) or left in edges.get(right,[]):
                direct_pairs.append([left,right])
    max_coupling=0
    for rel in unique:
        max_coupling=max(
            max_coupling,
            len(edges.get(rel,[]))+len(reverse.get(rel,[])),
        )
    reject=bool(len(unique)>1 and direct_pairs and max_coupling>=8)
    reason=(
        "patch spans directly coupled files in a high-coupling hotspot"
        if reject else
        "patch coupling within allowed bound"
    )
    return {
        "reject":reject,
        "reason":reason,
        "files":unique,
        "direct_pairs":direct_pairs[:50],
        "max_coupling":max_coupling,
    }
