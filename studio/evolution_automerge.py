"""Merge durable autonomous evolution from immutable content-bound GitHub proof."""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import time
from urllib.parse import urlparse

from core import canonical
from evolution_candidate import expected_paths
from evolution_pending import PendingError, check as check_pending
from evolution_persist import PersistenceError, _request

REQUIRED_CHECKS = {'validate', 'mobile-smoke'}
TRUSTED_CHECK_APP = 'github-actions'


class AutoMergeError(RuntimeError): pass


def _allowed_paths(candidate_id, gap):
    expected=set(expected_paths(gap).values()); expected.add('control/promoted_stages.json'); expected.add('control/evolution_rollbacks/'+candidate_id+'.json'); return expected


def _trusted_check(run, repository):
    if not isinstance(run,dict): return False
    app=run.get('app')
    if not isinstance(app,dict) or app.get('slug')!=TRUSTED_CHECK_APP: return False
    details=run.get('details_url')
    if not isinstance(details,str): return False
    parsed=urlparse(details); prefix='/'+repository+'/actions/runs/'
    return parsed.scheme=='https' and parsed.netloc=='github.com' and parsed.path.startswith(prefix)


def _proof(pending, persisted):
    if pending.get('proof')!='branch_name_sha_v1': raise AutoMergeError('Durable promotion proof missing')
    proof={'pull_request':pending.get('pull_request'),'commit_sha':pending.get('commit_sha'),'branch':pending.get('branch')}
    if not isinstance(proof['pull_request'],int) or not isinstance(proof['commit_sha'],str) or len(proof['commit_sha'])!=40 or not isinstance(proof['branch'],str):
        raise AutoMergeError('Durable promotion proof incomplete')
    if persisted:
        if not isinstance(persisted,dict) or persisted.get('status') not in {'promotion_persisted','already_persisted'}:
            raise AutoMergeError('Local persistence proof malformed')
        for key in proof:
            if persisted.get(key)!=proof[key]: raise AutoMergeError('Local persistence proof does not match durable proof')
    return proof


def attempt(work_order:dict,persisted:dict|None,token:str,repository:str)->dict:
    pending=check_pending(work_order,token,repository); status=pending.get('status')
    if status=='promotion_merged_restart_required': return {'status':'promotion_already_merged','pull_request':pending.get('pull_request')}
    if status!='promotion_pending_merge': raise AutoMergeError('Pending promotion is not safely mergeable')
    candidate_id=work_order.get('candidate_id'); gap=(work_order.get('primary_gap') or {}).get('value')
    proof=_proof(pending,persisted or {}); number=proof['pull_request']; head_sha=proof['commit_sha']; branch=proof['branch']
    api='https://api.github.com/repos/'+repository
    pr=_request(api+'/pulls/'+str(number),token)
    if not isinstance(pr,dict) or pr.get('state')!='open' or pr.get('draft') is True: raise AutoMergeError('Promotion pull request is not open and ready')
    if pr.get('base',{}).get('ref')!='main' or pr.get('head',{}).get('ref')!=branch or pr.get('head',{}).get('sha')!=head_sha: raise AutoMergeError('Promotion pull request head changed after approval')
    files=_request(api+'/pulls/'+str(number)+'/files?per_page=100',token); allowed=_allowed_paths(candidate_id,gap)
    if not isinstance(files,list) or len(files)!=len(allowed): raise AutoMergeError('Promotion pull request file scope changed')
    names={item.get('filename') for item in files if isinstance(item,dict)}
    if names!=allowed: raise AutoMergeError('Promotion pull request contains unapproved paths')
    if any(item.get('status') not in {'added','modified'} for item in files if isinstance(item,dict)): raise AutoMergeError('Promotion pull request contains destructive file changes')
    checks=_request(api+'/commits/'+head_sha+'/check-runs?per_page=100',token); runs=checks.get('check_runs') if isinstance(checks,dict) else None
    if not isinstance(runs,list): raise AutoMergeError('GitHub check-run evidence malformed')
    trusted=[run for run in runs if _trusted_check(run,repository)]; by_name={run.get('name'):run for run in trusted if isinstance(run.get('name'),str)}
    missing=REQUIRED_CHECKS-set(by_name)
    if missing: return {'status':'awaiting_required_checks','missing_checks':sorted(missing),'pull_request':number}
    for name in REQUIRED_CHECKS:
        run=by_name[name]
        if run.get('status')!='completed': return {'status':'awaiting_required_checks','missing_checks':[],'pull_request':number}
        if run.get('conclusion')!='success': raise AutoMergeError('Required promotion check failed: '+name)
    pr=_request(api+'/pulls/'+str(number),token)
    if pr.get('head',{}).get('sha')!=head_sha or pr.get('head',{}).get('ref')!=branch: raise AutoMergeError('Promotion pull request head changed during verification')
    if pr.get('mergeable') is not True or pr.get('mergeable_state')!='clean': return {'status':'awaiting_clean_merge_state','pull_request':number}
    merged=_request(api+'/pulls/'+str(number)+'/merge',token,'PUT',{'sha':head_sha,'merge_method':'merge','commit_title':'Promote autonomous capability: '+gap})
    if not isinstance(merged,dict) or merged.get('merged') is not True: raise AutoMergeError('GitHub refused autonomous promotion merge')
    return {'status':'promotion_merged','pull_request':number,'merge_sha':merged.get('sha'),'candidate_id':candidate_id,'gap':gap}


def wait_and_attempt(work_order,persisted,token,repository,wait_seconds,poll_seconds=20):
    deadline=time.monotonic()+max(0,wait_seconds)
    while True:
        result=attempt(work_order,persisted,token,repository)
        if result.get('status') not in {'awaiting_required_checks','awaiting_clean_merge_state'}: return result
        remaining=deadline-time.monotonic()
        if remaining<=0: return result
        time.sleep(min(poll_seconds,remaining))


def main(argv=None):
    import argparse
    parser=argparse.ArgumentParser(); parser.add_argument('work_order'); parser.add_argument('persisted',nargs='?'); parser.add_argument('--out',default='studio-output'); parser.add_argument('--wait-seconds',type=int,default=0)
    args=parser.parse_args(argv); out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
    try:
        order=json.loads(Path(args.work_order).read_text()); persisted=json.loads(Path(args.persisted).read_text()) if args.persisted else {}
        result=wait_and_attempt(order,persisted,os.environ.get('STUDIO_GITHUB_TOKEN',''),os.environ.get('GITHUB_REPOSITORY',''),args.wait_seconds)
        (out/'evolution-automerge.json').write_text(canonical(result)+'\n'); print(canonical(result)); return 0
    except (OSError,ValueError,json.JSONDecodeError,PersistenceError,PendingError,AutoMergeError):
        (out/'evolution-automerge-error.json').write_text(canonical({'status':'automerge_blocked'})+'\n'); return 1


if __name__=='__main__': sys.exit(main())
