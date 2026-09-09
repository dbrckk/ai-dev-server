"""Materialize, execute and score validated evolution candidates in isolation.

Candidate Python/tests run only in the pinned Flutter container with networking
removed, a read-only workspace, dropped Linux capabilities and no production
credentials. Trusted host-side code creates detached worktrees, runs the protected
factory smoke on baseline and candidate with a scrubbed environment, and feeds the
resulting machine evidence to the deterministic promotion evaluator. This module
never pushes or merges candidate code.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

from core import IMAGE, canonical
from evolution_benchmark import evaluate as evaluate_promotion
from evolution_candidate import PROTECTED_PATHS
from evolution_differential import evaluate as evaluate_differential


class IsolatedRunError(RuntimeError):
    pass

SAFE_ENV = {
    'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
    'HOME': '/tmp/home',
    'LANG': 'C.UTF-8',
    'LC_ALL': 'C.UTF-8',
    'PYTHONDONTWRITEBYTECODE': '1',
    'PYTHONUNBUFFERED': '1',
}


def _run(args: list[str], *, cwd: Path | None = None, timeout: int = 300,
         env: dict[str, str] | None = None, check: bool = False) -> subprocess.CompletedProcess:
    result = subprocess.run(args, cwd=cwd, env=env, text=True, capture_output=True, timeout=timeout)
    if check and result.returncode:
        raise IsolatedRunError('Trusted command failed: ' + args[0])
    return result


def _sha(value: object, label: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r'[0-9a-f]{40}', value):
        raise IsolatedRunError(label + ' SHA invalid')
    return value


def _test_path(validated_candidate: dict) -> str:
    paths = [item.get('path') for item in validated_candidate.get('files', [])
             if isinstance(item, dict) and isinstance(item.get('path'), str)
             and item['path'].startswith('tests/test_')]
    if len(paths) != 1:
        raise IsolatedRunError('Validated candidate must contain exactly one primary test file')
    return paths[0]


def _materialize_candidate(root: Path, validated_candidate: dict) -> None:
    for item in validated_candidate.get('files', []):
        if not isinstance(item, dict) or set(item) != {'path', 'content'}:
            raise IsolatedRunError('Validated candidate files malformed')
        target = root / item['path']
        if not target.resolve().is_relative_to(root.resolve()):
            raise IsolatedRunError('Candidate path escaped worktree')
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(item['content'])


def _protected_hashes(root: Path) -> dict[str, str]:
    result = {}
    for path in sorted(PROTECTED_PATHS):
        file = root / path
        if file.is_file():
            result[path] = hashlib.sha256(file.read_bytes()).hexdigest()
    if not result:
        raise IsolatedRunError('Protected factory files missing from worktree')
    return result


def _docker_python(root: Path, python_args: list[str], timeout: int = 300) -> subprocess.CompletedProcess:
    if shutil.which('docker') is None:
        raise IsolatedRunError('Docker unavailable for candidate isolation')
    command = [
        'docker', 'run', '--rm', '--network', 'none', '--read-only',
        '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges',
        '--pids-limit', '128', '--memory', '1024m', '--cpus', '2',
        '--tmpfs', '/tmp:rw,noexec,nosuid,size=256m',
        '-e', 'HOME=/tmp/home', '-e', 'LANG=C.UTF-8', '-e', 'LC_ALL=C.UTF-8',
        '-e', 'PYTHONDONTWRITEBYTECODE=1', '-e', 'PYTHONUNBUFFERED=1',
        '-v', str(root.resolve()) + ':/workspace:ro', '-w', '/workspace',
        IMAGE, 'python3', *python_args,
    ]
    return _run(command, timeout=timeout, env=SAFE_ENV)


def _trusted_flutter_smoke(root: Path, smoke_root: Path, timeout: int = 900) -> bool:
    if smoke_root.exists():
        raise IsolatedRunError('Smoke root already exists')
    env = dict(SAFE_ENV)
    env['STUDIO_SMOKE_ROOT'] = str(smoke_root)
    result = _run(['python3', 'studio/smoke.py'], cwd=root, timeout=timeout, env=env)
    return result.returncode == 0


def _parse_unittest(output: str, returncode: int) -> dict:
    match = re.search(r'Ran\s+(\d+)\s+tests?', output)
    count = int(match.group(1)) if match else 0
    failures = 0
    errors = 0
    failed = re.search(r'FAILED\s*\(([^)]*)\)', output)
    if failed:
        for key, value in re.findall(r'(failures|errors)=(\d+)', failed.group(1)):
            if key == 'failures':
                failures = int(value)
            elif key == 'errors':
                errors = int(value)
    passed = returncode == 0 and count > 0 and failures == 0 and errors == 0
    return {'passed': passed, 'count': count, 'failures': failures, 'errors': errors}


def _candidate_test_result(root: Path, commit_sha: str, test_file: str) -> dict:
    pattern = Path(test_file).name
    result = _docker_python(root, ['-m', 'unittest', 'discover', '-s', 'tests', '-p', pattern, '-v'])
    parsed = _parse_unittest((result.stdout or '') + '\n' + (result.stderr or ''), result.returncode)
    return {
        'commit_sha': commit_sha,
        'test_file': test_file,
        'tests_collected': parsed['count'],
        'failures': parsed['failures'],
        'errors': parsed['errors'],
        'passed': parsed['passed'],
    }


def _copy_test_into_baseline(candidate_root: Path, baseline_root: Path, test_file: str) -> None:
    source = candidate_root / test_file
    if not source.is_file():
        raise IsolatedRunError('Candidate differential test missing')
    target = baseline_root / test_file
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(source.read_bytes())


def _commit_candidate(candidate_root: Path, baseline_sha: str, paths: list[str]) -> str:
    _run(['git', 'add', '--', *paths], cwd=candidate_root, check=True)
    env = dict(SAFE_ENV)
    env['GIT_AUTHOR_NAME'] = env['GIT_COMMITTER_NAME'] = 'ai-dev-server evolution'
    env['GIT_AUTHOR_EMAIL'] = env['GIT_COMMITTER_EMAIL'] = 'evolution@localhost'
    _run(['git', 'commit', '--no-gpg-sign', '-m', 'Validated autonomous evolution candidate'],
         cwd=candidate_root, env=env, check=True)
    sha = _run(['git', 'rev-parse', 'HEAD'], cwd=candidate_root, check=True).stdout.strip()
    if sha == baseline_sha:
        raise IsolatedRunError('Candidate commit did not advance baseline')
    return _sha(sha, 'Candidate')


def _is_reversible(candidate_root: Path, baseline_sha: str) -> bool:
    parent = _run(['git', 'rev-parse', 'HEAD^'], cwd=candidate_root).stdout.strip()
    return parent == baseline_sha


def _capability_result(gap: str, assertions: int, passed: bool) -> dict:
    if type(assertions) is not int or assertions < 1:
        raise IsolatedRunError('Validated candidate benchmark assertion count missing')
    return {
        'gap': gap,
        'passed': passed,
        'assertions_total': assertions,
        'assertions_passed': assertions if passed else 0,
    }


def execute(repo_root: Path, work_order: dict, validated_candidate: dict, out: Path) -> dict:
    baseline_sha = _sha(work_order.get('baseline_sha'), 'Baseline')
    if (validated_candidate.get('status') != 'candidate_validated'
            or validated_candidate.get('candidate_id') != work_order.get('candidate_id')):
        raise IsolatedRunError('Validated candidate identity mismatch')
    gap = validated_candidate.get('gap')
    if not isinstance(gap, str) or gap != (work_order.get('primary_gap') or {}).get('value'):
        raise IsolatedRunError('Validated candidate gap mismatch')
    assertions = validated_candidate.get('benchmark_assertions')
    if validated_candidate.get('differential_tests') != assertions:
        raise IsolatedRunError('Candidate benchmark/test cardinality mismatch')
    if _run(['git', 'cat-file', '-e', baseline_sha + '^{commit}'], cwd=repo_root).returncode:
        raise IsolatedRunError('Pinned baseline commit unavailable locally')

    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='evolution-run-') as tmp:
        temp = Path(tmp)
        baseline_root = temp / 'baseline'
        candidate_root = temp / 'candidate'
        _run(['git', 'worktree', 'add', '--detach', str(baseline_root), baseline_sha], cwd=repo_root, check=True)
        try:
            _run(['git', 'worktree', 'add', '--detach', str(candidate_root), baseline_sha], cwd=repo_root, check=True)
            try:
                _materialize_candidate(candidate_root, validated_candidate)
                paths = [item['path'] for item in validated_candidate['files']]
                candidate_sha = _commit_candidate(candidate_root, baseline_sha, paths)
                reversible = _is_reversible(candidate_root, baseline_sha)
                test_file = _test_path(validated_candidate)
                _copy_test_into_baseline(candidate_root, baseline_root, test_file)

                baseline_diff = _candidate_test_result(baseline_root, baseline_sha, test_file)
                candidate_diff = _candidate_test_result(candidate_root, candidate_sha, test_file)
                differential = evaluate_differential(work_order, validated_candidate, baseline_diff, candidate_diff)
                capability_passed = bool(differential.get('improvement_proved'))

                baseline_tests_raw = _docker_python(baseline_root, ['-m', 'unittest', 'discover', '-s', 'tests', '-v'])
                candidate_tests_raw = _docker_python(candidate_root, ['-m', 'unittest', 'discover', '-s', 'tests', '-v'])
                baseline_tests = _parse_unittest((baseline_tests_raw.stdout or '') + '\n' + (baseline_tests_raw.stderr or ''), baseline_tests_raw.returncode)
                candidate_tests = _parse_unittest((candidate_tests_raw.stdout or '') + '\n' + (candidate_tests_raw.stderr or ''), candidate_tests_raw.returncode)

                baseline_compile = _docker_python(baseline_root, ['-m', 'compileall', '-q', 'studio', 'tests']).returncode == 0
                candidate_compile = _docker_python(candidate_root, ['-m', 'compileall', '-q', 'studio', 'tests']).returncode == 0
                baseline_smoke = _trusted_flutter_smoke(baseline_root, temp / 'baseline-smoke')
                candidate_smoke = _trusted_flutter_smoke(candidate_root, temp / 'candidate-smoke')
                baseline_hashes = _protected_hashes(baseline_root)
                candidate_hashes = _protected_hashes(candidate_root)

                baseline_result = {
                    'version': 1,
                    'commit_sha': baseline_sha,
                    'compile_passed': baseline_compile,
                    'unit_tests': baseline_tests,
                    'flutter_smoke_passed': baseline_smoke,
                    'protected_hashes': baseline_hashes,
                    'capability_benchmark': _capability_result(gap, assertions, False),
                    'reversible': True,
                }
                candidate_result = {
                    'version': 1,
                    'commit_sha': candidate_sha,
                    'compile_passed': candidate_compile,
                    'unit_tests': candidate_tests,
                    'flutter_smoke_passed': candidate_smoke,
                    'protected_hashes': candidate_hashes,
                    'capability_benchmark': _capability_result(gap, assertions, capability_passed),
                    'reversible': reversible,
                }
                promotion = evaluate_promotion(work_order, baseline_result, candidate_result, differential)

                evidence = {
                    'version': 2,
                    'status': 'isolated_benchmark_complete',
                    'candidate_id': work_order.get('candidate_id'),
                    'baseline_sha': baseline_sha,
                    'candidate_sha': candidate_sha,
                    'network': 'disabled_for_candidate_code',
                    'candidate_workspace': 'read_only',
                    'candidate_capabilities': 'dropped',
                    'credentials_exposed_to_candidate': False,
                    'baseline': baseline_result,
                    'candidate': candidate_result,
                    'differential': differential,
                    'promotion': promotion,
                }
                (out / 'evolution-isolated-benchmark.json').write_text(canonical(evidence) + '\n')
                (out / 'evolution-promotion.json').write_text(canonical(promotion) + '\n')
                return evidence
            finally:
                _run(['git', 'worktree', 'remove', '--force', str(candidate_root)], cwd=repo_root)
        finally:
            _run(['git', 'worktree', 'remove', '--force', str(baseline_root)], cwd=repo_root)
