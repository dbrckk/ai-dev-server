"""Fail-closed guard for architecture-sensitive model patches."""
from __future__ import annotations

from pathlib import PurePosixPath


COMMON_ARCHITECTURE_NAMES = {
    "package.json",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "requirements.txt",
    "pyproject.toml",
    "poetry.lock",
    "Pipfile",
    "Pipfile.lock",
    "Cargo.toml",
    "Cargo.lock",
    "go.mod",
    "go.sum",
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "compose.yml",
    "compose.yaml",
    "settings.gradle",
    "settings.gradle.kts",
    "build.gradle",
    "build.gradle.kts",
    "gradle.properties",
    "libs.versions.toml",
}
COMMON_ARCHITECTURE_PREFIXES = (
    ".github/workflows/",
    "docker/",
    "infra/",
    "infrastructure/",
    "terraform/",
    "k8s/",
    "kubernetes/",
    "helm/",
)
FLUTTER_ARCHITECTURE_NAMES = {
    "pubspec.yaml",
    "pubspec.lock",
    "analysis_options.yaml",
}
GODOT_ARCHITECTURE_NAMES = {
    "project.godot",
    "export_presets.cfg",
}
GODOT_ARCHITECTURE_PREFIXES = (
    "addons/",
)


class ArchitectureChangeBlocked(ValueError):
    pass


def is_architecture_sensitive(path: str, engine: str = "generic") -> bool:
    if not isinstance(path, str) or not path:
        return True
    normalized = PurePosixPath(path).as_posix()
    name = PurePosixPath(normalized).name
    if name in COMMON_ARCHITECTURE_NAMES:
        return True
    if any(normalized.startswith(prefix) for prefix in COMMON_ARCHITECTURE_PREFIXES):
        return True
    if engine == "flutter" and name in FLUTTER_ARCHITECTURE_NAMES:
        return True
    if engine == "godot":
        if name in GODOT_ARCHITECTURE_NAMES:
            return True
        if any(normalized.startswith(prefix) for prefix in GODOT_ARCHITECTURE_PREFIXES):
            return True
    return False


def inspect_patch(value: object, *, engine: str = "generic") -> dict:
    files = value.get("files") if isinstance(value, dict) else None
    if not isinstance(files, list):
        return {
            "architecture_sensitive": True,
            "sensitive_paths": [],
            "reason": "invalid patch envelope",
        }
    sensitive = []
    for item in files:
        if not isinstance(item, dict):
            continue
        path = item.get("path")
        if isinstance(path, str) and is_architecture_sensitive(path, engine):
            sensitive.append(path)
    return {
        "architecture_sensitive": bool(sensitive),
        "sensitive_paths": sorted(set(sensitive)),
        "reason": "architecture-sensitive files present" if sensitive else "source-only patch",
    }


def enforce(
    value: object,
    *,
    engine: str = "generic",
    architecture_changes_allowed: bool = True,
) -> dict:
    result = inspect_patch(value, engine=engine)
    if result["architecture_sensitive"] and not architecture_changes_allowed:
        paths = ", ".join(result["sensitive_paths"][:12]) or "<unknown>"
        raise ArchitectureChangeBlocked(
            "Architecture preflight HOLD blocks architecture-sensitive patch paths: " + paths
        )
    return result
