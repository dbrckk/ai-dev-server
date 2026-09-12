"""Trusted verification command discovery for generic repositories."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import time


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


def run(root: Path, *, timeout_per_command: int = 900) -> dict:
    commands = discover(root)
    if not commands:
        return {"status": "no_verifier", "passed": False, "commands": [], "results": []}
    results = []
    all_passed = True
    safe_env = {
        "PATH": __import__("os").environ.get("PATH", ""),
        "HOME": __import__("os").environ.get("HOME", "/tmp"),
        "CI": "true",
    }
    for command in commands:
        started = time.monotonic()
        try:
            p = subprocess.run(
                command, cwd=root, env=safe_env, stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                timeout=timeout_per_command, check=False,
            )
            rc = p.returncode
            log = p.stdout[-20000:]
        except (OSError, subprocess.TimeoutExpired) as exc:
            rc = 124
            log = type(exc).__name__
        passed = rc == 0
        all_passed = all_passed and passed
        results.append({
            "command": command,
            "returncode": rc,
            "passed": passed,
            "duration_seconds": round(time.monotonic() - started, 3),
            "log_tail": log,
        })
        if not passed:
            break
    return {
        "status": "passed" if all_passed else "failed",
        "passed": all_passed,
        "commands": commands,
        "results": results,
    }
