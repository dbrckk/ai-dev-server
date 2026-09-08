"""Fail-closed promotion decision for autonomous factory evolution candidates.

This module does not merge branches or execute candidate code. It validates trusted
benchmark/regression evidence and emits a deterministic promote/reject decision.
"""
from __future__ import annotations

import json
from pathlib import Path
import re

SHA_RE = re.compile(r'^[0-9a-f]{40}$')
PROTECTED_PATHS = {
    'studio/core.py',
    'studio/completion.py',
    'studio/security_audit.py',
    'studio/adaptation.py',
    'studio/evolution_executor.py',
    'studio/evolution_evidence.py',
    'studio/evolution_research.py',
    'studio/evolution_promotion.py',
    '.github/workflows/validate.yml',
    '.github/workflows/studio-smoke.yml',
}
REQUIRED_GATES = {
    'trusted_unit_tests_pass',
    'existing_regression_suite_non_regressing',
    'real_flutter_smoke_passes',
    'security_boundaries_not_weakened',
    'definition_of_done_not_weakened',
    'candidate_is_reversible',
}


def _valid_sha(value: object) -> bool:
    return isinstance(value, str) and bool(SHA_RE.fullmatch(value))


def _validate_changed_files(value: object) -> tuple[list[dict], list[str]]:
    blockers: list[str] = []
    if not isinstance(value, list) or not value:
        return [], ['candidate_changed_files_missing']
    normalized: list[dict] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, dict) or set(item) != {'path', 'status'}:
            blockers.append('candidate_changed_file_schema_invalid')
            continue
        path, status = item.get('path'), item.get('status')
        if not isinstance(path, str) or not path or path.startswith('/') or '..' in Path(path).parts:
            blockers.append('candidate_changed_path_invalid')
            continue
        if path in seen:
            blockers.append('candidate_changed_path_duplicate')
            continue
        seen.add(path)
        if status not in ('added', 'modified'):
            blockers.append('candidate_deletes_or_renames_files')
        if path in PROTECTED_PATHS:
            blockers.append('candidate_modifies_protected_factory_gate')
        if path.startswith('tests/') and status != 'added':
            blockers.append('candidate_modifies_existing_test')
        normalized.append({'path': path, 'status': status})
    return normalized, sorted(set(blockers))


def decide(work_order: dict, research: dict, evaluation: dict) -> dict:
    blockers: list[str] = []
    candidate_id = work_order.get('candidate_id') if isinstance(work_order, dict) else None
    baseline_sha = work_order.get('baseline_sha') if isinstance(work_order, dict) else None
    branch = work_order.get('candidate_branch') if isinstance(work_order, dict) else None

    if not isinstance(candidate_id, str) or not candidate_id:
        blockers.append('candidate_id_missing')
    if not _valid_sha(baseline_sha):
        blockers.append('baseline_sha_invalid')
    if branch != 'evolution/' + str(candidate_id):
        blockers.append('candidate_branch_mismatch')
    expected_gates = set(work_order.get('promotion_gates', [])) if isinstance(work_order, dict) else set()
    if not REQUIRED_GATES.issubset(expected_gates):
        blockers.append('work_order_promotion_gates_weakened')

    if not isinstance(research, dict) or research.get('status') != 'research_complete' or research.get('candidate_id') != candidate_id:
        blockers.append('trusted_research_incomplete')

    if not isinstance(evaluation, dict) or evaluation.get('version') != 1:
        blockers.append('candidate_evaluation_invalid')
        evaluation = {}
    if evaluation.get('candidate_id') != candidate_id:
        blockers.append('candidate_evaluation_mismatch')
    candidate_sha = evaluation.get('candidate_sha')
    if not _valid_sha(candidate_sha) or candidate_sha == baseline_sha:
        blockers.append('candidate_sha_invalid')
    if evaluation.get('baseline_sha') != baseline_sha:
        blockers.append('candidate_baseline_mismatch')

    changed, changed_blockers = _validate_changed_files(evaluation.get('changed_files'))
    blockers.extend(changed_blockers)

    tests = evaluation.get('tests')
    if not isinstance(tests, dict):
        blockers.append('candidate_test_evidence_missing')
    else:
        required = {'baseline_passed', 'candidate_passed', 'candidate_failed', 'new_trusted_tests'}
        if set(tests) != required or any(not isinstance(tests.get(k), int) or tests[k] < 0 for k in required):
            blockers.append('candidate_test_evidence_invalid')
        else:
            if tests['candidate_failed'] != 0:
                blockers.append('candidate_tests_failed')
            if tests['candidate_passed'] < tests['baseline_passed']:
                blockers.append('candidate_regression_detected')
            if tests['new_trusted_tests'] < 1:
                blockers.append('candidate_adds_no_trusted_tests')

    benchmark = evaluation.get('benchmark')
    if not isinstance(benchmark, dict) or set(benchmark) != {'baseline_supports_gap', 'candidate_supports_gap', 'passed'}:
        blockers.append('capability_benchmark_missing')
    elif benchmark.get('baseline_supports_gap') is not False or benchmark.get('candidate_supports_gap') is not True or benchmark.get('passed') is not True:
        blockers.append('capability_benchmark_not_improved')

    gates = evaluation.get('gates')
    if not isinstance(gates, dict) or set(gates) != REQUIRED_GATES:
        blockers.append('candidate_gate_evidence_incomplete')
    elif any(gates.get(name) is not True for name in REQUIRED_GATES):
        blockers.append('candidate_gate_failed')

    security = evaluation.get('security')
    if not isinstance(security, dict) or set(security) != {'passed', 'new_high_findings'}:
        blockers.append('candidate_security_evidence_missing')
    elif security.get('passed') is not True or security.get('new_high_findings') != 0:
        blockers.append('candidate_security_regression')

    registry = evaluation.get('registry_change')
    if not isinstance(registry, dict) or set(registry) != {'addition_only', 'stage_name'}:
        blockers.append('registry_change_evidence_missing')
    else:
        resume = work_order.get('resume_stage') if isinstance(work_order, dict) else None
        if registry.get('addition_only') is not True or registry.get('stage_name') != resume:
            blockers.append('registry_change_not_additive_for_gap')

    blockers = sorted(set(blockers))
    return {
        'version': 1,
        'candidate_id': candidate_id,
        'baseline_sha': baseline_sha,
        'candidate_sha': candidate_sha,
        'decision': 'promote' if not blockers else 'reject',
        'changed_files': changed,
        'blockers': blockers,
    }


def evaluate_files(work_order_path: Path, research_path: Path, evaluation_path: Path, out: Path) -> dict:
    work_order = json.loads(work_order_path.read_text())
    research = json.loads(research_path.read_text())
    evaluation = json.loads(evaluation_path.read_text())
    decision = decide(work_order, research, evaluation)
    out.mkdir(parents=True, exist_ok=True)
    (out / 'evolution-promotion.json').write_text(json.dumps(decision, sort_keys=True, indent=2) + '\n')
    return decision
