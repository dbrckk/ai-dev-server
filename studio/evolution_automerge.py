"""Merge a durable autonomous evolution only from the runner that persisted it."""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
from urllib.parse import urlparse

from core import canonical
from evolution_candidate import expected_paths
from evolution_pending import PendingError, check as check_pending
from evolution_persist import PersistenceError, _request

REQUIRED_CHECKS = {'validate', 'mobile-smoke'}
TRUSTED_CHECK_APP = 'github-actions'


class AutoMergeError(RuntimeError):
    pass


def _allowed_paths(candidate_id, gap):
    expected = set(expected_paths(gap).values())
    expected.add('control/promoted_stages.json')
    expected.add('control/evolution_rollbacks/' + candidate_id + '.json')
    return expected


def _trusted_check(run, repository):
    if not isinstance(run, dict): return False
    app = run.get('app')
    if not isinstance(app, dict) or app.get('slug') != TRUSTED_CHECK_APP: return False
    details = run.get('details_url')
    if not isinstance(details, str): return False
    parsed = urlparse(details)
    prefix = '/' + repository + '/actions/runs/'
    return parsed.scheme == 'https' and parsed.netloc == 'github.com' and parsed.path.startswith(prefix)


def attempt(work_order: dict, persisted: dict, token: str, repository: str) -> dict:
    if not isinstance(persisted, dict) or persisted.get('status') not in {'promotion_persisted','already_persisted'}:
        raise AutoMergeError('Local persistence proof missing')
    pending = check_pending(work_order, token, repository)
    status = pending.get('status')
    if status == 'promotion_merged_restart_required':
        return {'status':'promotion_already_merged','pull_request':pending.get('pull_request')}
    if status != 'promotion_pending_merge':
        raise AutoMergeError('Pending promotion is not safely mergeable')

    candidate_id = work_order.get('candidate_id'); gap = (work_order.get('primary_gap') or {}).get('value')
    number = persisted.get('pull_request'); head_sha = persisted.get('commit_sha'); branch = persisted.get('branch')
    if pending.get('pull_request') != number or pending.get('branch') != branch:
        raise AutoMergeError('Pending promotion does not match local persistence proof')
    if not isinstance(number,int) or not isinstance(head_sha,str) or len(head_sha)!=40 or not isinstance(branch,str):
        raise AutoMergeError('Local persistence proof incomplete')
    api = 'https://api.github.com/repos/' + repository
    pr = _request(api + '/pulls/' + str(number), token)
    if not isinstance(pr,dict) or pr.get('state')!='open' or pr.get('draft') is True:
        raise AutoMergeError('Promotion pull request is not open and ready')
    if pr.get('base',{}).get('ref')!='main' or pr.get('head',{}).get('ref')!=branch or pr.get('head',{}).get('sha')!=head_sha:
        raise AutoMergeError('Promotion pull request head changed after approval')

    files = _request(api + '/pulls/' + str(number) + '/files?per_page=100', token)
    allowed = _allowed_paths(candidate_id,gap)
    if not isinstance(files,list) or len(files)!=len(allowed): raise AutoMergeError('Promotion pull request file scope changed')
    names={item.get('filename') for item in files if isinstance(item,dict)}
    if names!=allowed: raise AutoMergeError('Promotion pull request contains unapproved paths')
    if any(item.get('status') not in {'added','modified'} for item in files if isinstance(item,dict)):
        raise AutoMergeError('Promotion pull request contains destructive file changes')

    checks=_request(api + '/commits/' + head_sha + '/check-runs?per_page=100',token)
    runs=checks.get('check_runs') if isinstance(checks,dict) else None
    if not isinstance(runs,list): raise AutoMergeError('GitHub check-run evidence malformed')
    trusted=[run for run in runs if _trusted_check(run,repository)]
    by_name={run.get('name'):run for run in trusted if isinstance(run.get('name'),str)}
    missing=REQUIRED_CHECKS-set(by_name)
    if missing: return {'status':'awaiting_required_checks','missing_checks':sorted(missing),'pull_request':number}
    for name in REQUIRED_CHECKS:
        run=by_name[name]
        if run.get('status')!='completed': return {'status':'awaiting_required_checks','missing_checks':[],'pull_request':number}
        if run.get('conclusion')!='success': raise AutoMergeError('Required promotion check failed: '+name)

    pr=_request(api + '/pulls/' + str(number),token)
    if pr.get('head',{}).get('sha')!=head_sha: raise AutoMergeError('Promotion pull request head changed during verification')
    if pr.get('mergeable') is not True or pr.get('mergeable_state')!='clean':
        return {'status':'awaiting_clean_merge_state','pull_request':number}
    merged=_request(api + '/pulls/' + str(number) + '/merge',token,'PUT',{'sha':head_sha,'merge_method':'merge','commit_title':'Promote autonomous capability: '+gap})
    if not isinstance(merged,dict) or merged.get('merged') is not True: raise AutoMergeError('GitHub refused autonomous promotion merge')
    return {'status':'promotion_merged','pull_request':number,'merge_sha':merged.get('sha'),'candidate_id':candidate_id,'gap':gap}


def main(argv=None):
    import argparse
    parser=argparse.ArgumentParser(); parser.add_argument('work_order'); parser.add_argument('persisted'); parser.add_argument('--out',default='studio-output')
    args=parser.parse_args(argv); out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
    try:
        order=json.loads(Path(args.work_order).read_text()); persisted=json.loads(Path(args.persisted).read_text())
        result=attempt(order,persisted,os.environ.get('STUDIO_GITHUB_TOKEN',''),os.environ.get('GITHUB_REPOSITORY',''))
        (out/'evolution-automerge.json').write_text(canonical(result)+'\n'); print(canonical(result)); return 0
    except (OSError,ValueError,json.JSONDecodeError,PersistenceError,PendingError,AutoMergeError):
        (out/'evolution-automerge-error.json').write_text(canonical({'status':'automerge_blocked'})+'\n'); return 1


if __name__=='__main__': sys.exit(main())
