"""Plan minimal trusted Flutter quick gates from an editable-source delta."""
from __future__ import annotations

from pathlib import Path
import re

DEPENDENCY_FILES = {"pubspec.yaml"}
ANALYZE_FILES = {"analysis_options.yaml", "pubspec.yaml"}


def _package_name(root: Path) -> str | None:
    pubspec = root / "pubspec.yaml"
    if not pubspec.is_file():
        return None
    try:
        text = pubspec.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return None
    match = re.search(r"(?m)^name:\s*([a-zA-Z0-9_]+)\s*$", text)
    return match.group(1) if match else None


def _targeted_tests(root: Path, changed: list[str]) -> list[str]:
    targets: set[str] = set()
    changed_lib = [
        rel[len("lib/"):]
        for rel in changed
        if rel.startswith("lib/") and rel.endswith(".dart")
    ]
    for rel in changed:
        if rel.startswith("test/") and rel.endswith("_test.dart"):
            if (root / rel).is_file():
                targets.add(rel)
            continue
        if rel.startswith("lib/") and rel.endswith(".dart"):
            stem = rel[len("lib/"):-len(".dart")]
            direct = "test/" + stem + "_test.dart"
            leaf = "test/" + Path(stem).name + "_test.dart"
            for candidate in (direct, leaf):
                if (root / candidate).is_file():
                    targets.add(candidate)

    if changed_lib:
        package = _package_name(root)
        for path in sorted((root / "test").rglob("*_test.dart")) if (root / "test").is_dir() else []:
            if path.is_symlink() or not path.is_file():
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeError):
                continue
            rel_test = path.relative_to(root).as_posix()
            for lib_rel in changed_lib:
                package_import = f"package:{package}/{lib_rel}" if package else None
                if package_import and package_import in text:
                    targets.add(rel_test)
                    break
                if re.search(r"['\"][^'\"]*" + re.escape(lib_rel) + r"['\"]", text):
                    targets.add(rel_test)
                    break
    return sorted(targets)


def plan(root: Path, changed: list[str]) -> dict:
    changed = sorted({item for item in changed if isinstance(item, str) and item})
    dependency_changed = any(item in DEPENDENCY_FILES for item in changed)
    lib_changed = any(
        item.startswith("lib/") and item.endswith(".dart")
        for item in changed
    )
    test_changed = any(
        item.startswith("test/") and item.endswith(".dart")
        for item in changed
    )
    code_changed = lib_changed or test_changed
    # Test-only deltas are compiled by their targeted quick test. Full project
    # analysis remains mandatory in the final trusted gate set.
    analyze_needed = lib_changed or any(item in ANALYZE_FILES for item in changed)
    tests_needed = code_changed
    targeted = _targeted_tests(root, changed) if tests_needed else []

    return {
        "changed": changed,
        "dependency": dependency_changed,
        "analyze": analyze_needed,
        "test": tests_needed,
        "targeted_tests": targeted,
        "test_mode": "targeted" if targeted else ("full" if tests_needed else "skip"),
    }
