"""Trusted post-preview release evidence collection.

This module performs only deterministic build/evidence work. Model output never
controls shell commands and signing credentials are never placed in model context.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

from core import Sandbox, StudioError


def build_release(root: Path, sandbox: Sandbox | None = None) -> dict:
    """Build release AAB + APK and return verifiable evidence.

    The AAB is the store-oriented artifact. The APK is produced from the same
    source/release mode so trusted Android emulator QA can install exactly the
    release configuration instead of falling back to a debug build.
    """
    sandbox = sandbox or Sandbox(root)
    commands = [
        (['flutter', 'pub', 'get'], True),
        (['flutter', 'analyze', '--no-pub'], False),
        (['flutter', 'test', '--no-pub', '--exclude-tags=studio-visual'], False),
        (['flutter', 'build', 'appbundle', '--release', '--no-pub'], True),
        (['flutter', 'build', 'apk', '--release', '--no-pub'], True),
    ]
    logs = []
    for args, network in commands:
        rc, output = sandbox.run(args, network=network, timeout=1200)
        logs.append({'command': args, 'exit_code': rc, 'output': output})
        if rc:
            return {'passed': False, 'logs': logs}

    bundle = root / 'build/app/outputs/bundle/release/app-release.aab'
    apk = root / 'build/app/outputs/flutter-apk/app-release.apk'
    if not bundle.is_file() or bundle.stat().st_size <= 1000:
        raise StudioError('Release build reported success but no valid AAB was produced')
    if not apk.is_file() or apk.stat().st_size <= 1000:
        raise StudioError('Release build reported success but no valid APK was produced')

    bundle_raw = bundle.read_bytes()
    apk_raw = apk.read_bytes()
    return {
        'passed': True,
        'artifact': 'app-release.aab',
        'bytes': len(bundle_raw),
        'sha256': hashlib.sha256(bundle_raw).hexdigest(),
        'installable_artifact': 'app-release.apk',
        'installable_bytes': len(apk_raw),
        'installable_sha256': hashlib.sha256(apk_raw).hexdigest(),
        'logs': logs,
    }
