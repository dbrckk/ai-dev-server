"""Trusted Play Billing QA contract.

This stage never fabricates a successful purchase. It validates the generated app's
billing integration and accepts an external Play Billing sandbox result only when
that evidence matches the exact package and release APK hash.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

from core import StudioError, canonical
from device_qa import package_name

BILLING_DEPENDENCIES = {'in_app_purchase', 'purchases_flutter'}
BILLING_MARKERS = ('InAppPurchase', 'PurchaseDetails', 'ProductDetails', 'Purchases.')
REQUIRED_OUTCOMES = ('product_query', 'purchase_success', 'purchase_cancel', 'purchase_restore')


def _pubspec_dependencies(root: Path) -> set[str]:
    path = root / 'pubspec.yaml'
    if not path.is_file():
        return set()
    deps: set[str] = set()
    in_deps = False
    for raw in path.read_text(errors='replace').splitlines():
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        if not line.startswith(' '):
            in_deps = line.strip() == 'dependencies:'
            continue
        if in_deps:
            match = re.match(r'^\s{2}([A-Za-z0-9_]+):', line)
            if match:
                deps.add(match.group(1))
    return deps


def _source_markers(root: Path) -> list[str]:
    found: set[str] = set()
    lib = root / 'lib'
    if not lib.is_dir():
        return []
    for path in lib.rglob('*.dart'):
        if path.is_symlink() or path.stat().st_size > 500_000:
            continue
        text = path.read_text(errors='replace')
        for marker in BILLING_MARKERS:
            if marker in text:
                found.add(marker)
    return sorted(found)


def _apk_hash(root: Path) -> str | None:
    apk = root / 'build/app/outputs/flutter-apk/app-release.apk'
    if not apk.is_file() or apk.stat().st_size < 1000:
        return None
    return hashlib.sha256(apk.read_bytes()).hexdigest()


def validate_sandbox_evidence(value: object, package: str, apk_sha256: str) -> dict:
    if not isinstance(value, dict):
        raise StudioError('Billing sandbox evidence must be an object')
    allowed = {'schema', 'provider', 'package', 'apk_sha256', 'tester_mode', 'outcomes'}
    if set(value) != allowed:
        raise StudioError('Billing sandbox evidence schema mismatch')
    if value.get('schema') != 1 or value.get('provider') != 'google_play_billing_sandbox':
        raise StudioError('Unsupported billing sandbox evidence provider')
    if value.get('package') != package or value.get('apk_sha256') != apk_sha256:
        raise StudioError('Billing sandbox evidence does not match release artifact')
    if value.get('tester_mode') is not True:
        raise StudioError('Billing evidence must come from Play tester mode')
    outcomes = value.get('outcomes')
    if not isinstance(outcomes, dict) or set(outcomes) != set(REQUIRED_OUTCOMES):
        raise StudioError('Billing sandbox outcomes are incomplete')
    for name in REQUIRED_OUTCOMES:
        entry = outcomes[name]
        if not isinstance(entry, dict) or set(entry) != {'passed'} or entry.get('passed') is not True:
            raise StudioError('Billing sandbox outcome failed: ' + name)
    return value


def validate_billing(root: Path, out: Path) -> dict:
    package = package_name(root)
    apk_sha256 = _apk_hash(root)
    dependencies = sorted(_pubspec_dependencies(root) & BILLING_DEPENDENCIES)
    markers = _source_markers(root)
    blockers: list[str] = []

    if not apk_sha256:
        blockers.append('release_apk_missing')
    if not dependencies and not markers:
        blockers.append('billing_integration_not_detected')

    sandbox_path = out / 'billing-sandbox-evidence.json'
    sandbox = None
    if apk_sha256 and sandbox_path.is_file():
        try:
            sandbox = validate_sandbox_evidence(json.loads(sandbox_path.read_text()), package, apk_sha256)
        except (OSError, json.JSONDecodeError, StudioError):
            blockers.append('billing_sandbox_evidence_invalid')
    elif apk_sha256:
        blockers.append('play_billing_sandbox_purchase_not_verified')

    evidence = {
        'passed': not blockers,
        'package': package,
        'apk_sha256': apk_sha256,
        'dependencies': dependencies,
        'source_markers': markers,
        'sandbox_verified': sandbox is not None,
        'required_outcomes': list(REQUIRED_OUTCOMES),
        'blockers': blockers,
        'limitations': [] if sandbox is not None else [
            'A local emulator or adb command cannot prove a Google Play purchase transaction.',
            'A Play tester account/store-backed sandbox result is required for purchase success, cancellation and restore.',
        ],
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / 'billing-qa.json').write_text(canonical(evidence))
    return evidence
