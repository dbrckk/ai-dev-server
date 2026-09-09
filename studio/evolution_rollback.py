"""Trusted rollback for previously promoted evolution candidates."""
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
from evolution_promotion import REGISTRY, ROLLBACK_DIR


class RollbackError(RuntimeError):
    pass


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile('w', dir=path.parent, delete=False, encoding='utf-8') as handle:
        handle.write(content)
        temp = Path(handle.name)
    os.replace(temp, path)


def _load_json(path: Path, label: str) -> dict:
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        raise RollbackError(label + ' unreadable') from None
    if not isinstance(value, dict):
        raise RollbackError(label + ' malformed')
    return value


def rollback(repo_root: Path, candidate_id: str) -> dict:
    root = repo_root.resolve()
    if not isinstance(candidate_id, str) or not re.fullmatch(r'[A-Za-z0-9._-]{3,120}', candidate_id):
        raise RollbackError('Candidate id invalid')
    record_path = root / ROLLBACK_DIR / (candidate_id + '.json')
    record = _load_json(record_path, 'Rollback record')
    required = {'version','candidate_id','gap','baseline_sha','candidate_sha','created_paths','created_sha256','registry_before','registry_sha256_before'}
    if set(record) != required or record.get('version') != 2 or record.get('candidate_id') != candidate_id:
        raise RollbackError('Rollback record malformed')
    gap = record.get('gap')
    if not isinstance(gap, str) or not re.fullmatch(r'[a-z][a-z0-9_]{2,48}_qa', gap):
        raise RollbackError('Rollback gap invalid')
    for key in ('baseline_sha', 'candidate_sha'):
        if not isinstance(record.get(key), str) or not re.fullmatch(r'[0-9a-f]{40}', record[key]):
            raise RollbackError('Rollback commit identity invalid')
    paths = record.get('created_paths')
    hashes = record.get('created_sha256')
    if not isinstance(paths, list) or not paths or any(not isinstance(path, str) for path in paths):
        raise RollbackError('Rollback paths malformed')
    if not isinstance(hashes, dict) or set(hashes) != set(paths):
        raise RollbackError('Rollback file hashes malformed')
    if any(not isinstance(value, str) or not re.fullmatch(r'[0-9a-f]{64}', value) for value in hashes.values()):
        raise RollbackError('Rollback file hash invalid')
    previous_registry = record.get('registry_before')
    if not isinstance(previous_registry, dict) or previous_registry.get('version') != 1 or not isinstance(previous_registry.get('stages'), dict):
        raise RollbackError('Rollback previous registry malformed')
    previous_text = canonical(previous_registry) + '\n'
    if hashlib.sha256(previous_text.encode()).hexdigest() != record.get('registry_sha256_before'):
        raise RollbackError('Rollback previous registry integrity mismatch')

    registry_path = root / REGISTRY
    current = _load_json(registry_path, 'Promoted-stage registry')
    entry = (current.get('stages') or {}).get(gap) if isinstance(current.get('stages'), dict) else None
    if not isinstance(entry, dict) or entry.get('candidate_id') != candidate_id or entry.get('candidate_sha') != record['candidate_sha']:
        raise RollbackError('Current registry no longer matches promoted candidate')

    targets = []
    for relative in paths:
        target = (root / relative).resolve()
        if not target.is_relative_to(root):
            raise RollbackError('Rollback path escaped repository')
        if not target.is_file():
            raise RollbackError('Promoted file missing before rollback')
        if hashlib.sha256(target.read_bytes()).hexdigest() != hashes[relative]:
            raise RollbackError('Promoted file changed after promotion')
        targets.append(target)

    _atomic_write(registry_path, previous_text)
    for target in targets:
        target.unlink()
    applied = {
        'version': 1,
        'status': 'rolled_back',
        'candidate_id': candidate_id,
        'gap': gap,
        'restored_baseline_sha': record['baseline_sha'],
        'removed_paths': paths,
    }
    _atomic_write(root / ROLLBACK_DIR / (candidate_id + '.applied.json'), canonical(applied) + '\n')
    return applied


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('candidate_id')
    parser.add_argument('--repo-root', default='.')
    parser.add_argument('--out', default='studio-output')
    args = parser.parse_args(argv)
    out = Path(args.out)
    try:
        result = rollback(Path(args.repo_root), args.candidate_id)
        out.mkdir(parents=True, exist_ok=True)
        (out / 'evolution-rollback.json').write_text(canonical(result) + '\n')
        print(canonical(result))
        return 0
    except (OSError, ValueError, json.JSONDecodeError, RollbackError) as exc:
        out.mkdir(parents=True, exist_ok=True)
        (out / 'evolution-rollback-error.json').write_text(canonical({'status':'rollback_blocked','error':type(exc).__name__}) + '\n')
        return 1


if __name__ == '__main__':
    sys.exit(main())
