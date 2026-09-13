"""Conservative targeted pre-verification from dependency impact hints."""
from __future__ import annotations

from pathlib import Path

from generic_sandbox import run as run_command
from generic_verify import discover


def targeted_command(root: Path, impacted_tests: list[str]) -> list[str] | None:
    tests=sorted(set(str(x) for x in impacted_tests if x))
    if not tests:
        return None
    commands=discover(root)
    for command in commands:
        if not command:
            continue
        exe=Path(command[0]).name
        if exe=="pytest":
            return [*command,*tests]
        if exe=="uv" and len(command)>=3 and command[1:3]==["run","pytest"]:
            return [*command,*tests]
    return None


def run(root: Path, impacted_tests: list[str], *, timeout: int=120) -> dict:
    command=targeted_command(root,impacted_tests)
    if command is None:
        return {
            "status":"unsupported",
            "passed":None,
            "command":None,
            "impacted_tests":sorted(set(impacted_tests)),
        }
    result=run_command(command,root,timeout=max(30,min(300,int(timeout))),network=False)
    return {
        "status":"passed" if result.get("passed") else "failed",
        "passed":result.get("passed") is True,
        "command":command,
        "impacted_tests":sorted(set(impacted_tests)),
        "result":result,
    }
