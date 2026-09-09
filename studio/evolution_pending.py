"""Recover a durable content-bound GitHub evolution across runner restarts."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import sys
import urllib.parse

from core import canonical
from evolution_persist import PersistenceError, _branch_prefix, _request


class PendingError(RuntimeError):
    pass


def _candidate_prs(api, token, prefix):
    query = urllib.parse.urlencode({'state':'all','base':'main','per_page':100})
    pulls = _request(api + '/pulls?' + query, token)
    if not isinstance(pulls, list): raise PendingError('Pending promotion PR lookup malformed')
    if len(pulls) == 100: raise PendingError('Pending promotion history exceeds bounded lookup')
    return [pr for pr in pulls if isinstance(pr, dict) and isinstance(pr.get('head', {}).get('ref'), str)
            and pr['head']['ref'].startswith(prefix)]


def check(work_order: dict, token: str, repository: str) -> dict:
    if not token: raise PendingError('GitHub persistence token missing')
    if not re.fullmatch(r'[^/]+/[^/]+', repository): raise PendingError('GitHub repository identity invalid')
    if work_order.get('status') != 'candidate_planned': raise PendingError('Pending check requires candidate work order')
    candidate_id = work_order.get('candidate_id'); gap = (work_order.get('primary_gap') or {}).get('value')
    if not isinstance(candidate_id, str) or not candidate_id or not isinstance(gap, str) or not gap.endswith('_qa'):
        raise PendingError('Pending promotion identity invalid')
    prefix = _branch_prefix(gap, candidate_id); api = 'https://api.github.com/repos/' + repository
    matches = _candidate_prs(api, token, prefix)
    if not matches:
        refs = _request(api + '/git/matching-refs/heads/' + urllib.parse.quote(prefix, safe='/'), token)
        if not isinstance(refs, list): raise PendingError('Pending promotion ref lookup malformed')
        return {'status':'promotion_orphaned' if refs else 'no_pending_promotion','candidate_id':candidate_id,'gap':gap,'branch_prefix':prefix}
    if len(matches) != 1:
        return {'status':'promotion_orphaned','candidate_id':candidate_id,'gap':gap,'branch_prefix':prefix}

    pr = matches[0]; branch = pr['head']['ref']; encoded_sha = branch[len(prefix):]; pr_sha = pr.get('head', {}).get('sha')
    if not re.fullmatch(r'[0-9a-f]{40}', encoded_sha or '') or pr_sha != encoded_sha or not isinstance(pr.get('number'), int):
        return {'status':'promotion_orphaned','candidate_id':candidate_id,'gap':gap,'branch':branch,'branch_prefix':prefix}

    if pr.get('merged_at'):
        state = 'promotion_merged_restart_required'
    elif pr.get('state') == 'open':
        ref = _request(api + '/git/ref/heads/' + urllib.parse.quote(branch, safe='/'), token, allow_404=True)
        current_sha = ref.get('object', {}).get('sha') if isinstance(ref, dict) else None
        if current_sha != encoded_sha:
            return {'status':'promotion_orphaned','candidate_id':candidate_id,'gap':gap,'branch':branch,'branch_prefix':prefix,'commit_sha':encoded_sha,'pull_request':pr['number']}
        state = 'promotion_pending_merge'
    else:
        state = 'promotion_closed_without_merge'
    return {'status':state,'candidate_id':candidate_id,'gap':gap,'branch':branch,'branch_prefix':prefix,
            'commit_sha':encoded_sha,'pull_request':pr['number'],'proof':'branch_name_sha_v1'}


def main(argv=None):
    import argparse
    parser=argparse.ArgumentParser(); parser.add_argument('work_order'); parser.add_argument('--out',default='studio-output')
    args=parser.parse_args(argv); out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
    try:
        order=json.loads(Path(args.work_order).read_text())
        result=check(order,os.environ.get('STUDIO_GITHUB_TOKEN',''),os.environ.get('GITHUB_REPOSITORY',''))
        (out/'evolution-pending.json').write_text(canonical(result)+'\n'); print(canonical(result)); return 0
    except (OSError,ValueError,json.JSONDecodeError,PersistenceError,PendingError):
        (out/'evolution-pending-error.json').write_text(canonical({'status':'pending_check_blocked'})+'\n'); return 1


if __name__=='__main__': sys.exit(main())
