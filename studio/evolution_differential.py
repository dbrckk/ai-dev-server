"""Validate baseline-red/candidate-green proof for self-evolution."""
from __future__ import annotations
import re

class DifferentialRejected(ValueError):
    pass

def _sha(value, label):
    if not isinstance(value, str) or not re.fullmatch(r'[0-9a-f]{40}', value):
        raise DifferentialRejected(label + ' SHA invalid')
    return value

def _result(value, label):
    required = {'commit_sha','test_file','tests_collected','failures','errors','passed'}
    if not isinstance(value, dict) or set(value) != required:
        raise DifferentialRejected(label + ' differential evidence malformed')
    out = dict(value); out['commit_sha'] = _sha(value.get('commit_sha'), label)
    if not isinstance(value.get('test_file'), str) or not re.fullmatch(r'tests/test_[a-z0-9_]+\.py', value['test_file']):
        raise DifferentialRejected(label + ' test path invalid')
    for key in ('tests_collected','failures','errors'):
        if not isinstance(value.get(key), int) or value[key] < 0:
            raise DifferentialRejected(label + ' test counts invalid')
    if value['tests_collected'] < 1 or not isinstance(value.get('passed'), bool):
        raise DifferentialRejected(label + ' differential result invalid')
    if value['failures'] + value['errors'] > value['tests_collected']:
        raise DifferentialRejected(label + ' failed test count exceeds collection')
    if value['passed'] != (value['failures'] == 0 and value['errors'] == 0):
        raise DifferentialRejected(label + ' pass flag inconsistent')
    return out

def evaluate(work_order, validated_candidate, baseline, candidate):
    if not isinstance(work_order, dict) or work_order.get('status') != 'candidate_planned':
        raise DifferentialRejected('Differential proof requires planned work order')
    if not isinstance(validated_candidate, dict) or validated_candidate.get('status') != 'candidate_validated':
        raise DifferentialRejected('Differential proof requires validated candidate')
    if validated_candidate.get('candidate_id') != work_order.get('candidate_id'):
        raise DifferentialRejected('Candidate identity mismatch')
    baseline_sha = _sha(work_order.get('baseline_sha'), 'Baseline')
    tests = [f.get('path') for f in validated_candidate.get('files', []) if isinstance(f, dict) and isinstance(f.get('path'), str) and f['path'].startswith('tests/test_')]
    if len(tests) != 1:
        raise DifferentialRejected('Candidate must contain exactly one primary differential test')
    expected = tests[0]
    baseline = _result(baseline, 'Baseline'); candidate = _result(candidate, 'Candidate')
    if baseline['commit_sha'] != baseline_sha:
        raise DifferentialRejected('Baseline evidence does not match pinned SHA')
    if candidate['commit_sha'] == baseline_sha:
        raise DifferentialRejected('Candidate evidence points to baseline')
    if baseline['test_file'] != expected or candidate['test_file'] != expected:
        raise DifferentialRejected('Differential evidence test file mismatch')
    if baseline['tests_collected'] != candidate['tests_collected']:
        raise DifferentialRejected('Differential test collection changed between baseline and candidate')
    baseline_failed_all = (
        not baseline['passed']
        and baseline['failures'] + baseline['errors'] == baseline['tests_collected']
    )
    candidate_passed = candidate['passed']
    improved = baseline_failed_all and candidate_passed
    blockers = []
    if not baseline_failed_all:
        blockers.append('not_every_candidate_test_failed_on_baseline')
    if not candidate_passed:
        blockers.append('candidate_test_did_not_pass_on_candidate')
    return {
        'version':1,
        'status':'differential_proved' if improved else 'differential_rejected',
        'candidate_id':work_order.get('candidate_id'),
        'baseline_sha':baseline_sha,
        'candidate_sha':candidate['commit_sha'],
        'test_file':expected,
        'tests_collected':candidate['tests_collected'],
        'baseline_failed_all':baseline_failed_all,
        'candidate_passed':candidate_passed,
        'improvement_proved':improved,
        'blockers':blockers,
    }
