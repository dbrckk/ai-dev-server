"""Detect an already-persisted GitHub evolution so a restarted runner does not regenerate it."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import sys
import urllib.parse

from core import canonical
from evolution_persist import PersistenceError, _branch_name, _request


class PendingError(RuntimeError):
    pass


def check(work_order: dict, token: str, repository: str) -> dict:
    if not token: raise PendingError('GitHub persistence token missing')
    if not re.fullmatch(r'[^/]+/[^/]+', repository): raise PendingError('GitHub repository identity invalid')
    if work_order.get('status') != 'candidate_planned': raise PendingError('Pending check requires candidate work order')
    candidate_id = work_order.get('candidate_id'); gap = (work_order.get('primary_gap') or {}).get('value')
    if not isinstance(candidate_id, str) or not candidate_id or not isinstance(gap, str) or not gap.endswith('_qa'):
        raise PendingError('Pending promotion identity invalid')
    branch = _branch_name(gap, candidate_id); owner = repository.split('/', 1)[0]; api = 'https://api.github.com/repos/' + repository
    ref = _request(api + '/git/ref/heads/' + urllib.parse.quote(branch, safe='/'), token, allow_404=True)
    if ref is None:
        return {'status': 'no_pending_promotion', 'candidate_id': candidate_id, 'gap': gap, 'branch': branch}
    commit_sha = ref.get('object', {}).get('sha') if isinstance(ref, dict) else None
    if not isinstance(commit_sha, str) or not re.fullmatch(r'[0-9a-f]{40}', commit_sha): raise PendingError('Pending promotion branch malformed')
    query = urllib.parse.urlencode({'state': 'all', 'head': owner + ':' + branch, 'base': 'main', 'per_page': 10})
    pulls = _request(api + '/pulls?' + query, token)
    if not isinstance(pulls, list): raise PendingError('Pending promotion PR lookup malformed')
    matches = [pr for pr in pulls if isinstance(pr, dict) and pr.get('head', {}).get('sha') == commit_sha and isinstance(pr.get('number'), int)]
    if len(matches) != 1:
        return {'status': 'promotion_orphaned', 'candidate_id': candidate_id, 'gap': gap, 'branch': branch, 'commit_sha': commit_sha}
    pr = matches[0]
    if pr.get('merged_at'):
        state = 'promotion_merged_restart_required'
    elif pr.get('state') == 'open':
        state = 'promotion_pending_merge'
    else:
        state = 'promotion_closed_without_merge'
    return {'status': state, 'candidate_id': candidate_id, 'gap': gap, 'branch': branch,
            'commit_sha': commit_sha, 'pull_request': pr['number']}


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(); parser.add_argument('work_order'); parser.add_argument('--out', default='studio-output')
    args = parser.parse_args(argv); out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    try:
        order = json.loads(Path(args.work_order).read_text())
        result = check(order, os.environ.get('STUDIO_GITHUB_TOKEN', ''), os.environ.get('GITHUB_REPOSITORY', ''))
        (out / 'evolution-pending.json').write_text(canonical(result) + '\n'); print(canonical(result)); return 0
    except (OSError, ValueError, json.JSONDecodeError, PersistenceError, PendingError):
        (out / 'evolution-pending-error.json').write_text(canonical({'status': 'pending_check_blocked'}) + '\n'); return 1


if __name__ == '__main__': sys.exit(main())
