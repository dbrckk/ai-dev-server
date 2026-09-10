"""Trusted Godot session adapter for the generic studio.

This adapter deliberately exposes only validation. Android export, rendering and device QA
remain separate completion capabilities and are not implied by a successful headless gate.
"""
from __future__ import annotations

from pathlib import Path
import tempfile

from core import StudioError
from godot_runtime import install, validate


class GodotSandbox:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def create(self, name: str) -> None:
        if not self.root.is_dir() or not (self.root / 'project.godot').is_file():
            raise StudioError('Godot sessions require an existing project.godot project')

    def gates(self, name: str, journeys) -> tuple[bool, list[dict]]:
        # journeys are retained in the generic contract but headless Godot validation does
        # not claim to execute user journeys. Runtime/device journey QA is a later gate.
        with tempfile.TemporaryDirectory(prefix='studio-godot-runtime-') as cache:
            binary = install(Path(cache))
            result = validate(self.root, binary, timeout=600)
        evidence = {
            'command': ['godot', '--headless', '--editor', '--quit'],
            'exit_code': result['exit_code'],
            'output': result['output'],
            'engine_version': result['engine_version'],
            'archive_sha256': result['archive_sha256'],
            'binary_sha256': result['binary_sha256'],
            'network': result['network'],
            'source_project_immutable': result.get('source_project_immutable', False),
            'journeys_executed': False,
        }
        return bool(result['passed']), [evidence]
