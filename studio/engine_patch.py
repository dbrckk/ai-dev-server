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
    # Exact-match edits are deliberately Godot-implementation only. A small
    # replacement avoids asking a free model to echo a whole existing script.
    # This validates the envelope; the runner must verify the unique match
    # against the trusted on-disk source before constructing full-file patches.
    if isinstance(value, dict) and set(value) == {'edits'}:
        if engine != 'godot' or role != 'implementation':
            raise PatchPolicyError('Exact edits permitted only for Godot implementation')
        edits = value['edits']
        if not isinstance(edits, list) or not 1 <= len(edits) <= 12:
            raise PatchPolicyError('Exact edit count invalid')
        seen = set()
        total = 0
        normalized = []
        for item in edits:
            if not isinstance(item, dict) or set(item) != {'path', 'find', 'replace'}:
                raise PatchPolicyError('Exact edit entry malformed')
            path, find, replacement = item['path'], item['find'], item['replace']
            if not isinstance(path, str) or not editable(path, engine):
                raise PatchPolicyError('Exact edit path outside Godot scope')
            if path in seen or not isinstance(find, str) or not isinstance(replacement, str):
                raise PatchPolicyError('Duplicate path or invalid exact edit')
            if not find or find == replacement or '\\x00' in find or '\\x00' in replacement:
                raise PatchPolicyError('Empty, unchanged or invalid exact edit')
            size = len(find.encode('utf-8')) + len(replacement.encode('utf-8'))
            if size > 24_000 or SECRET.search(find) or SECRET.search(replacement):
                raise PatchPolicyError('Exact edit too large or contains credential-like material')
            total += size
            if total > 48_000:
                raise PatchPolicyError('Exact edit payload too large')
            seen.add(path)
            normalized.append({'path': path, 'find': find, 'replace': replacement})
        return normalized
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
