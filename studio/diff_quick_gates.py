"""Plan minimal trusted Flutter quick gates from an editable-source delta."""
from __future__ import annotations

from pathlib import Path

DEPENDENCY_FILES = {"pubspec.yaml"}
ANALYZE_FILES = {"analysis_options.yaml", "pubspec.yaml"}


def _targeted_tests(root: Path, changed: list[str]) -> list[str]:
    targets: set[str] = set()
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
    return sorted(targets)


def plan(root: Path, changed: list[str]) -> dict:
    changed = sorted({item for item in changed if isinstance(item, str) and item})
    dependency_changed = any(item in DEPENDENCY_FILES for item in changed)
    code_changed = any(
        item.startswith(("lib/", "test/")) and item.endswith(".dart")
        for item in changed
    )
    analyze_needed = code_changed or any(item in ANALYZE_FILES for item in changed)
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
