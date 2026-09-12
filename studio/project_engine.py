"""Trusted mobile project-engine identification and path policy.

This module is intentionally independent from model output. Engine selection is
based on repository markers and each engine gets its own bounded editable scope.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath


class EngineError(ValueError):
    pass


@dataclass(frozen=True)
class EngineProfile:
    name: str
    marker: str
    test_suffix: str


FLUTTER = EngineProfile('flutter', 'pubspec.yaml', '_test.dart')
GODOT = EngineProfile('godot', 'project.godot', '.gd')
GENERIC = EngineProfile('generic', '*', '')
PROFILES = {profile.name: profile for profile in (FLUTTER, GODOT, GENERIC)}

_GODOT_ROOT_EDITABLE = {'project.godot', 'export_presets.cfg'}
_GODOT_TEXT_EXTENSIONS = {'.gd', '.tscn', '.tres', '.svg', '.json', '.md', '.txt'}
_GODOT_EDITABLE_ROOTS = {'scripts', 'scenes', 'assets', 'tests', 'docs'}
_GODOT_RESTORE_EXACT = {
    'project.godot', 'export_presets.cfg', 'README.md', 'SETUP_REQUIRED.txt',
    'THIRD_PARTY_NOTICES.md', '.gitignore',
}


def _safe(path: str) -> PurePosixPath:
    if not isinstance(path, str) or not path or '\\' in path or path.startswith('/') or len(path) > 220:
        raise EngineError('Project path invalid')
    parsed = PurePosixPath(path)
    if any(part in ('', '.', '..') for part in parsed.parts):
        raise EngineError('Project path traversal rejected')
    return parsed


def infer(paths) -> EngineProfile:
    values = set()
    for value in paths:
        parsed = _safe(value)
        values.add(parsed.as_posix())
    specialized = [profile for profile in (FLUTTER, GODOT) if profile.marker in values]
    if len(specialized) > 1:
        raise EngineError('Ambiguous project engine markers')
    if specialized:
        return specialized[0]
    return GENERIC


def editable(path: str, engine: str) -> bool:
    try:
        parsed = _safe(path)
    except EngineError:
        return False
    if engine == 'flutter':
        parts = parsed.parts
        return (path in ('pubspec.yaml', 'analysis_options.yaml') or
                (parts[0] in ('lib', 'test') and path.endswith('.dart')) or
                (parts[0] == 'assets' and path.endswith(('.svg', '.json'))) or
                (parts[0] == 'docs' and path.endswith('.md')))
    if engine == 'godot':
        if path in _GODOT_ROOT_EDITABLE:
            return True
        if len(parsed.parts) < 2 or parsed.parts[0] not in _GODOT_EDITABLE_ROOTS:
            return False
        return parsed.suffix.lower() in _GODOT_TEXT_EXTENSIONS
    if engine == 'generic':
        from generic_policy import editable as generic_editable
        return generic_editable(path)
    raise EngineError('Unsupported project engine')


def restorable(path: str, engine: str) -> bool:
    try:
        parsed = _safe(path)
    except EngineError:
        return False
    if engine == 'flutter':
        return editable(path, engine) or path in {'pubspec.lock', 'PROJECT_CONTEXT.md', '.studio/state.json'}
    if engine == 'godot':
        if path in _GODOT_RESTORE_EXACT or path in {'PROJECT_CONTEXT.md', '.studio/state.json'}:
            return True
        if parsed.parts and parsed.parts[0] in _GODOT_EDITABLE_ROOTS:
            return parsed.suffix.lower() in _GODOT_TEXT_EXTENSIONS
        return False
    if engine == 'generic':
        from generic_policy import editable as generic_editable
        return generic_editable(path) or path in {'PROJECT_CONTEXT.md', '.studio/state.json'}
    raise EngineError('Unsupported project engine')


def profile(name: str) -> EngineProfile:
    try:
        return PROFILES[name]
    except (KeyError, TypeError):
        raise EngineError('Unsupported project engine') from None
