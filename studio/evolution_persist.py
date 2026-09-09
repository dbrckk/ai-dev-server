"""Persist an approved local promotion as a content-bound GitHub branch and PR."""
from __future__ import annotations

import base64
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

from core import canonical


class PersistenceError(RuntimeError):
    pass


def _request(url, token, method='GET', payload=None, allow_404=False):
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
    except urllib.error.HTTPError as exc:
        if allow_404 and exc.code == 404:
            return None
        raise PersistenceError('GitHub persistence request failed') from exc
    except (urllib.error.URLError, json.JSONDecodeError) as exc:
        raise PersistenceError('GitHub persistence request failed') from exc


def _branch_prefix(gap, candidate_id):
    slug = re.sub(r'[^a-z0-9-]+', '-', gap.replace('_', '-')).strip('-')
    identity = hashlib.sha256(candidate_id.encode()).hexdigest()[:12]
    return 'evolution/promote-' + slug + '-' + identity + '-'


def _branch_name(gap, candidate_id, commit_sha):
    if not isinstance(commit_sha, str) or not re.fullmatch(r'[0-9a-f]{40}', commit_sha):
        raise PersistenceError('Promotion commit SHA invalid')
    return _branch_prefix(gap, candidate_id) + commit_sha


def _matching_refs(api, token, prefix):
    url = api + '/git/matching-refs/heads/' + urllib.parse.quote(prefix, safe='/')
    refs = _request(url, token)
    if not isinstance(refs, list):
        raise PersistenceError('GitHub promotion ref lookup malformed')
    expected_prefix = 'refs/heads/' + prefix
    return [ref for ref in refs if isinstance(ref, dict) and isinstance(ref.get('ref'), str)
            and ref['ref'].startswith(expected_prefix)]


def _existing_pr(api, token, owner, branch, commit_sha):
    query = urllib.parse.urlencode({'state': 'all', 'head': owner + ':' + branch, 'base': 'main', 'per_page': 20})
    pulls = _request(api + '/pulls?' + query, token)
    if not isinstance(pulls, list):
        raise PersistenceError('GitHub pull request lookup malformed')
    matches = [pr for pr in pulls if isinstance(pr, dict) and pr.get('head', {}).get('sha') == commit_sha
               and pr.get('head', {}).get('ref') == branch and isinstance(pr.get('number'), int)]
    if len(matches) > 1:
        raise PersistenceError('Multiple pull requests claim the same promotion branch')
    return matches[0]['number'] if matches else None


def _verify_local_promotion(root, applied, baseline_sha):
    candidate_id = applied['candidate_id']; gap = applied['gap']; candidate_sha = applied.get('candidate_sha')
    if not isinstance(candidate_sha, str) or not re.fullmatch(r'[0-9a-f]{40}', candidate_sha):
        raise PersistenceError('Applied candidate SHA invalid')
    rollback_path = root / 'control/evolution_rollbacks' / (candidate_id + '.json')
    registry_path = root / 'control/promoted_stages.json'
    try:
        rollback = json.loads(rollback_path.read_text()); registry = json.loads(registry_path.read_text())
    except (OSError, json.JSONDecodeError):
        raise PersistenceError('Promotion integrity evidence unreadable') from None
    if not isinstance(rollback, dict) or rollback.get('version') != 2:
        raise PersistenceError('Rollback integrity evidence malformed')
    if rollback.get('candidate_id') != candidate_id or rollback.get('gap') != gap or rollback.get('baseline_sha') != baseline_sha or rollback.get('candidate_sha') != candidate_sha:
        raise PersistenceError('Rollback integrity identity mismatch')
    hashes = rollback.get('created_sha256'); paths = rollback.get('created_paths')
    if not isinstance(hashes, dict) or not isinstance(paths, list) or set(hashes) != set(paths):
        raise PersistenceError('Rollback file integrity evidence malformed')
    for rel in paths:
        if not isinstance(rel, str): raise PersistenceError('Rollback path malformed')
        path = (root / rel).resolve()
        if not path.is_relative_to(root) or not path.is_file(): raise PersistenceError('Promoted file missing')
        if hashlib.sha256(path.read_bytes()).hexdigest() != hashes.get(rel):
            raise PersistenceError('Promoted file changed after approval')
    entry = registry.get('stages', {}).get(gap) if isinstance(registry, dict) else None
    if not isinstance(entry, dict) or entry.get('candidate_id') != candidate_id or entry.get('baseline_sha') != baseline_sha or entry.get('candidate_sha') != candidate_sha:
        raise PersistenceError('Promoted-stage registry identity mismatch')
    return rollback_path, registry_path


def persist(repo_root: Path, applied: dict, token: str, repository: str, baseline_sha: str):
    if not token: raise PersistenceError('GitHub persistence token missing')
    if not re.fullmatch(r'[^/]+/[^/]+', repository): raise PersistenceError('GitHub repository identity invalid')
    if not re.fullmatch(r'[0-9a-f]{40}', baseline_sha): raise PersistenceError('Baseline SHA invalid')
    if applied.get('status') not in {'promoted', 'already_promoted'}: raise PersistenceError('Only an applied promotion may be persisted')
    candidate_id = applied.get('candidate_id'); gap = applied.get('gap')
    if not isinstance(candidate_id, str) or not candidate_id or not isinstance(gap, str) or not gap.endswith('_qa'):
        raise PersistenceError('Promotion identity invalid')

    root = repo_root.resolve(); rollback, registry = _verify_local_promotion(root, applied, baseline_sha)
    stage = root / f'studio/{gap[:-3]}_stage.py'; implementation = root / f'studio/{gap}.py'
    tests = root / f'tests/test_{gap}.py'; benchmark = root / f'tests/benchmarks/{gap}.json'
    files = [registry, rollback, stage, implementation, tests, benchmark]
    if not all(path.is_file() for path in files): raise PersistenceError('Applied promotion files are incomplete')

    api = 'https://api.github.com/repos/' + repository; owner = repository.split('/', 1)[0]
    base_commit = _request(api + '/git/commits/' + baseline_sha, token)
    base_tree = base_commit.get('tree', {}).get('sha') if isinstance(base_commit, dict) else None
    if not isinstance(base_tree, str): raise PersistenceError('Baseline tree missing')

    tree_entries = []
    for path in files:
        rel = path.relative_to(root).as_posix()
        blob = _request(api + '/git/blobs', token, 'POST', {'content': base64.b64encode(path.read_bytes()).decode(), 'encoding': 'base64'})
        sha = blob.get('sha') if isinstance(blob, dict) else None
        if not isinstance(sha, str): raise PersistenceError('GitHub blob creation failed')
        tree_entries.append({'path': rel, 'mode': '100644', 'type': 'blob', 'sha': sha})
    tree = _request(api + '/git/trees', token, 'POST', {'base_tree': base_tree, 'tree': tree_entries})
    tree_sha = tree.get('sha') if isinstance(tree, dict) else None
    if not isinstance(tree_sha, str): raise PersistenceError('GitHub tree creation failed')

    prefix = _branch_prefix(gap, candidate_id); refs = _matching_refs(api, token, prefix)
    if len(refs) > 1: raise PersistenceError('Multiple promotion branches exist for one candidate')
    if refs:
        branch = refs[0]['ref'][len('refs/heads/'):]
        encoded_sha = branch[len(prefix):]
        current_sha = refs[0].get('object', {}).get('sha')
        if not re.fullmatch(r'[0-9a-f]{40}', encoded_sha or '') or current_sha != encoded_sha:
            raise PersistenceError('Promotion branch head no longer matches its approved SHA')
        existing_commit = _request(api + '/git/commits/' + encoded_sha, token)
        existing_tree = existing_commit.get('tree', {}).get('sha') if isinstance(existing_commit, dict) else None
        parents = existing_commit.get('parents') if isinstance(existing_commit, dict) else None
        parent_shas = [item.get('sha') for item in parents] if isinstance(parents, list) else []
        if existing_tree != tree_sha or parent_shas != [baseline_sha]: raise PersistenceError('Promotion branch already exists with different content')
        number = _existing_pr(api, token, owner, branch, encoded_sha)
        if number is None: raise PersistenceError('Existing promotion branch has no matching pull request')
        return {'status':'already_persisted','candidate_id':candidate_id,'gap':gap,'branch':branch,'commit_sha':encoded_sha,'pull_request':number}

    commit = _request(api + '/git/commits', token, 'POST', {'message': f'Promote autonomous capability {gap}', 'tree': tree_sha, 'parents': [baseline_sha]})
    commit_sha = commit.get('sha') if isinstance(commit, dict) else None
    if not isinstance(commit_sha, str) or not re.fullmatch(r'[0-9a-f]{40}', commit_sha): raise PersistenceError('GitHub promotion commit creation failed')
    branch = _branch_name(gap, candidate_id, commit_sha)
    _request(api + '/git/refs', token, 'POST', {'ref':'refs/heads/' + branch,'sha':commit_sha})
    existing_number = _existing_pr(api, token, owner, branch, commit_sha)
    if existing_number is not None:
        return {'status':'already_persisted','candidate_id':candidate_id,'gap':gap,'branch':branch,'commit_sha':commit_sha,'pull_request':existing_number}
    pr = _request(api + '/pulls', token, 'POST', {
        'title': f'Promote autonomous capability: {gap}', 'head': branch, 'base': 'main',
        'body': 'Machine-approved autonomous factory evolution. The branch name cryptographically binds this PR to the exact approved commit SHA. Generated from isolated differential, regression, smoke, integrity and rollback evidence.'})
    number = pr.get('number') if isinstance(pr, dict) else None
    if not isinstance(number, int): raise PersistenceError('GitHub promotion pull request creation failed')
    return {'status':'promotion_persisted','candidate_id':candidate_id,'gap':gap,'branch':branch,'commit_sha':commit_sha,'pull_request':number}


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(); parser.add_argument('applied'); parser.add_argument('--repo-root', default='.'); parser.add_argument('--out', default='studio-output')
    args = parser.parse_args(argv); out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    try:
        applied = json.loads(Path(args.applied).read_text())
        result = persist(Path(args.repo_root), applied, os.environ.get('STUDIO_GITHUB_TOKEN', ''), os.environ.get('GITHUB_REPOSITORY', ''), os.environ.get('GITHUB_SHA', ''))
        (out / 'evolution-persisted.json').write_text(canonical(result) + '\n'); print(canonical(result)); return 0
    except (OSError, ValueError, json.JSONDecodeError, PersistenceError):
        (out / 'evolution-persist-error.json').write_text(canonical({'status':'persistence_blocked'}) + '\n'); return 1


if __name__ == '__main__': sys.exit(main())
