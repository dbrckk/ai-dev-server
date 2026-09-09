"""GitHub Actions adapter for the provider-neutral autonomous completion pipeline."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import uuid

from ci_provider import enabled
from core import StudioError, canonical, request_check
from orchestrator import run_project


def bounded_run(args, timeout):
    run_id=uuid.uuid4().hex; env=dict(os.environ,STUDIO_RUN_ID=run_id); process=subprocess.Popen(args,env=env,start_new_session=True)
    try: return subprocess.CompletedProcess(args,process.wait(timeout=timeout))
    except subprocess.TimeoutExpired:
        try: os.killpg(process.pid,signal.SIGTERM); process.wait(timeout=10)
        except (ProcessLookupError,subprocess.TimeoutExpired): pass
        try: os.killpg(process.pid,signal.SIGKILL)
        except ProcessLookupError: pass
        process.wait()
        try:
            containers=subprocess.run(['docker','ps','-aq','--filter','label=mobile-studio-run='+run_id],capture_output=True,text=True,timeout=15,check=True).stdout.split()
            if containers: subprocess.run(['docker','rm','-f',*containers],capture_output=True,timeout=30,check=True)
        except (OSError,subprocess.SubprocessError): raise StudioError('Timed-out worker stopped but container cleanup failed') from None
        raise


def _finish_persisted_evolution(out,runner,deadline,clock):
    order=out/'evolution-work-order.json'; persisted=out/'evolution-persisted.json'
    if not order.is_file() or not persisted.is_file(): return None
    remaining=int(deadline-clock())
    if remaining<=0: return 'deferred'
    result=runner([sys.executable,'studio/evolution_automerge.py',str(order),str(persisted),'--out',str(out),'--wait-seconds',str(max(0,remaining-10))],timeout=remaining)
    if result.returncode!=0: return 'blocked'
    path=out/'evolution-automerge.json'
    if not path.is_file(): raise StudioError('Successful evolution auto-merge produced no evidence')
    try: value=json.loads(path.read_text())
    except (OSError,json.JSONDecodeError): raise StudioError('Evolution auto-merge produced invalid evidence') from None
    status=value.get('status')
    if status in {'promotion_merged','promotion_already_merged'}: return 'merged_restart_required'
    if status in {'awaiting_required_checks','awaiting_clean_merge_state'}: return 'awaiting_checks'
    raise StudioError('Evolution auto-merge returned invalid state')


def run(request_path:Path,out=Path('studio-output'),runner=bounded_run,clock=time.monotonic,budget_seconds=85*60,baseline_sha:str|None=None)->dict:
    request=request_check(json.loads(request_path.read_text()))
    if not request['enabled']:
        result={'status':'disabled','next_stage':None,'finished':False}; out.mkdir(parents=True,exist_ok=True); (out/'github-pipeline.json').write_text(canonical(result)); return result
    deadline=clock()+budget_seconds
    with tempfile.TemporaryDirectory(prefix='studio-github-') as work: result=run_project(str(request_path),out,work,runner,deadline,clock,baseline_sha)
    automerge_status=_finish_persisted_evolution(out,runner,deadline,clock)
    summary={'status':result['status'],'next_stage':result.get('next_stage'),'finished':bool(result.get('report',{}).get('completion',{}).get('finished'))}
    for key in ('pending_status','research_status','synthesis_status','benchmark_status','promotion_status','persistence_status'):
        if result.get(key) is not None: summary[key]=result[key]
    if automerge_status is not None: summary['automerge_status']=automerge_status
    out.mkdir(parents=True,exist_ok=True); (out/'github-pipeline.json').write_text(canonical(summary)); return summary


def main(argv=None)->int:
    parser=argparse.ArgumentParser(); parser.add_argument('request'); parser.add_argument('--out',default='studio-output'); args=parser.parse_args(argv)
    if os.environ.get('GITHUB_REF')!='refs/heads/main': raise StudioError('Privileged GitHub generation requires main')
    if not enabled('github'): print('GitHub generation inactive'); return 0
    baseline_sha=os.environ.get('GITHUB_SHA','')
    if len(baseline_sha)!=40: raise StudioError('GitHub generation requires a full baseline commit SHA')
    os.environ['STUDIO_CI_PROVIDER']='github'; result=run(Path(args.request),Path(args.out),baseline_sha=baseline_sha); print(canonical(result)); return 0 if result['status'] in ('complete','disabled') else 1


if __name__=='__main__':
    try: sys.exit(main())
    except (StudioError,ValueError,OSError,json.JSONDecodeError) as exc:
        Path('studio-output').mkdir(exist_ok=True); Path('studio-output/github-pipeline-error.json').write_text(canonical({'status':'blocked','error':str(exc) if isinstance(exc,StudioError) else type(exc).__name__})); print('GitHub autonomous pipeline blocked; see artifact evidence.',file=sys.stderr); sys.exit(1)
