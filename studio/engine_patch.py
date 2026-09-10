"""Trusted engine-aware validation for model-generated source patches."""
from __future__ import annotations

import re

from project_engine import editable, profile

MAX_FILES = 60
MAX_TOTAL_BYTES = 600_000
SECRET = re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----|github_pat_[A-Za-z0-9_]+|gh[pousr]_[A-Za-z0-9]+|nvapi-[A-Za-z0-9_-]{15,}|sk-[A-Za-z0-9_-]{20,}')


class PatchPolicyError(ValueError):
    pass


def validate(value: dict, engine: str, role: str = 'implementation') -> list[dict]:
    profile(engine)
    if role not in ('implementation', 'tests'):
        raise PatchPolicyError('Unsupported patch role')
    if not isinstance(value, dict) or set(value) != {'files'} or not isinstance(value['files'], list):
        raise PatchPolicyError('Expected patch envelope')
    if not 1 <= len(value['files']) <= MAX_FILES:
        raise PatchPolicyError('Patch file count invalid')
    seen = set(); total = 0; normalized = []
    for item in value['files']:
        if not isinstance(item, dict) or set(item) != {'path', 'content'}:
            raise PatchPolicyError('Patch file entry malformed')
        path = item.get('path'); content = item.get('content')
        if not isinstance(path, str) or not editable(path, engine):
            raise PatchPolicyError('Patch path outside engine editable scope')
        if path in seen or not isinstance(content, str) or '\x00' in content:
            raise PatchPolicyError('Duplicate path or invalid content')
        if role == 'tests':
            if engine == 'flutter' and not (path.startswith('test/') and path.endswith('_test.dart')):
                raise PatchPolicyError('Flutter QA may only write test/*_test.dart')
            if engine == 'godot' and not (path.startswith('tests/') and path.endswith('.gd')):
                raise PatchPolicyError('Godot QA may only write tests/*.gd')
        size = len(content.encode())
        if size == 0:
            raise PatchPolicyError('Patch file may not be empty')
        total += size
        if total > MAX_TOTAL_BYTES or SECRET.search(content):
            raise PatchPolicyError('Patch too large or contains credential-like material')
        seen.add(path); normalized.append({'path': path, 'content': content})
    return normalized
