"""Fail-closed capability-gap detection for autonomous factory evolution.

This module never executes downloaded code. It turns unsupported completion work
into a machine-readable evolution request that can be researched, implemented on
an isolated branch, benchmarked, and either promoted or rejected.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from capability_memory import attach_capability_hints
from project_memory import load as load_project_memory

VERSION = 1

RESOURCE_PLAYBOOK = {
    'billing_qa': [
        {'kind': 'official_docs', 'query': 'Google Play Billing integration and test purchases'},
        {'kind': 'sdk_tool', 'query': 'Play Billing test environment and license testers'},
        {'kind': 'package_registry', 'query': 'Flutter in_app_purchase maintained package and changelog'},
    ],
    'platform_view_qa': [
        {'kind': 'official_docs', 'query': 'Flutter Android platform views testing'},
        {'kind': 'device_runtime', 'query': 'Android emulator platform view rendering and interaction'},
        {'kind': 'package_registry', 'query': 'maintained Flutter platform-view plugin compatibility'},
    ],
    'notification_qa': [
        {'kind': 'official_docs', 'query': 'Android notification permission lifecycle and notification testing'},
        {'kind': 'device_runtime', 'query': 'Android emulator notification foreground background tap validation'},
    ],
    'native_qa': [
        {'kind': 'official_docs', 'query': 'Android runtime permissions and hardware capability testing'},
        {'kind': 'device_runtime', 'query': 'Android emulator native capability validation'},
    ],
    'performance_qa': [
        {'kind': 'official_docs', 'query': 'Flutter performance profiling frame timing jank'},
        {'kind': 'device_runtime', 'query': 'Android frame stats lifecycle soak test'},
    ],
}

DEFAULT_RESOURCES = [
    {'kind': 'official_docs', 'query': 'official platform documentation for the unsupported capability'},
    {'kind': 'package_registry', 'query': 'maintained implementation packages and compatibility metadata'},
    {'kind': 'github_source', 'query': 'well-maintained open-source reference implementations and tests'},
    {'kind': 'device_runtime', 'query': 'runtime environment capable of verifying the feature end to end'},
]

PROMOTION_GATES = [
    'trusted_unit_tests_pass',
    'existing_regression_suite_non_regressing',
    'real_flutter_smoke_passes',
    'security_boundaries_not_weakened',
    'definition_of_done_not_weakened',
    'candidate_is_reversible',
    'differential_improvement_proved',
]


def _clean_strings(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item.strip()]


def build_adaptation_request(report: dict, registered_stages: set[str] | frozenset[str]) -> dict:
    """Describe unsupported work without guessing that it succeeded."""
    completion = report.get('completion', {}) if isinstance(report, dict) else {}
    release = report.get('release_evidence', {}) if isinstance(report, dict) else {}
    capability = release.get('capability_qa', {}) if isinstance(release, dict) else {}
    next_stage = completion.get('next_stage') if isinstance(completion, dict) else None

    gaps: list[dict] = []
    seen: set[tuple[str, str]] = set()

    def add(kind: str, value: str, reason: str) -> None:
        key = (kind, value)
        if key in seen:
            return
        seen.add(key)
        gaps.append({'kind': kind, 'value': value, 'reason': reason})

    if isinstance(completion, dict) and not completion.get('finished') and not next_stage:
        add('invalid_completion_state', 'missing_next_stage',
            'The project is unfinished but the completion contract supplied no next stage.')

    if isinstance(next_stage, str) and next_stage and next_stage not in registered_stages:
        add('missing_stage_executor', next_stage,
            'Completion requires a trusted stage that is not implemented by the current factory.')

    if isinstance(capability, dict):
        for stage in _clean_strings(capability.get('required_qa_stages')):
            if stage not in registered_stages:
                add('missing_stage_executor', stage,
                    'Capability classification requires QA that the current registry cannot execute.')

        mapped_values = {
            item.get('value') for item in capability.get('reasons', [])
            if isinstance(item, dict) and isinstance(item.get('value'), str)
        }
        for permission in _clean_strings(capability.get('permissions')):
            if permission not in mapped_values and permission.startswith('android.permission.'):
                add('unclassified_permission', permission,
                    'The release declares an Android permission with no specialized capability rationale.')

    blockers = _clean_strings(completion.get('blockers') if isinstance(completion, dict) else [])
    for blocker in blockers:
        if blocker.endswith('_missing'):
            stage = blocker[:-8]
            if stage and stage not in registered_stages and stage not in ('release_build',):
                add('missing_completion_executor', stage,
                    'Definition-of-done requires evidence that the current executor set cannot produce.')

    resource_items: list[dict] = []
    resource_seen: set[tuple[str, str]] = set()
    for gap in gaps:
        candidates = RESOURCE_PLAYBOOK.get(gap['value'], DEFAULT_RESOURCES)
        for item in candidates:
            key = (item['kind'], item['query'])
            if key not in resource_seen:
                resource_seen.add(key)
                resource_items.append(dict(item))

    return {
        'version': VERSION,
        'status': 'adaptation_required' if gaps else 'no_adaptation_required',
        'next_stage': next_stage,
        'gaps': gaps,
        'resource_research': resource_items,
        'candidate_policy': {
            'isolation': 'dedicated_branch',
            'external_code_execution': 'forbidden_until_reviewed_and_pinned',
            'promotion': 'only_after_all_gates_pass',
            'rollback': 'required',
        },
        'promotion_gates': list(PROMOTION_GATES),
    }


def write_adaptation_request(report: dict, out: Path, registered_stages: set[str] | frozenset[str]) -> dict:
    request = build_adaptation_request(report, registered_stages)
    if request['status'] != 'adaptation_required':
        return request
    memory_path = out / '.memory' / 'memory.json'
    project_id = os.environ.get('STUDIO_PROJECT_ID')
    if memory_path.is_file() and isinstance(project_id, str) and project_id:
        memory = load_project_memory(memory_path)
        request = attach_capability_hints(request, memory, project_id)
    out.mkdir(parents=True, exist_ok=True)
    path = out / 'evolution-request.json'
    path.write_text(json.dumps(request, ensure_ascii=False, sort_keys=True, indent=2) + '\n')
    return request
