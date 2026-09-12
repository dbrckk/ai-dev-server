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
        venv_pytest=root/".studio-venv/bin/pytest"
        venv_python=root/".studio-venv/bin/python"
        if venv_pytest.is_file():
            commands.append([str(venv_pytest), "-q"])
        elif venv_python.is_file():
            commands.append([str(venv_python), "-m", "unittest", "discover"])
        elif (root/"uv.lock").is_file() and shutil.which("uv"):
            commands.append(["uv","run","pytest","-q"])
        elif shutil.which("pytest"):
            commands.append(["pytest", "-q"])
        elif shutil.which("python"):
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
    if (root/"deno.json").is_file() or (root/"deno.jsonc").is_file():
        if shutil.which("deno"):
            commands.append(["deno","test","--no-prompt"])
    if (root/"bun.lock").is_file() or (root/"bun.lockb").is_file():
        if shutil.which("bun"):
            commands.append(["bun","test"])
    if (root/"composer.json").is_file() and shutil.which("php"):
        if (root/"vendor/bin/phpunit").is_file():
            commands.append(["php","vendor/bin/phpunit"])
    if (root/"Gemfile").is_file() and shutil.which("bundle"):
        if (root/"Rakefile").is_file():
            commands.append(["bundle","exec","rake","test"])
    if (root/"mix.exs").is_file() and shutil.which("mix"):
        commands.append(["mix","test"])
    if (root/"Package.swift").is_file() and shutil.which("swift"):
        commands.append(["swift","test"])
    if (root/"CMakeLists.txt").is_file() and shutil.which("cmake") and shutil.which("ctest"):
        commands.append(["cmake","-S",".","-B",".studio-cmake-build"])
        commands.append(["cmake","--build",".studio-cmake-build"])
        commands.append(["ctest","--test-dir",".studio-cmake-build","--output-on-failure"])
    elif (root/"Makefile").is_file() and shutil.which("make"):
        commands.append(["make","test"])
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
