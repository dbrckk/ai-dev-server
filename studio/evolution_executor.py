"""Consume an evolution request into a safe, machine-readable candidate work order.

This module does not execute discovered code or weaken gates. It turns a trusted
adaptation request into the next bounded factory-evolution job.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

SUPPORTED_RESOURCE_KINDS = {
    'official_docs',
    'sdk_tool',
    'package_registry',
    'github_source',
    'device_runtime',
}

REQUIRED_PROMOTION_GATES = {
    'trusted_unit_tests_pass',
    'existing_regression_suite_non_regressing',
    'real_flutter_smoke_passes',
    'security_boundaries_not_weakened',
    'definition_of_done_not_weakened',
    'candidate_is_reversible',
}


def _slug(value: str) -> str:
    cleaned = re.sub(r'[^a-z0-9]+', '-', value.lower()).strip('-')
    if not cleaned:
        raise ValueError('Evolution gap cannot produce a candidate slug')
    return cleaned[:48]


def validate_request(request: dict) -> dict:
    if not isinstance(request, dict) or request.get('version') != 1:
        raise ValueError('Unsupported evolution request version')
    if request.get('status') != 'adaptation_required':
        raise ValueError('Evolution executor requires adaptation_required')
    gaps = request.get('gaps')
    resources = request.get('resource_research')
    gates = request.get('promotion_gates')
    policy = request.get('candidate_policy')
    if not isinstance(gaps, list) or not gaps:
        raise ValueError('Evolution request has no gaps')
    if not isinstance(resources, list):
        raise ValueError('Evolution request resources must be a list')
    if not isinstance(gates, list) or not REQUIRED_PROMOTION_GATES.issubset(set(gates)):
        raise ValueError('Evolution request weakens mandatory promotion gates')
    if not isinstance(policy, dict):
        raise ValueError('Evolution request candidate policy missing')
    if policy.get('isolation') != 'dedicated_branch':
        raise ValueError('Evolution candidates must use dedicated branches')
    if policy.get('external_code_execution') != 'forbidden_until_reviewed_and_pinned':
        raise ValueError('Evolution request weakens external-code policy')
    if policy.get('promotion') != 'only_after_all_gates_pass' or policy.get('rollback') != 'required':
        raise ValueError('Evolution request weakens promotion/rollback policy')

    for gap in gaps:
        if not isinstance(gap, dict) or set(gap) != {'kind', 'value', 'reason'}:
            raise ValueError('Malformed evolution gap')
        if any(not isinstance(gap[k], str) or not gap[k].strip() for k in ('kind', 'value', 'reason')):
            raise ValueError('Malformed evolution gap value')
    for resource in resources:
        if not isinstance(resource, dict) or set(resource) != {'kind', 'query'}:
            raise ValueError('Malformed evolution resource')
        if resource.get('kind') not in SUPPORTED_RESOURCE_KINDS:
            raise ValueError('Unsupported evolution resource kind')
        if not isinstance(resource.get('query'), str) or not resource['query'].strip():
            raise ValueError('Empty evolution research query')
    return request


def build_work_order(request: dict, baseline_sha: str) -> dict:
    request = validate_request(request)
    if not isinstance(baseline_sha, str) or not re.fullmatch(r'[0-9a-f]{40}', baseline_sha):
        raise ValueError('Baseline SHA must be a full Git commit SHA')

    primary = request['gaps'][0]
    gap_value = primary['value']
    slug = _slug(gap_value)
    digest = hashlib.sha256(json.dumps(request, sort_keys=True, separators=(',', ':')).encode()).hexdigest()[:12]
    candidate_id = f'{slug}-{digest}'

    research = []
    for index, resource in enumerate(request['resource_research']):
        research.append({
            'id': f'research-{index + 1}',
            'kind': resource['kind'],
            'query': resource['query'],
            'requirements': [
                'record_source_url_or_identifier',
                'record_version_or_revision_when_applicable',
                'record_license_when_applicable',
                'record_maintenance_signal',
                'record_security_or_compatibility_risks',
                'do_not_execute_discovered_code',
            ],
        })

    return {
        'version': 1,
        'status': 'candidate_planned',
        'candidate_id': candidate_id,
        'candidate_branch': 'evolution/' + candidate_id,
        'baseline_sha': baseline_sha,
        'primary_gap': primary,
        'all_gaps': request['gaps'],
        'resume_stage': request.get('next_stage'),
        'research_tasks': research,
        'implementation_contract': {
            'must_add_trusted_tests': True,
            'must_add_capability_benchmark': True,
            'external_code_execution_before_review': False,
            'may_modify_definition_of_done_to_pass': False,
            'may_remove_existing_tests': False,
            'may_reduce_security_boundaries': False,
        },
        'promotion_gates': list(request['promotion_gates']),
        'promotion_decision': 'pending',
        'rollback': {
            'required': True,
            'baseline_sha': baseline_sha,
        },
    }


def consume(request_path: Path, out: Path, baseline_sha: str) -> dict:
    request = json.loads(request_path.read_text())
    work_order = build_work_order(request, baseline_sha)
    out.mkdir(parents=True, exist_ok=True)
    path = out / 'evolution-work-order.json'
    path.write_text(json.dumps(work_order, ensure_ascii=False, sort_keys=True, indent=2) + '\n')
    return work_order
