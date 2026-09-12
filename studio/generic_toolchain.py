"""Trusted toolchain/dependency preparation for generic repositories.

Only deterministic project-native package-manager operations are emitted.
No model-generated bootstrap command is executed here.
"""
from __future__ import annotations

import json
from pathlib import Path
import shutil

def detect(root: Path) -> dict:
    markers=[]
    if (root/"package.json").is_file(): markers.append("node")
    if (root/"pyproject.toml").is_file() or (root/"requirements.txt").is_file(): markers.append("python")
    if (root/"go.mod").is_file(): markers.append("go")
    if (root/"Cargo.toml").is_file(): markers.append("rust")
    if (root/"pom.xml").is_file(): markers.append("maven")
    if (root/"gradlew").is_file() or (root/"build.gradle").is_file() or (root/"build.gradle.kts").is_file(): markers.append("gradle")
    if any(root.glob("*.sln")) or any(root.glob("*.csproj")): markers.append("dotnet")
    if (root/"composer.json").is_file(): markers.append("php")
    if (root/"Gemfile").is_file(): markers.append("ruby")
    if (root/"mix.exs").is_file(): markers.append("elixir")
    if (root/"Package.swift").is_file(): markers.append("swift")
    return {"stacks":markers}

def bootstrap_commands(root: Path) -> list[list[str]]:
    commands=[]
    if (root/"package.json").is_file():
        if (root/"package-lock.json").is_file() and shutil.which("npm"):
            commands.append(["npm","ci","--ignore-scripts","--no-audit","--no-fund"])
        elif (root/"pnpm-lock.yaml").is_file() and shutil.which("pnpm"):
            commands.append(["pnpm","install","--frozen-lockfile","--ignore-scripts"])
        elif (root/"yarn.lock").is_file() and shutil.which("yarn"):
            commands.append(["yarn","install","--immutable","--ignore-scripts"])
    if (root/"pyproject.toml").is_file() and (root/"uv.lock").is_file() and shutil.which("uv"):
        commands.append(["uv","sync","--frozen"])
    elif (root/"requirements.txt").is_file() and shutil.which("python"):
        commands.append(["python","-m","venv",".studio-venv"])
        commands.append([".studio-venv/bin/pip","install","--disable-pip-version-check","-r","requirements.txt"])
    if (root/"go.mod").is_file() and shutil.which("go"):
        commands.append(["go","mod","download"])
    if (root/"Cargo.toml").is_file() and (root/"Cargo.lock").is_file() and shutil.which("cargo"):
        commands.append(["cargo","fetch","--locked"])
    if (root/"composer.json").is_file() and (root/"composer.lock").is_file() and shutil.which("composer"):
        commands.append(["composer","install","--no-interaction","--no-scripts","--no-plugins"])
    if (root/"Gemfile").is_file() and (root/"Gemfile.lock").is_file() and shutil.which("bundle"):
        commands.append(["bundle","install","--deployment"])
    return commands
