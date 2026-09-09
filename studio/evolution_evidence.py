"""Validate research evidence supplied to a factory-evolution work order.

The orchestrating ChatGPT/Work layer or trusted research adapters may gather
external metadata, but only compact allowlisted evidence enters the trusted
factory. Executable code is never accepted as research evidence.
"""
from __future__ import annotations

import re
from urllib.parse import urlsplit

OFFICIAL_HOSTS = {
    'developer.android.com',
    'docs.flutter.dev',
    'developers.google.com',
    'firebase.google.com',
    'support.google.com',
    'developer.apple.com',
}
PACKAGE_HOSTS = {'pub.dev'}
GITHUB_HOSTS = {'github.com'}
DEVICE_IDENTIFIERS = {
    'android-emulator',
    'physical-android-device',
    'play-console-test-track',
}


def _https_host(source: str) -> str:
    parsed = urlsplit(source)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password or parsed.fragment:
        raise ValueError('Research source must be a safe HTTPS URL')
    if parsed.port not in (None, 443):
        raise ValueError('Research source must use standard HTTPS')
    return parsed.hostname.lower()


def validate_evidence(work_order: dict, evidence: dict) -> dict:
    tasks = work_order.get('research_tasks') if isinstance(work_order, dict) else None
    if not isinstance(tasks, list):
        raise ValueError('Work order has no research tasks')
    expected = {task.get('id'): task for task in tasks if isinstance(task, dict) and isinstance(task.get('id'), str)}
    if len(expected) != len(tasks):
        raise ValueError('Work order research task ids invalid')

    if not isinstance(evidence, dict) or set(evidence) != {'version', 'candidate_id', 'items'}:
        raise ValueError('Malformed research evidence envelope')
    version = evidence.get('version')
    if version not in (1, 2) or evidence.get('candidate_id') != work_order.get('candidate_id'):
        raise ValueError('Research evidence does not match candidate')
    items = evidence.get('items')
    if not isinstance(items, list) or len(items) != len(tasks):
        raise ValueError('Research evidence must cover every task exactly once')

    seen = set()
    normalized = []
    for item in items:
        required = {'task_id', 'kind', 'source', 'version_or_revision', 'license', 'maintenance_signal', 'risks', 'notes'}
        if version == 2:
            required.add('content_sha256')
        if not isinstance(item, dict) or set(item) != required:
            raise ValueError('Malformed research evidence item')
        task_id = item.get('task_id')
        task = expected.get(task_id)
        if task is None or task_id in seen:
            raise ValueError('Unknown or duplicate research task evidence')
        seen.add(task_id)
        if item.get('kind') != task.get('kind'):
            raise ValueError('Research evidence kind mismatch')
        for key in ('source', 'version_or_revision', 'license', 'maintenance_signal', 'notes'):
            if not isinstance(item.get(key), str):
                raise ValueError('Research evidence text field invalid')
        risks = item.get('risks')
        if not isinstance(risks, list) or any(not isinstance(risk, str) or not risk.strip() for risk in risks):
            raise ValueError('Research risks invalid')
        if len(item['notes']) > 4000 or any(len(item[key]) > 500 for key in ('source', 'version_or_revision', 'license', 'maintenance_signal')):
            raise ValueError('Research evidence field too large')
        if version == 2 and not re.fullmatch(r'[0-9a-f]{64}', item.get('content_sha256', '')):
            raise ValueError('Research evidence content hash invalid')

        kind = item['kind']
        source = item['source']
        if kind == 'official_docs':
            if _https_host(source) not in OFFICIAL_HOSTS:
                raise ValueError('Official documentation source is not allowlisted')
        elif kind == 'package_registry':
            if _https_host(source) not in PACKAGE_HOSTS:
                raise ValueError('Package registry source is not allowlisted')
        elif kind == 'github_source':
            if _https_host(source) not in GITHUB_HOSTS:
                raise ValueError('GitHub source must use github.com')
        elif kind == 'sdk_tool':
            if _https_host(source) not in OFFICIAL_HOSTS:
                raise ValueError('SDK source is not official')
        elif kind == 'device_runtime':
            if source not in DEVICE_IDENTIFIERS:
                raise ValueError('Unknown device runtime evidence source')
        else:
            raise ValueError('Unsupported research evidence kind')

        normalized.append(dict(item))

    return {
        'version': version,
        'candidate_id': evidence['candidate_id'],
        'status': 'research_complete',
        'items': normalized,
    }
