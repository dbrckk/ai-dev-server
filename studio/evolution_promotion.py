"""Trusted application of an already benchmark-approved evolution candidate."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile

from core import canonical
from evolution_benchmark import evaluate as evaluate_promotion
from evolution_candidate import expected_paths

REGISTRY = Path('control/promoted_stages.json')
ROLLBACK_DIR = Path('control/evolution_rollbacks')


class PromotionError(RuntimeError):
    pass


def _sha(value, label):
    if not isinstance(value, str) or not re.fullmatch(r'[0-9a-f]{40}', value):
        raise PromotionError(label + ' SHA invalid')
    return value


def _candidate_digest(candidate):
    files = candidate.get('files')
    if not isinstance(files, list):
        raise PromotionError('Validated candidate files missing')
    payload = {
        'candidate_id': candidate.get('candidate_id'),
        'gap': candidate.get('gap'),
        'files': [
            {'path': item['path'], 'sha256': hashlib.sha256(item['content'].encode()).hexdigest()}
            for item in sorted(files, key=lambda item: item['path'])
        ],
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def _load_registry(root):
    path = root / REGISTRY
    if not path.exists():
        return {'version': 1, 'stages': {}}
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        raise PromotionError('Promoted-stage registry is unreadable') from None
    if not isinstance(value, dict) or value.get('version') != 1 or not isinstance(value.get('stages'), dict):
        raise PromotionError('Promoted-stage registry malformed')
    return value


def _atomic_write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile('w', dir=path.parent, delete=False, encoding='utf-8') as handle:
        handle.write(content)
        temp = Path(handle.name)
    os.replace(temp, path)


def apply(repo_root, work_order, candidate, benchmark, supplied_promotion):
    root = repo_root.resolve()
    if work_order.get('status') != 'candidate_planned':
        raise PromotionError('Promotion requires candidate work order')
    candidate_id = work_order.get('candidate_id')
    gap = (work_order.get('primary_gap') or {}).get('value')
    baseline_sha = _sha(work_order.get('baseline_sha'), 'Baseline')
    if candidate.get('status') != 'candidate_validated' or candidate.get('candidate_id') != candidate_id or candidate.get('gap') != gap:
        raise PromotionError('Validated candidate identity mismatch')
    digest = _candidate_digest(candidate)
    if candidate.get('candidate_sha256') != digest:
        raise PromotionError('Validated candidate digest mismatch')
    if benchmark.get('status') != 'isolated_benchmark_complete' or benchmark.get('candidate_id') != candidate_id or benchmark.get('baseline_sha') != baseline_sha:
        raise PromotionError('Isolated benchmark identity mismatch')
    try:
        recomputed = evaluate_promotion(work_order, benchmark.get('baseline'), benchmark.get('candidate'), benchmark.get('differential'))
    except (TypeError, ValueError) as exc:
        raise PromotionError('Promotion evidence failed deterministic reevaluation') from exc
    if recomputed != supplied_promotion or benchmark.get('promotion') != supplied_promotion:
        raise PromotionError('Promotion decision does not match benchmark evidence')
    if supplied_promotion.get('status') != 'promotion_approved' or supplied_promotion.get('promotion_decision') != 'approve':
        raise PromotionError('Candidate is not approved for promotion')
    candidate_sha = _sha(supplied_promotion.get('candidate_sha'), 'Candidate')
    if supplied_promotion.get('candidate_id') != candidate_id or supplied_promotion.get('baseline_sha') != baseline_sha or supplied_promotion.get('gap') != gap:
        raise PromotionError('Promotion decision identity mismatch')

    expected = expected_paths(gap)
    files = candidate.get('files')
    by_path = {item.get('path'): item.get('content') for item in files if isinstance(item, dict)}
    if set(by_path) != set(expected.values()) or any(not isinstance(content, str) for content in by_path.values()):
        raise PromotionError('Candidate files no longer match validated scope')

    registry = _load_registry(root)
    stages = dict(registry['stages'])
    if gap in stages:
        existing = stages[gap]
        if isinstance(existing, dict) and existing.get('candidate_id') == candidate_id and existing.get('candidate_sha') == candidate_sha:
            return {'status': 'already_promoted', 'candidate_id': candidate_id, 'gap': gap, 'candidate_sha': candidate_sha}
        raise PromotionError('Promoted stage name already occupied')

    collisions = [path for path in expected.values() if (root / path).exists()]
    if collisions:
        raise PromotionError('Promotion would overwrite existing trusted files')

    previous_registry = canonical(registry) + '\n'
    file_hashes = {path: hashlib.sha256(content.encode()).hexdigest() for path, content in sorted(by_path.items())}
    rollback = {
        'version': 2,
        'candidate_id': candidate_id,
        'gap': gap,
        'baseline_sha': baseline_sha,
        'candidate_sha': candidate_sha,
        'created_paths': sorted(expected.values()),
        'created_sha256': file_hashes,
        'registry_before': registry,
        'registry_sha256_before': hashlib.sha256(previous_registry.encode()).hexdigest(),
    }

    written = []
    try:
        for path, content in sorted(by_path.items()):
            target = (root / path).resolve()
            if not target.is_relative_to(root):
                raise PromotionError('Promotion path escaped repository')
            _atomic_write(target, content)
            written.append(target)
        stages[gap] = {
            'script': expected['stage'],
            'candidate_id': candidate_id,
            'baseline_sha': baseline_sha,
            'candidate_sha': candidate_sha,
        }
        new_registry = {'version': 1, 'stages': stages}
        _atomic_write(root / REGISTRY, canonical(new_registry) + '\n')
        _atomic_write(root / ROLLBACK_DIR / (candidate_id + '.json'), canonical(rollback) + '\n')
    except Exception:
        for target in reversed(written):
            try:
                target.unlink()
            except OSError:
                pass
        _atomic_write(root / REGISTRY, previous_registry)
        raise

    return {'status': 'promoted', 'candidate_id': candidate_id, 'gap': gap, 'candidate_sha': candidate_sha,
            'stage_script': expected['stage'], 'rollback_recorded': True}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('work_order')
    parser.add_argument('candidate')
    parser.add_argument('benchmark')
    parser.add_argument('promotion')
    parser.add_argument('--repo-root', default='.')
    parser.add_argument('--out', default='studio-output')
    args = parser.parse_args(argv)
    out = Path(args.out)
    try:
        order = json.loads(Path(args.work_order).read_text())
        candidate = json.loads(Path(args.candidate).read_text())
        benchmark = json.loads(Path(args.benchmark).read_text())
        promotion = json.loads(Path(args.promotion).read_text())
        result = apply(Path(args.repo_root), order, candidate, benchmark, promotion)
        out.mkdir(parents=True, exist_ok=True)
        (out / 'evolution-applied.json').write_text(canonical(result) + '\n')
        print(canonical(result))
        return 0
    except (OSError, ValueError, json.JSONDecodeError, PromotionError) as exc:
        out.mkdir(parents=True, exist_ok=True)
        (out / 'evolution-apply-error.json').write_text(canonical({'status': 'promotion_blocked', 'error': type(exc).__name__}) + '\n')
        return 1


if __name__ == '__main__':
    sys.exit(main())
