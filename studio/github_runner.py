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

from autonomous_project import run_persistent_project
from capability_adaptation_state import new_state as new_capability_adaptation_state, record_research as record_capability_research
from adaptation_research import research_missing_capability
from repository_research_provider import build_repository_providers
from ci_provider import enabled
from continuous_improvement import assess as assess_improvements
from core import StudioError, canonical, request_check
from github_goal_store import RemoteStateError, persist_local, restore_local
from github_memory_store import GitHubMemoryError, persist_local as persist_memory_local, restore_local as restore_memory_local
from improvement_backlog import activate_next, load as load_improvement_backlog, merge_assessment, new_backlog, save as save_improvement_backlog
from improvement_executor import run_active_improvement, verified_project_cycle
from memory_lifecycle import ingest_run
from project_memory import load as load_project_memory, save as save_project_memory
from multi_engine_orchestrator import run_project as run_multi_engine_project
from run import GitHub as RepoGitHub


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


def _update_improvements(out: Path, goal_state: dict, project_state: dict) -> dict:
    out.mkdir(parents=True,exist_ok=True)
    assessment=assess_improvements(goal_state,project_state)
    (out/'continuous-improvement.json').write_text(canonical(assessment))
    backlog_path=out/'.autonomy/improvement-backlog.json'
    backlog=load_improvement_backlog(backlog_path) if backlog_path.is_file() else new_backlog()
    backlog=merge_assessment(backlog,assessment)
    backlog=activate_next(backlog)
    save_improvement_backlog(backlog_path,backlog)
    active=next((item for item in backlog['items'] if item['status']=='active'),None)
    return {
        'status':assessment['status'],
        'active_candidate':active['candidate']['id'] if active else None,
        'queued':sum(item['status']=='queued' for item in backlog['items']),
        'proved':sum(item['status']=='proved' for item in backlog['items']),
    }


def run(request_path:Path,out=Path('studio-output'),runner=bounded_run,clock=time.monotonic,budget_seconds=85*60,baseline_sha:str|None=None)->dict:
    request=request_check(json.loads(request_path.read_text()))
    if not request['enabled']:
        result={'status':'disabled','next_stage':None,'finished':False}; out.mkdir(parents=True,exist_ok=True); (out/'github-pipeline.json').write_text(canonical(result)); return result
    os.environ['STUDIO_PROJECT_ID']=request['id']
    deadline=clock()+budget_seconds
    remote_github=None
    if os.environ.get('STUDIO_PERSIST_REMOTE')=='1':
        control_repo=os.environ.get('GITHUB_REPOSITORY','')
        if not control_repo or '/' not in control_repo:
            raise StudioError('Remote autonomous persistence requires GITHUB_REPOSITORY')
        remote_github=RepoGitHub(control_repo)
        try:
            restore_local(remote_github,request['id'],out)
            restore_memory_local(remote_github,out/'.memory/memory.json')
        except RemoteStateError as exc:
            raise StudioError('Remote autonomous state restore failed: '+str(exc)) from None
        except GitHubMemoryError as exc:
            raise StudioError('Remote project memory restore failed: '+str(exc)) from None
    adaptation_path=out/'.autonomy/capability-adaptation.json'
    memory_path=out/'.memory/memory.json'
    registry_path=out/'.autonomy/capabilities.json'
    if adaptation_path.is_file():
        from capability_adaptation_state import validate as validate_capability_adaptation
        adaptation_state=validate_capability_adaptation(json.loads(adaptation_path.read_text()))
        if adaptation_state['status']=='research_required':
            if not isinstance(baseline_sha,str) or len(baseline_sha)!=40:
                raise StudioError('Capability research requires a pinned baseline SHA')
            memory=load_project_memory(memory_path)
            from capability_registry import load as load_capability_registry
            registry=load_capability_registry(registry_path)
            search_provider,fetch_provider=build_repository_providers(
                Path('.'),
                os.environ.get('GITHUB_REPOSITORY',''),
                baseline_sha,
                adaptation_state['capability'],
            )
            memory,_,research_state=research_missing_capability(
                memory,
                registry,
                request['id'],
                adaptation_state['capability'],
                search_provider,
                fetch_provider,
                min_sources=2,
            )
            save_project_memory(memory_path,memory)
            normalized=research_state.get('research_status')
            if normalized not in {'research_complete','research_incomplete'}:
                normalized='research_incomplete'
            adaptation_state=record_capability_research(adaptation_state,normalized)
            adaptation_path.write_text(canonical(adaptation_state))
    last_result={}
    def run_once(*args):
        result=run_multi_engine_project(*args)
        last_result.clear(); last_result.update(result)
        return result
    with tempfile.TemporaryDirectory(prefix='studio-github-') as work:
        state=run_persistent_project(
            str(request_path),out,work,runner,deadline,clock,baseline_sha,
            goal_id=request['id'],
            objective='Complete project '+request['id']+' with verified release evidence',
            max_cycles=4,
            run_once=run_once,
        )
    improvement=None
    improvement_run=None
    status=state.get('status')
    if status=='complete':
        project_state=last_result.get('report') if isinstance(last_result.get('report'),dict) else {}
        improvement=_update_improvements(out,state,project_state)
        backlog_path=out/'.autonomy/improvement-backlog.json'
        improvement_goal_path=out/'.autonomy/improvement-goal.json'
        registry_path=out/'.autonomy/capabilities.json'
        backlog=load_improvement_backlog(backlog_path)
        active=next((item for item in backlog['items'] if item['status']=='active'),None)
        if active is not None:
            candidate=active['candidate']
            def improvement_project_cycle(_goal_state):
                with tempfile.TemporaryDirectory(prefix='studio-improvement-') as improve_work:
                    return run_multi_engine_project(
                        str(request_path),out,improve_work,runner,deadline,clock,baseline_sha
                    )
            improvement_run=run_active_improvement(
                backlog_path,
                improvement_goal_path,
                registry_path,
                verified_project_cycle(candidate,improvement_project_cycle),
                max_cycles=2,
            )
    if remote_github is not None:
        try:
            persist_local(remote_github,request['id'],out)
            memory=load_project_memory(memory_path)
            memory=ingest_run(memory,request['id'],out)
            save_project_memory(memory_path,memory)
            persist_memory_local(remote_github,memory_path)
        except RemoteStateError as exc:
            raise StudioError('Remote autonomous state persistence failed: '+str(exc)) from None
        except GitHubMemoryError as exc:
            raise StudioError('Remote project memory persistence failed: '+str(exc)) from None
        except ValueError as exc:
            raise StudioError('Project memory ingestion failed: '+str(exc)) from None
    summary={
        'status':status,
        'next_stage':last_result.get('next_stage'),
        'finished':status=='complete',
    }
    if improvement is not None:
        summary['improvement_status']=improvement['status']
        summary['improvement_next']=improvement['active_candidate']
        summary['improvement_queued']=improvement['queued']
        summary['improvement_proved']=improvement['proved']
    if improvement_run is not None:
        summary['improvement_run_status']=improvement_run['status']
        summary['improvement_candidate']=improvement_run['candidate_id']
        summary['improvement_goal_status']=improvement_run['goal_status']
        if improvement_run.get('missing_capability'):
            missing=improvement_run['missing_capability']
            summary['improvement_missing_capability']=missing
            adaptation_state=new_capability_adaptation_state(
                request['id'],
                missing,
                improvement_run['candidate_id'],
            )
            adaptation_path.write_text(canonical(adaptation_state))
            summary['capability_adaptation_status']=adaptation_state['status']
            summary['capability_adaptation_candidate']=adaptation_state['adaptation_candidate_id']
    if status=='human_action_required':
        summary['next_stage']=state.get('human_action')
    elif status=='blocked':
        summary['next_stage']=state.get('blocked_reason')
    for key in ('pending_status','research_status','synthesis_status','benchmark_status','promotion_status','persistence_status','automerge_status'):
        if last_result.get(key) is not None: summary[key]=last_result[key]
    out.mkdir(parents=True,exist_ok=True); (out/'github-pipeline.json').write_text(canonical(summary)); return summary


def main(argv=None)->int:
    parser=argparse.ArgumentParser(); parser.add_argument('request'); parser.add_argument('--out',default='studio-output'); args=parser.parse_args(argv)
    if os.environ.get('GITHUB_REF')!='refs/heads/main': raise StudioError('Privileged GitHub generation requires main')
    if not enabled('github'): print('GitHub generation inactive'); return 0
    baseline_sha=os.environ.get('GITHUB_SHA','')
    if len(baseline_sha)!=40: raise StudioError('GitHub generation requires a full baseline commit SHA')
    os.environ['STUDIO_CI_PROVIDER']='github'; os.environ['STUDIO_PERSIST_REMOTE']='1'; result=run(Path(args.request),Path(args.out),baseline_sha=baseline_sha); print(canonical(result)); return 0 if result['status'] in ('complete','disabled') else 1


if __name__=='__main__':
    try: sys.exit(main())
    except (StudioError,ValueError,OSError,json.JSONDecodeError) as exc:
        Path('studio-output').mkdir(exist_ok=True); Path('studio-output/github-pipeline-error.json').write_text(canonical({'status':'blocked','error':str(exc) if isinstance(exc,StudioError) else type(exc).__name__})); print('GitHub autonomous pipeline blocked; see artifact evidence.',file=sys.stderr); sys.exit(1)
