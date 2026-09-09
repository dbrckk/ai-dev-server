"""Persist an approved local promotion as a dedicated GitHub branch and pull request."""
from __future__ import annotations

import base64
import json
import os
from pathlib import Path
import re
import sys
import urllib.error
import urllib.request

from core import canonical


class PersistenceError(RuntimeError):
    pass


def _request(url, token, method='GET', payload=None):
    data = None if payload is None else canonical(payload).encode()
    req = urllib.request.Request(url, data=data, method=method, headers={
        'Accept': 'application/vnd.github+json',
        'Authorization': 'Bearer ' + token,
        'X-GitHub-Api-Version': '2022-11-28',
        'User-Agent': 'ai-dev-server',
        'Content-Type': 'application/json',
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode())
    except (urllib.error.URLError, json.JSONDecodeError) as exc:
        raise PersistenceError('GitHub persistence request failed') from exc


def persist(repo_root: Path, applied: dict, token: str, repository: str, baseline_sha: str):
    if not token:
        raise PersistenceError('GitHub persistence token missing')
    if not re.fullmatch(r'[^/]+/[^/]+', repository):
        raise PersistenceError('GitHub repository identity invalid')
    if not re.fullmatch(r'[0-9a-f]{40}', baseline_sha):
        raise PersistenceError('Baseline SHA invalid')
    if applied.get('status') not in {'promoted', 'already_promoted'}:
        raise PersistenceError('Only an applied promotion may be persisted')
    candidate_id = applied.get('candidate_id')
    gap = applied.get('gap')
    if not isinstance(candidate_id, str) or not candidate_id or not isinstance(gap, str) or not gap.endswith('_qa'):
        raise PersistenceError('Promotion identity invalid')

    root = repo_root.resolve()
    registry = root / 'control/promoted_stages.json'
    rollback = root / 'control/evolution_rollbacks' / (candidate_id + '.json')
    stage = root / f'studio/{gap[:-3]}_stage.py'
    implementation = root / f'studio/{gap}.py'
    tests = root / f'tests/test_{gap}.py'
    benchmark = root / f'tests/benchmarks/{gap}.json'
    files = [registry, rollback, stage, implementation, tests, benchmark]
    if not all(path.is_file() for path in files):
        raise PersistenceError('Applied promotion files are incomplete')

    api = 'https://api.github.com/repos/' + repository
    base_commit = _request(api + '/git/commits/' + baseline_sha, token)
    base_tree = base_commit.get('tree', {}).get('sha')
    if not isinstance(base_tree, str):
        raise PersistenceError('Baseline tree missing')

    tree_entries = []
    for path in files:
        rel = path.relative_to(root).as_posix()
        blob = _request(api + '/git/blobs', token, 'POST', {
            'content': base64.b64encode(path.read_bytes()).decode(), 'encoding': 'base64'})
        sha = blob.get('sha')
        if not isinstance(sha, str):
            raise PersistenceError('GitHub blob creation failed')
        tree_entries.append({'path': rel, 'mode': '100644', 'type': 'blob', 'sha': sha})

    tree = _request(api + '/git/trees', token, 'POST', {'base_tree': base_tree, 'tree': tree_entries})
    tree_sha = tree.get('sha')
    if not isinstance(tree_sha, str):
        raise PersistenceError('GitHub tree creation failed')
    commit = _request(api + '/git/commits', token, 'POST', {
        'message': f'Promote autonomous capability {gap}', 'tree': tree_sha, 'parents': [baseline_sha]})
    commit_sha = commit.get('sha')
    if not isinstance(commit_sha, str):
        raise PersistenceError('GitHub promotion commit creation failed')

    branch = 'evolution/promote-' + re.sub(r'[^a-z0-9-]+', '-', gap.replace('_', '-')).strip('-') + '-' + candidate_id[-8:].lower()
    ref_payload = {'ref': 'refs/heads/' + branch, 'sha': commit_sha}
    try:
        _request(api + '/git/refs', token, 'POST', ref_payload)
    except PersistenceError:
        existing = _request(api + '/git/ref/heads/' + branch, token)
        if existing.get('object', {}).get('sha') != commit_sha:
            raise PersistenceError('Promotion branch already exists with different commit')

    pr = _request(api + '/pulls', token, 'POST', {
        'title': f'Promote autonomous capability: {gap}',
        'head': branch,
        'base': 'main',
        'body': 'Machine-approved autonomous factory evolution. Generated from isolated differential, regression, smoke, integrity and rollback evidence. Merge only through normal repository checks.',
    })
    number = pr.get('number')
    if not isinstance(number, int):
        raise PersistenceError('GitHub promotion pull request creation failed')
    return {'status': 'promotion_persisted', 'candidate_id': candidate_id, 'gap': gap,
            'branch': branch, 'commit_sha': commit_sha, 'pull_request': number}


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('applied')
    parser.add_argument('--repo-root', default='.')
    parser.add_argument('--out', default='studio-output')
    args = parser.parse_args(argv)
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    try:
        applied = json.loads(Path(args.applied).read_text())
        result = persist(Path(args.repo_root), applied, os.environ.get('STUDIO_GITHUB_TOKEN', ''),
                         os.environ.get('GITHUB_REPOSITORY', ''), os.environ.get('GITHUB_SHA', ''))
        (out / 'evolution-persisted.json').write_text(canonical(result) + '\n')
        print(canonical(result)); return 0
    except (OSError, ValueError, json.JSONDecodeError, PersistenceError):
        (out / 'evolution-persist-error.json').write_text(canonical({'status':'persistence_blocked'}) + '\n')
        return 1


if __name__ == '__main__':
    sys.exit(main())
