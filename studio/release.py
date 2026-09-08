"""Trusted post-preview release evidence collection.

This module performs only deterministic build/evidence work. Model output never
controls shell commands and signing credentials are never placed in model context.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

from core import Sandbox, StudioError


def build_release(root: Path, sandbox: Sandbox | None = None) -> dict:
    """Build a release AAB and return verifiable evidence.

    This proves that the generated source can produce a release-mode bundle. It
    intentionally does not claim Play signing, store submission, or device QA.
    """
    sandbox = sandbox or Sandbox(root)
    commands = [
        (['flutter', 'pub', 'get'], True),
        (['flutter', 'analyze', '--no-pub'], False),
        (['flutter', 'test', '--no-pub', '--exclude-tags=studio-visual'], False),
        (['flutter', 'build', 'appbundle', '--release', '--no-pub'], True),
    ]
    logs = []
    for args, network in commands:
        rc, output = sandbox.run(args, network=network, timeout=1200)
        logs.append({'command': args, 'exit_code': rc, 'output': output})
        if rc:
            return {'passed': False, 'logs': logs}

    bundle = root / 'build/app/outputs/bundle/release/app-release.aab'
    if not bundle.is_file() or bundle.stat().st_size <= 1000:
        raise StudioError('Release build reported success but no valid AAB was produced')
    raw = bundle.read_bytes()
    return {
        'passed': True,
        'artifact': 'app-release.aab',
        'bytes': len(raw),
        'sha256': hashlib.sha256(raw).hexdigest(),
        'logs': logs,
    }
