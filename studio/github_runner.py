"""GitHub Actions adapter for the provider-neutral autonomous completion pipeline."""
from __future__ import annotations

import argparse
import hashlib
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
from capability_adaptation_state import new_state as new_capability_adaptation_state, record_research as record_capability_research, record_synthesis as record_capability_synthesis, record_validation as record_capability_validation, record_candidate_persistence as record_capability_candidate_persistence, record_registry_promotion_persistence as record_capability_registry_promotion_persistence
from adaptation_research import research_missing_capability
from repository_research_provider import build_repository_providers
from generic_capability_synthesis import synthesize_from_memory
from generic_capability_isolated_validation import validate_in_isolation, validate_isolated_validation_result
from capability_synthesis import validate_candidate_envelope
from generic_capability_persist import persist as persist_generic_capability_candidate, GenericCapabilityPersistError
from capability_review import inspect as inspect_capability_review, CapabilityReviewError
from capability_registry_promotion_persist import persist as persist_capability_registry_promotion, CapabilityRegistryPromotionPersistError
from ci_provider import enabled
from continuous_improvement import assess as assess_improvements
from core import StudioError, canonical, request_check
from github_goal_store import RemoteStateError, persist_local, restore_local
from goal_engine import load as load_goal_state, resume_human_action, save as save_goal_state
from github_memory_store import GitHubMemoryError, persist_local as persist_memory_local, restore_local as restore_memory_local
from github_agent_performance_store import AgentPerformanceStoreError, persist_local as persist_agent_performance_local, restore_local as restore_agent_performance_local
from improvement_backlog import activate_next, load as load_improvement_backlog, merge_assessment, new_backlog, save as save_improvement_backlog
from improvement_executor import run_active_improvement, verified_project_cycle
from human_input_request import prerequisite_satisfied, requires_human_input, write_request as write_human_input_request
from memory_lifecycle import ingest_run
from project_memory import load as load_project_memory, save as save_project_memory
from portfolio_scan import scan as scan_portfolio
from multi_engine_orchestrator import run_project as run_multi_engine_project
from run import GitHub as RepoGitHub


def _prepare_capability_promotion_handoff(out: Path, adaptation_state: dict, baseline_sha: str) -> dict:
    if adaptation_state.get('status')!='promotion_required' or adaptation_state.get('promotion_status')!='eligible':
        raise StudioError('Capability promotion handoff requires eligible promotion state')
    if not isinstance(baseline_sha,str) or len(baseline_sha)!=40 or any(ch not in '0123456789abcdef' for ch in baseline_sha):
        raise StudioError('Capability promotion handoff requires pinned baseline SHA')
    candidate_path=out/'.autonomy/capability-candidate.json'
    validation_path=out/'.autonomy/capability-validation.json'
    if not candidate_path.is_file() or not validation_path.is_file():
        raise StudioError('Capability promotion handoff requires persisted candidate and validation')
    candidate=validate_candidate_envelope(json.loads(candidate_path.read_text()))
    validation=validate_isolated_validation_result(json.loads(validation_path.read_text()))
    candidate_id=candidate.get('candidate_id')
    candidate_sha=candidate.get('candidate_sha256')
    if validation.get('candidate_id')!=candidate_id or validation.get('candidate_sha256')!=candidate_sha:
        raise StudioError('Capability promotion handoff candidate mismatch')
    if validation.get('validation',{}).get('status')!='candidate_validated':
        raise StudioError('Capability promotion handoff requires validated candidate')
    if adaptation_state.get('synthesis_status')!='candidate_synthesized:'+candidate_sha:
        raise StudioError('Capability promotion handoff adaptation mismatch')
    payload=candidate.get('candidate',{})
    if payload.get('capability')!=adaptation_state.get('capability'):
        raise StudioError('Capability promotion handoff capability mismatch')
    handoff={
        'status':'promotion_required',
        'capability':adaptation_state['capability'],
        'candidate_id':candidate_id,
        'candidate_sha256':candidate_sha,
        'provider':payload.get('provider'),
        'baseline_sha':baseline_sha,
        'validation_report_sha256':validation.get('report_sha256'),
        'candidate_materialized_in_trusted_repo':False,
        'capability_registered':False,
        'next_action':'persist_candidate_on_dedicated_branch_then_prepare_promotion',
    }
    handoff['handoff_sha256']=hashlib.sha256(canonical(handoff).encode()).hexdigest()
    path=out/'.autonomy/capability-promotion-handoff.json'
    path.write_text(canonical(handoff))
    return handoff


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
    # Every autonomous project starts by examining the owner's portfolio for
    # related work that can accelerate architecture, implementation or testing.
    try:
        portfolio_api=RepoGitHub(request['target_repo'])
        scan_portfolio(request['target_repo'],request['brief'],out,portfolio_api)
    except (StudioError,ValueError,OSError) as exc:
        out.mkdir(parents=True,exist_ok=True)
        (out/'portfolio-research.json').write_text(canonical({
            'status':'unavailable',
            'target_repo':request['target_repo'],
            'error':type(exc).__name__,
            'similar':[],
        }))
    remote_github=None
    if os.environ.get('STUDIO_PERSIST_REMOTE')=='1':
        control_repo=os.environ.get('GITHUB_REPOSITORY','')
        if not control_repo or '/' not in control_repo:
            raise StudioError('Remote autonomous persistence requires GITHUB_REPOSITORY')
        remote_github=RepoGitHub(control_repo)
        try:
            restore_local(remote_github,request['id'],out)
            restore_memory_local(remote_github,out/'.memory/memory.json')
            restore_agent_performance_local(remote_github,out/'.autonomy/agent-performance.json')
        except RemoteStateError as exc:
            raise StudioError('Remote autonomous state restore failed: '+str(exc)) from None
        except GitHubMemoryError as exc:
            raise StudioError('Remote project memory restore failed: '+str(exc)) from None
        except AgentPerformanceStoreError as exc:
            raise StudioError('Remote agent performance restore failed: '+str(exc)) from None
    goal_path=out/'.autonomy/goal.json'
    if goal_path.is_file():
        try:
            goal_state=load_goal_state(goal_path)
            if goal_state.get('status')=='human_action_required' and prerequisite_satisfied(str(goal_state.get('human_action') or '')):
                save_goal_state(goal_path,resume_human_action(goal_state))
                (out/'USER_INPUT_REQUIRED.txt').unlink(missing_ok=True)
                (out/'user-input-required.json').unlink(missing_ok=True)
        except ValueError as exc:
            raise StudioError('Autonomous goal resume check failed: '+str(exc)) from None
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
        if adaptation_state['status']=='synthesis_required':
            memory=load_project_memory(memory_path)
            candidate=synthesize_from_memory(
                memory,
                request['id'],
                adaptation_state['capability'],
            )
            candidate_path=out/'.autonomy/capability-candidate.json'
            candidate_path.write_text(canonical(candidate))
            adaptation_state=record_capability_synthesis(
                adaptation_state,
                candidate['candidate_sha256'],
            )
            adaptation_path.write_text(canonical(adaptation_state))
        if adaptation_state['status']=='validation_required':
            candidate_path=out/'.autonomy/capability-candidate.json'
            if not candidate_path.is_file():
                raise StudioError('Capability validation requires persisted candidate')
            candidate=json.loads(candidate_path.read_text())
            validation_report=validate_in_isolation(candidate,Path('.'))
            validation_path=out/'.autonomy/capability-validation.json'
            validation_path.write_text(canonical(validation_report))
            decision=validation_report.get('validation',{}).get('status')
            adaptation_state=record_capability_validation(adaptation_state,decision)
            adaptation_path.write_text(canonical(adaptation_state))
        if adaptation_state['status']=='promotion_required':
            handoff=_prepare_capability_promotion_handoff(out,adaptation_state,baseline_sha)
            candidate_persistence=None
            if remote_github is not None:
                try:
                    candidate=json.loads((out/'.autonomy/capability-candidate.json').read_text())
                    validation=json.loads((out/'.autonomy/capability-validation.json').read_text())
                    candidate_persistence=persist_generic_capability_candidate(
                        remote_github,candidate,validation,handoff,baseline_sha
                    )
                    adaptation_state=record_capability_candidate_persistence(
                        adaptation_state,candidate_persistence['status']
                    )
                    adaptation_path.write_text(canonical(adaptation_state))
                    review={
                        'status':candidate_persistence['status'],
                        'candidate_id':candidate_persistence['candidate_id'],
                        'candidate_sha256':candidate_persistence['candidate_sha256'],
                        'capability':candidate_persistence['capability'],
                        'branch':candidate_persistence['branch'],
                        'commit_sha':candidate_persistence['commit_sha'],
                        'pull_request':candidate_persistence['pull_request'],
                    }
                    (out/'.autonomy/capability-review.json').write_text(canonical(review))
                    persist_local(remote_github,request['id'],out)
                except GenericCapabilityPersistError as exc:
                    raise StudioError('Capability candidate persistence failed: '+str(exc)) from None
                except RemoteStateError as exc:
                    raise StudioError('Remote autonomous state persistence failed: '+str(exc)) from None
            summary={
                'status':'adaptation_required',
                'next_stage':adaptation_state['capability'],
                'finished':False,
                'capability_adaptation_status':adaptation_state['status'],
                'promotion_status':adaptation_state['promotion_status'],
                'promotion_handoff_sha256':handoff['handoff_sha256'],
            }
            if candidate_persistence is not None:
                summary['candidate_persistence_status']=candidate_persistence['status']
                summary['candidate_pull_request']=candidate_persistence['pull_request']
                summary['candidate_commit_sha']=candidate_persistence['commit_sha']
            out.mkdir(parents=True,exist_ok=True)
            (out/'github-pipeline.json').write_text(canonical(summary))
            return summary
    if adaptation_path.is_file():
        from capability_adaptation_state import validate as validate_capability_adaptation
        waiting=validate_capability_adaptation(json.loads(adaptation_path.read_text()))
        if waiting['status']=='awaiting_merge':
            review_status=None
            if remote_github is not None:
                review_path=out/'.autonomy/capability-review.json'
                if not review_path.is_file():
                    raise StudioError('Awaiting capability review requires persisted review identity')
                try:
                    review_status=inspect_capability_review(
                        remote_github,json.loads(review_path.read_text())
                    )
                except CapabilityReviewError as exc:
                    raise StudioError('Capability candidate review verification failed: '+str(exc)) from None
            summary={
                'status':'adaptation_required',
                'next_stage':waiting['capability'],
                'finished':False,
                'capability_adaptation_status':'awaiting_merge',
                'promotion_status':'candidate_review_required',
            }
            if review_status is not None:
                summary['candidate_review_status']=review_status['status']
                summary['candidate_pull_request']=review_status['pull_request']
                if review_status.get('merge_commit_sha') is not None:
                    summary['candidate_merge_commit_sha']=review_status['merge_commit_sha']
                if review_status.get('status')=='candidate_merged':
                    try:
                        candidate=json.loads((out/'.autonomy/capability-candidate.json').read_text())
                        validation=json.loads((out/'.autonomy/capability-validation.json').read_text())
                        review=json.loads((out/'.autonomy/capability-review.json').read_text())
                        registry_promotion=persist_capability_registry_promotion(
                            remote_github,candidate,validation,review,review_status,baseline_sha
                        )
                    except CapabilityRegistryPromotionPersistError as exc:
                        raise StudioError('Capability registry promotion persistence failed: '+str(exc)) from None
                    summary['registry_promotion_status']=registry_promotion['status']
                    if registry_promotion.get('pull_request') is not None:
                        summary['registry_promotion_pull_request']=registry_promotion['pull_request']
                    if registry_promotion.get('commit_sha') is not None:
                        summary['registry_promotion_commit_sha']=registry_promotion['commit_sha']
                    if registry_promotion['status'] in {'registry_promotion_persisted','registry_promotion_already_persisted'}:
                        waiting=record_capability_registry_promotion_persistence(
                            waiting,registry_promotion['status']
                        )
                        adaptation_path.write_text(canonical(waiting))
                        registry_review={
                            'status':registry_promotion['status'],
                            'candidate_id':registry_promotion['candidate_id'],
                            'candidate_sha256':registry_promotion['candidate_sha256'],
                            'capability':registry_promotion['capability'],
                            'candidate_merge_sha':registry_promotion['candidate_merge_sha'],
                            'branch':registry_promotion['branch'],
                            'commit_sha':registry_promotion['commit_sha'],
                            'pull_request':registry_promotion['pull_request'],
                        }
                        (out/'.autonomy/capability-registry-review.json').write_text(canonical(registry_review))
                        persist_local(remote_github,request['id'],out)
                        summary['capability_adaptation_status']='awaiting_registry_merge'
                        summary['promotion_status']='registry_review_required'
            out.mkdir(parents=True,exist_ok=True)
            (out/'github-pipeline.json').write_text(canonical(summary))
            return summary
    if adaptation_path.is_file():
        from capability_adaptation_state import validate as validate_capability_adaptation
        registry_waiting=validate_capability_adaptation(json.loads(adaptation_path.read_text()))
        if registry_waiting['status']=='awaiting_registry_merge':
            summary={
                'status':'adaptation_required',
                'next_stage':registry_waiting['capability'],
                'finished':False,
                'capability_adaptation_status':'awaiting_registry_merge',
                'promotion_status':'registry_review_required',
            }
            out.mkdir(parents=True,exist_ok=True)
            (out/'github-pipeline.json').write_text(canonical(summary))
            return summary
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
            # Memory ingestion must happen before autonomous-state persistence so
            # every validated artifact produced during this run is durably
            # checkpointed before the runner exits.
            memory=load_project_memory(memory_path)
            memory=ingest_run(memory,request['id'],out)
            save_project_memory(memory_path,memory)
            persist_local(remote_github,request['id'],out)
            persist_memory_local(remote_github,memory_path)
            persist_agent_performance_local(remote_github,out/'.autonomy/agent-performance.json')
        except RemoteStateError as exc:
            raise StudioError('Remote autonomous state persistence failed: '+str(exc)) from None
        except GitHubMemoryError as exc:
            raise StudioError('Remote project memory persistence failed: '+str(exc)) from None
        except AgentPerformanceStoreError as exc:
            raise StudioError('Remote agent performance persistence failed: '+str(exc)) from None
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
        write_human_input_request(
            out,
            request['id'],
            str(state.get('human_action') or 'external_human_action'),
            target_repo=request.get('target_repo'),
        )
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
        out=Path('studio-output'); out.mkdir(exist_ok=True)
        detail=str(exc) if isinstance(exc,StudioError) else type(exc).__name__
        Path(out/'github-pipeline-error.json').write_text(canonical({'status':'blocked','error':detail}))
        if requires_human_input(detail):
            project_id=os.environ.get('STUDIO_PROJECT_ID','unknown-project')
            target_repo=None
            request_path=os.environ.get('STUDIO_REQUEST')
            if request_path:
                try:
                    request=json.loads(Path(request_path).read_text())
                    project_id=str(request.get('id') or project_id)
                    target_repo=request.get('target_repo')
                except (OSError,json.JSONDecodeError,TypeError):
                    pass
            write_human_input_request(out,project_id,detail,target_repo=target_repo)
        print('GitHub autonomous pipeline blocked; see artifact evidence.',file=sys.stderr); sys.exit(1)
