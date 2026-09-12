"""Synthesize a bounded verifier recipe when a generic stack has no built-in verifier."""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from core import StudioError, canonical
from generic_model import ask
from learning_context import load_context

SYSTEM = """You design verification commands for an autonomous software repository.
Return ONLY JSON:
{"commands":[["executable","arg1","arg2"]],"reason":"why these commands verify the project"}.
Use only tools listed as available. Prefer native test/build/lint commands already supported by the project.
Never install packages, curl/wget remote code, use a shell command string, alter git state, publish, deploy, or access secrets.
Commands must be deterministic and non-interactive."""

ALLOWED_EXECUTABLES = {
    "npm","npx","pnpm","yarn","bun","python","python3","pytest","uv","tox","poetry",
    "go","cargo","rustc","mvn","gradle","bash","dotnet","deno","php","composer",
    "ruby","bundle","rake","swift","make","cmake","ctest","meson","ninja","mix",
    "flutter","dart","godot","java","javac",
}
FORBIDDEN_ARGS = {
    "-c","--command","eval","exec","install","publish","deploy","release","login",
    "push","upload","curl","wget",
}
SAFE_ARG = re.compile(r"^[A-Za-z0-9_./:=+@%,-]{1,180}$")


def available_tools() -> list[str]:
    return sorted(name for name in ALLOWED_EXECUTABLES if shutil.which(name))


def _file_hints(root: Path) -> list[str]:
    hints = []
    for p in sorted(root.rglob("*")):
        if not p.is_file() or p.is_symlink():
            continue
        rel = p.relative_to(root).as_posix()
        if len(rel) > 180:
            continue
        if any(part in {".git","node_modules","vendor","build","dist",".next","target"} for part in p.parts):
            continue
        hints.append(rel)
        if len(hints) >= 300:
            break
    return hints


def validate_recipe(value: object, root: Path) -> dict:
    if not isinstance(value, dict) or set(value) != {"commands","reason"}:
        raise ValueError("Verifier recipe malformed")
    commands = value["commands"]
    reason = value["reason"]
    if not isinstance(reason, str) or not reason.strip() or len(reason) > 2000:
        raise ValueError("Verifier reason invalid")
    if not isinstance(commands, list) or not 1 <= len(commands) <= 6:
        raise ValueError("Verifier command count invalid")
    normalized = []
    for command in commands:
        if not isinstance(command, list) or not 1 <= len(command) <= 24:
            raise ValueError("Verifier command invalid")
        if any(not isinstance(arg, str) or not arg or not SAFE_ARG.fullmatch(arg) for arg in command):
            raise ValueError("Verifier argument rejected")
        exe = command[0]
        if exe not in ALLOWED_EXECUTABLES or shutil.which(exe) is None:
            raise ValueError("Verifier executable unavailable")
        lowered = {arg.lower() for arg in command[1:]}
        if lowered & FORBIDDEN_ARGS:
            raise ValueError("Verifier contains forbidden operation")
        if any(arg.startswith("/") or ".." in Path(arg).parts for arg in command[1:]):
            raise ValueError("Verifier path argument rejected")
        if exe == "bash":
            if len(command) < 2:
                raise ValueError("bash verifier requires a local script")
            script = command[1]
            if script.startswith("-") or not (root / script).is_file():
                raise ValueError("bash verifier may only execute an existing project script")
        normalized.append(command)
    return {"commands": normalized, "reason": reason.strip()}


def synthesize(root: Path, brief: str, previous: dict | None = None) -> tuple[dict, dict]:
    tools = available_tools()
    if not tools:
        raise StudioError("No safe local verification tool is available")
    context = {
        "brief": brief,
        "available_tools": tools,
        "repository_files": _file_hints(root),
        "previous_verification": previous,
        "validated_engineering_memory": load_context(),
    }
    recipe, model = ask(SYSTEM, canonical(context), code=False)
    try:
        return validate_recipe(recipe, root), model
    except ValueError as exc:
        raise StudioError("Adaptive verifier rejected: " + str(exc)) from None


def save_recipe(path: Path, recipe: dict, model: dict) -> None:
    payload = {"status":"validated_recipe","recipe":recipe,"model":model}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
