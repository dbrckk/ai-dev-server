"""Fail-closed guard for architecture-sensitive model patches."""
from __future__ import annotations

from pathlib import Path, PurePosixPath
import re


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

SEMANTIC_IMPORT_PATTERNS = {
    "python": re.compile(r"^(?:from\s+([A-Za-z0-9_.]+)\s+import|import\s+([A-Za-z0-9_.]+))", re.MULTILINE),
    "dart": re.compile(r"^import\s+['\"]([^'\"]+)['\"];", re.MULTILINE),
    "js": re.compile(r"^(?:import .*? from\s+['\"]([^'\"]+)['\"]|(?:const|let|var).*?require\(['\"]([^'\"]+)['\"]\))", re.MULTILINE),
    "godot": re.compile(r"^(?:extends|class_name|preload|load)\s*\(?['\"]?([^'\")\s]+)", re.MULTILINE),
}

SEMANTIC_MARKERS = (
    "router",
    "routing",
    "navigator",
    "dependency injection",
    "dependency_injection",
    "service locator",
    "provider",
    "repository",
    "persistence",
    "database",
    "storage",
    "event bus",
    "message bus",
    "middleware",
    "container",
)


def _language(path: str) -> str | None:
    suffix = PurePosixPath(path).suffix.lower()
    if suffix == ".py":
        return "python"
    if suffix == ".dart":
        return "dart"
    if suffix in {".js", ".jsx", ".ts", ".tsx"}:
        return "js"
    if suffix == ".gd":
        return "godot"
    return None


def _imports(text: str, language: str | None) -> set[str]:
    if not language or not isinstance(text, str):
        return set()
    pattern = SEMANTIC_IMPORT_PATTERNS.get(language)
    if pattern is None:
        return set()
    found = set()
    for match in pattern.finditer(text):
        for group in match.groups():
            if group:
                found.add(group.strip())
    return found


def _marker_hits(text: str) -> set[str]:
    lowered = text.lower() if isinstance(text, str) else ""
    return {marker for marker in SEMANTIC_MARKERS if marker in lowered}


def semantic_impact(path: str, old_content: str, new_content: str) -> dict:
    language = _language(path)
    old_imports = _imports(old_content, language)
    new_imports = _imports(new_content, language)
    added_imports = sorted(new_imports - old_imports)
    removed_imports = sorted(old_imports - new_imports)
    old_markers = _marker_hits(old_content)
    new_markers = _marker_hits(new_content)
    added_markers = sorted(new_markers - old_markers)

    score = 0
    score += min(4, len(added_imports) + len(removed_imports))
    score += min(4, len(added_markers) * 2)

    path_lower = path.lower()
    if any(token in path_lower for token in ("router", "routing", "container", "repository", "storage", "database", "service")):
        score += 2
    if len(new_content) > max(4000, len(old_content) * 2) and len(new_content) - len(old_content) > 1500:
        score += 1

    return {
        "path": path,
        "impact_score": score,
        "architecture_semantic": score >= 4,
        "added_imports": added_imports[:12],
        "removed_imports": removed_imports[:12],
        "added_markers": added_markers[:12],
    }


def inspect_semantic_patch(value: object, root: Path | str | None) -> dict:
    if root is None or not isinstance(value, dict):
        return {"architecture_semantic": False, "semantic_paths": [], "details": []}
    files = value.get("files")
    if not isinstance(files, list):
        return {"architecture_semantic": True, "semantic_paths": [], "details": []}
    root = Path(root)
    details = []
    for item in files:
        if not isinstance(item, dict):
            continue
        path = item.get("path")
        content = item.get("content")
        if not isinstance(path, str) or not isinstance(content, str):
            continue
        target = root / path
        try:
            old_content = target.read_text(encoding="utf-8") if target.is_file() else ""
        except (OSError, UnicodeError):
            old_content = ""
        impact = semantic_impact(path, old_content, content)
        if impact["architecture_semantic"]:
            details.append(impact)
    return {
        "architecture_semantic": bool(details),
        "semantic_paths": [item["path"] for item in details],
        "details": details[:12],
    }



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
    root: Path | str | None = None,
) -> dict:
    result = inspect_patch(value, engine=engine)
    semantic = inspect_semantic_patch(value, root)
    result["architecture_semantic"] = semantic["architecture_semantic"]
    result["semantic_paths"] = semantic["semantic_paths"]
    result["semantic_details"] = semantic["details"]

    if not architecture_changes_allowed:
        blocked = sorted(set(result["sensitive_paths"] + result["semantic_paths"]))
        if blocked:
            raise ArchitectureChangeBlocked(
                "Architecture preflight HOLD blocks architecture-sensitive patch paths: "
                + ", ".join(blocked[:12])
            )
    return result
