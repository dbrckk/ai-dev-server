"""Trusted verification command discovery for generic repositories."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import time

from generic_sandbox import run as run_command


def discover(root: Path) -> list[list[str]]:
    commands: list[list[str]] = []
    package = root / "package.json"
    if package.is_file():
        try:
            data = json.loads(package.read_text())
        except (OSError, json.JSONDecodeError):
            data = {}
        scripts = data.get("scripts") if isinstance(data, dict) else {}
        if (root / "package-lock.json").is_file() and shutil.which("npm"):
            commands.append(["npm", "ci", "--ignore-scripts"])
        if isinstance(scripts, dict) and "test" in scripts and shutil.which("npm"):
            commands.append(["npm", "test", "--", "--runInBand"])
        if isinstance(scripts, dict) and "build" in scripts and shutil.which("npm"):
            commands.append(["npm", "run", "build"])
    if (root / "pyproject.toml").is_file() or (root / "requirements.txt").is_file():
        if shutil.which("python"):
            if shutil.which("pytest"):
                commands.append(["pytest", "-q"])
            else:
                commands.append(["python", "-m", "unittest", "discover"])
    if (root / "go.mod").is_file() and shutil.which("go"):
        commands.append(["go", "test", "./..."])
    if (root / "Cargo.toml").is_file() and shutil.which("cargo"):
        commands.append(["cargo", "test", "--all-targets"])
    if (root / "pom.xml").is_file() and shutil.which("mvn"):
        commands.append(["mvn", "-B", "test"])
    if (root / "gradlew").is_file():
        commands.append(["bash", "./gradlew", "test", "--no-daemon"])
    if any(root.glob("*.sln")) or any(root.glob("*.csproj")):
        if shutil.which("dotnet"):
            commands.append(["dotnet", "test", "--nologo"])
    return commands


def run(root: Path, *, timeout_per_command: int = 900, commands: list[list[str]] | None = None) -> dict:
    commands = discover(root) if commands is None else commands
    if not commands:
        return {"status": "no_verifier", "passed": False, "commands": [], "results": []}
    results = []
    all_passed = True
    for command in commands:
        result = run_command(command, root, timeout=timeout_per_command, network=False)
        passed = result["passed"]
        all_passed = all_passed and passed
        results.append(result)
        if not passed:
            break
    return {
        "status": "passed" if all_passed else "failed",
        "passed": all_passed,
        "commands": commands,
        "results": results,
    }
