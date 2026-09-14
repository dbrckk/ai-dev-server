"""Bounded deterministic remediation for security findings.

Only transformations that are semantics-preserving for a release build are
performed here. Findings that need product/security judgement remain blockers.
"""
from __future__ import annotations

from pathlib import Path
import re

MAX_REMEDIATION_ROUNDS = 2


def _android_manifest(root: Path) -> Path:
    return root / "android/app/src/main/AndroidManifest.xml"


def remediate(root: Path, evidence: dict) -> dict:
    blockers = set(evidence.get("blockers", []))
    actions: list[dict] = []
    changed = False

    manifest = _android_manifest(root)
    if manifest.is_file() and not manifest.is_symlink():
        original = manifest.read_text(errors="strict")
        updated = original

        if "release_manifest_debuggable" in blockers:
            updated, count = re.subn(
                r'\s+android:debuggable=(["\'])true\1',
                "",
                updated,
                flags=re.I,
            )
            if count:
                actions.append({
                    "action": "remove_release_debuggable_true",
                    "path": "android/app/src/main/AndroidManifest.xml",
                    "changes": count,
                })

        if "cleartext_network_traffic_detected" in blockers:
            updated, count = re.subn(
                r'android:usesCleartextTraffic=(["\'])true\1',
                r'android:usesCleartextTraffic=\1false\1',
                updated,
                flags=re.I,
            )
            if count:
                actions.append({
                    "action": "disable_android_cleartext_traffic",
                    "path": "android/app/src/main/AndroidManifest.xml",
                    "changes": count,
                })

        if updated != original:
            manifest.write_text(updated)
            changed = True

    return {
        "changed": changed,
        "actions": actions,
        "remaining_requires_rescan": changed,
    }


def remediation_candidate(evidence: dict) -> bool:
    blockers = set(evidence.get("blockers", []))
    return bool(blockers & {
        "release_manifest_debuggable",
        "cleartext_network_traffic_detected",
    })
