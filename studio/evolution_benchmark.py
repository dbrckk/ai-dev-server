"""Deterministic promotion evaluator for factory-evolution candidates.

This module does not run candidate code. It evaluates trusted execution evidence
produced by the later isolated benchmark runner and refuses promotion on any
regression, protected-file drift, missing capability benchmark, or weakened gate.
"""
from __future__ import annotations

import re

REQUIRED_RESULT_KEYS = {
    'version', 'commit_sha', 'compile_passed', 'unit_tests', 'flutter_smoke_passed',
    'protected_hashes', 'capability_benchmark', 'reversible',
}


class BenchmarkRejected(ValueError):
    pass


def _sha(value: object, label: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r'[0-9a-f]{40}', value):
        raise BenchmarkRejected(label + ' commit SHA invalid')
    return value


def _hash_map(value: object) -> dict[str, str]:
    if not isinstance(value, dict) or not value:
        raise BenchmarkRejected('Protected hash evidence missing')
    normalized = {}
    for path, digest in value.items():
        if not isinstance(path, str) or not path or not isinstance(digest, str) or not re.fullmatch(r'[0-9a-f]{64}', digest):
            raise BenchmarkRejected('Protected hash evidence invalid')
        normalized[path] = digest
    return normalized


def _test_result(value: object) -> dict:
    if not isinstance(value, dict) or set(value) != {'passed', 'count', 'failures', 'errors'}:
        raise BenchmarkRejected('Unit-test evidence malformed')
    if not isinstance(value['passed'], bool):
        raise BenchmarkRejected('Unit-test pass flag invalid')
    for key in ('count', 'failures', 'errors'):
        if not isinstance(value[key], int) or value[key] < 0:
            raise BenchmarkRejected('Unit-test count invalid')
    if value['passed'] != (value['failures'] == 0 and value['errors'] == 0):
        raise BenchmarkRejected('Unit-test evidence inconsistent')
    return dict(value)


def _capability(value: object, expected_gap: str) -> dict:
    if not isinstance(value, dict) or set(value) != {'gap', 'passed', 'assertions_total', 'assertions_passed'}:
        raise BenchmarkRejected('Capability benchmark evidence malformed')
    if value.get('gap') != expected_gap or not isinstance(value.get('passed'), bool):
        raise BenchmarkRejected('Capability benchmark identity invalid')
    for key in ('assertions_total', 'assertions_passed'):
        if not isinstance(value[key], int) or value[key] < 0:
            raise BenchmarkRejected('Capability benchmark count invalid')
    if value['assertions_total'] < 1 or value['assertions_passed'] > value['assertions_total']:
        raise BenchmarkRejected('Capability benchmark assertion counts invalid')
    if value['passed'] != (value['assertions_passed'] == value['assertions_total']):
        raise BenchmarkRejected('Capability benchmark evidence inconsistent')
    return dict(value)


def validate_execution_result(value: dict, expected_gap: str) -> dict:
    if not isinstance(value, dict) or set(value) != REQUIRED_RESULT_KEYS or value.get('version') != 1:
        raise BenchmarkRejected('Benchmark execution result malformed')
    result = dict(value)
    result['commit_sha'] = _sha(value.get('commit_sha'), 'Benchmark')
    if not isinstance(value.get('compile_passed'), bool) or not isinstance(value.get('flutter_smoke_passed'), bool):
        raise BenchmarkRejected('Benchmark boolean gate invalid')
    result['unit_tests'] = _test_result(value.get('unit_tests'))
    result['protected_hashes'] = _hash_map(value.get('protected_hashes'))
    result['capability_benchmark'] = _capability(value.get('capability_benchmark'), expected_gap)
    if not isinstance(value.get('reversible'), bool):
        raise BenchmarkRejected('Reversibility evidence invalid')
    return result


def evaluate(work_order: dict, baseline: dict, candidate: dict) -> dict:
    if not isinstance(work_order, dict) or work_order.get('status') != 'candidate_planned':
        raise BenchmarkRejected('Benchmark requires candidate work order')
    primary = work_order.get('primary_gap')
    gap = primary.get('value') if isinstance(primary, dict) else None
    if not isinstance(gap, str):
        raise BenchmarkRejected('Benchmark gap missing')
    baseline_sha = _sha(work_order.get('baseline_sha'), 'Baseline')
    baseline = validate_execution_result(baseline, gap)
    candidate = validate_execution_result(candidate, gap)
    if baseline['commit_sha'] != baseline_sha:
        raise BenchmarkRejected('Baseline evidence does not match pinned SHA')
    if candidate['commit_sha'] == baseline_sha:
        raise BenchmarkRejected('Candidate evidence points to baseline instead of candidate')

    blockers = []
    gates = {}
    gates['trusted_unit_tests_pass'] = candidate['unit_tests']['passed']
    if not gates['trusted_unit_tests_pass']:
        blockers.append('trusted_unit_tests_failed')
    non_regressing = (
        candidate['unit_tests']['passed']
        and candidate['unit_tests']['count'] >= baseline['unit_tests']['count']
        and candidate['unit_tests']['failures'] <= baseline['unit_tests']['failures']
        and candidate['unit_tests']['errors'] <= baseline['unit_tests']['errors']
    )
    gates['existing_regression_suite_non_regressing'] = non_regressing
    if not non_regressing:
        blockers.append('regression_suite_regressed')
    gates['real_flutter_smoke_passes'] = candidate['flutter_smoke_passed']
    if not gates['real_flutter_smoke_passes']:
        blockers.append('real_flutter_smoke_failed')
    protected_equal = candidate['protected_hashes'] == baseline['protected_hashes']
    gates['security_boundaries_not_weakened'] = protected_equal
    gates['definition_of_done_not_weakened'] = protected_equal
    if not protected_equal:
        blockers.append('protected_factory_contract_changed')
    gates['candidate_is_reversible'] = candidate['reversible']
    if not candidate['reversible']:
        blockers.append('candidate_not_reversible')
    capability_passed = candidate['capability_benchmark']['passed']
    if not capability_passed:
        blockers.append('capability_benchmark_failed')
    required = work_order.get('promotion_gates')
    if not isinstance(required, list) or any(not isinstance(item, str) for item in required):
        raise BenchmarkRejected('Promotion gate contract malformed')
    unknown = [item for item in required if item not in gates]
    if unknown:
        raise BenchmarkRejected('Unknown promotion gate: ' + ','.join(unknown))
    missing_pass = [item for item in required if not gates[item]]
    for item in missing_pass:
        marker = 'promotion_gate_failed:' + item
        if marker not in blockers:
            blockers.append(marker)
    accepted = capability_passed and not blockers
    return {
        'version': 1,
        'status': 'promotion_approved' if accepted else 'promotion_rejected',
        'candidate_id': work_order.get('candidate_id'),
        'baseline_sha': baseline_sha,
        'candidate_sha': candidate['commit_sha'],
        'gap': gap,
        'gates': gates,
        'capability_benchmark_passed': capability_passed,
        'blockers': blockers,
        'promotion_decision': 'approve' if accepted else 'reject',
    }
