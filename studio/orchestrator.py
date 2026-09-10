"""Provider-neutral autonomous completion pipeline."""
from __future__ import annotations
import json
import os
from pathlib import Path
import re
import sys
import time
from adaptation import write_adaptation_request
from core import StudioError
from evolution_executor import consume as consume_evolution_request
from stage_registry import STAGES,get_stage

def load_report(project_out):
    path=project_out/'report.json'
    if not path.is_file(): raise StudioError('Stage did not produce report.json')
    try: value=json.loads(path.read_text())
    except (OSError,json.JSONDecodeError): raise StudioError('Stage produced invalid report.json') from None
    if not isinstance(value,dict): raise StudioError('Stage report must be an object')
    return value

def _remaining(deadline,clock):
    value=deadline-clock()
    if value<=0: raise TimeoutError('Autonomous pipeline deadline exhausted')
    return value

def _write_adaptation_handoff(report,project_out,baseline_sha):
    request=write_adaptation_request(report,project_out,frozenset(STAGES))
    if request.get('status')!='adaptation_required': return request
    if isinstance(baseline_sha,str) and re.fullmatch(r'[0-9a-f]{40}',baseline_sha): consume_evolution_request(project_out/'evolution-request.json',project_out,baseline_sha)
    return request

def _run_adaptation_pending(project_out,deadline,runner,clock):
    if os.environ.get('STUDIO_CI_PROVIDER')!='github': return 'not_applicable'
    order=project_out/'evolution-work-order.json'
    if not order.is_file(): return 'not_ready'
    try: remaining=_remaining(deadline,clock)
    except TimeoutError: return 'deferred'
    result=runner([sys.executable,'studio/evolution_pending.py',str(order),'--out',str(project_out)],timeout=remaining)
    if result.returncode!=0: return 'blocked'
    path=project_out/'evolution-pending.json'
    if not path.is_file(): raise StudioError('Successful pending-promotion check produced no evidence')
    try: value=json.loads(path.read_text())
    except (OSError,json.JSONDecodeError): raise StudioError('Pending-promotion check produced invalid evidence') from None
    status=value.get('status')
    mapping={'no_pending_promotion':'none','promotion_pending_merge':'pending_merge','promotion_merged_restart_required':'restart_required','promotion_orphaned':'blocked','promotion_closed_without_merge':'blocked'}
    if status not in mapping: raise StudioError('Pending-promotion check returned invalid status')
    return mapping[status]

def _run_adaptation_research(project_out,deadline,runner,clock):
    order=project_out/'evolution-work-order.json'
    if not order.is_file(): return 'not_planned_without_baseline'
    try: remaining=_remaining(deadline,clock)
    except TimeoutError: return 'deferred'
    result=runner([sys.executable,'studio/evolution_research.py',str(order),'--out',str(project_out)],timeout=remaining)
    if result.returncode!=0: return 'blocked'
    evidence_path=project_out/'evolution-research.json'
    if not evidence_path.is_file(): raise StudioError('Successful evolution research produced no evidence')
    try: evidence=json.loads(evidence_path.read_text()); work_order=json.loads(order.read_text())
    except (OSError,json.JSONDecodeError): raise StudioError('Evolution research produced invalid evidence') from None
    if not isinstance(evidence,dict) or evidence.get('status')!='research_complete' or evidence.get('candidate_id')!=work_order.get('candidate_id'): raise StudioError('Evolution research evidence does not match work order')
    return 'complete'

def _run_adaptation_synthesis(project_out,deadline,runner,clock):
    order=project_out/'evolution-work-order.json'; research=project_out/'evolution-research.json'
    if not order.is_file() or not research.is_file(): return 'not_ready'
    try: remaining=_remaining(deadline,clock)
    except TimeoutError: return 'deferred'
    result=runner([sys.executable,'studio/evolution_synthesis.py',str(order),str(research),'--out',str(project_out)],timeout=remaining)
    if result.returncode!=0: return 'rejected'
    candidate_path=project_out/'evolution-candidate.json'
    if not candidate_path.is_file(): raise StudioError('Successful evolution synthesis produced no candidate')
    try: candidate=json.loads(candidate_path.read_text()); work_order=json.loads(order.read_text())
    except (OSError,json.JSONDecodeError): raise StudioError('Evolution synthesis produced invalid candidate evidence') from None
    if not isinstance(candidate,dict) or candidate.get('status')!='candidate_validated' or candidate.get('candidate_id')!=work_order.get('candidate_id'): raise StudioError('Evolution candidate does not match work order')
    return 'validated'

def _run_adaptation_benchmark(project_out,deadline,runner,clock):
    order=project_out/'evolution-work-order.json'; candidate=project_out/'evolution-candidate.json'
    if not order.is_file() or not candidate.is_file(): return 'not_ready'
    try: remaining=_remaining(deadline,clock)
    except TimeoutError: return 'deferred'
    result=runner([sys.executable,'studio/evolution_isolated_runner.py',str(order),str(candidate),'--repo-root','.','--out',str(project_out)],timeout=remaining)
    if result.returncode!=0: return 'blocked'
    promotion_path=project_out/'evolution-promotion.json'; benchmark_path=project_out/'evolution-isolated-benchmark.json'
    if not promotion_path.is_file() or not benchmark_path.is_file(): raise StudioError('Successful isolated benchmark produced incomplete evidence')
    try: promotion=json.loads(promotion_path.read_text()); work_order=json.loads(order.read_text())
    except (OSError,json.JSONDecodeError): raise StudioError('Isolated benchmark produced invalid promotion evidence') from None
    if not isinstance(promotion,dict) or promotion.get('candidate_id')!=work_order.get('candidate_id'): raise StudioError('Promotion evidence does not match work order')
    if promotion.get('status')=='promotion_approved' and promotion.get('promotion_decision')=='approve': return 'approved'
    if promotion.get('status')=='promotion_rejected' and promotion.get('promotion_decision')=='reject': return 'rejected'
    raise StudioError('Promotion evidence has invalid decision state')

def _run_adaptation_promotion(project_out,deadline,runner,clock):
    paths=[project_out/name for name in ('evolution-work-order.json','evolution-candidate.json','evolution-isolated-benchmark.json','evolution-promotion.json')]
    if not all(path.is_file() for path in paths): return 'not_ready'
    try: remaining=_remaining(deadline,clock)
    except TimeoutError: return 'deferred'
    result=runner([sys.executable,'studio/evolution_promotion.py',str(paths[0]),str(paths[1]),str(paths[2]),str(paths[3]),'--repo-root','.','--out',str(project_out)],timeout=remaining)
    if result.returncode!=0: return 'blocked'
    applied=project_out/'evolution-applied.json'
    if not applied.is_file(): raise StudioError('Successful promotion produced no application evidence')
    try: value=json.loads(applied.read_text())
    except (OSError,json.JSONDecodeError): raise StudioError('Promotion produced invalid application evidence') from None
    return 'promoted' if value.get('status') in {'promoted','already_promoted'} else 'blocked'

def _run_adaptation_persistence(project_out,deadline,runner,clock):
    if os.environ.get('STUDIO_CI_PROVIDER')!='github': return 'not_applicable'
    applied=project_out/'evolution-applied.json'
    if not applied.is_file(): return 'not_ready'
    try: remaining=_remaining(deadline,clock)
    except TimeoutError: return 'deferred'
    result=runner([sys.executable,'studio/evolution_persist.py',str(applied),'--repo-root','.','--out',str(project_out)],timeout=remaining)
    if result.returncode!=0: return 'blocked'
    persisted=project_out/'evolution-persisted.json'
    if not persisted.is_file(): raise StudioError('Successful persistence produced no evidence')
    try: value=json.loads(persisted.read_text())
    except (OSError,json.JSONDecodeError): raise StudioError('Persistence produced invalid evidence') from None
    return 'persisted' if value.get('status') in {'promotion_persisted','already_persisted'} else 'blocked'

def _run_adaptation_automerge(project_out,deadline,runner,clock):
    if os.environ.get('STUDIO_CI_PROVIDER')!='github': return 'not_applicable'
    order=project_out/'evolution-work-order.json'; persisted=project_out/'evolution-persisted.json'
    if not order.is_file(): return 'not_ready'
    try: remaining=_remaining(deadline,clock)
    except TimeoutError: return 'deferred'
    wait_seconds=max(0,min(int(remaining)-5,20*60))
    if wait_seconds<=0: return 'deferred'
    args=[sys.executable,'studio/evolution_automerge.py',str(order)]
    if persisted.is_file(): args.append(str(persisted))
    args.extend(['--out',str(project_out),'--wait-seconds',str(wait_seconds)])
    result=runner(args,timeout=remaining)
    if result.returncode!=0: return 'blocked'
    path=project_out/'evolution-automerge.json'
    if not path.is_file(): raise StudioError('Successful auto-merge produced no evidence')
    try: value=json.loads(path.read_text())
    except (OSError,json.JSONDecodeError): raise StudioError('Auto-merge produced invalid evidence') from None
    status=value.get('status')
    if status in {'promotion_merged','promotion_already_merged'}: return 'merged'
    if status in {'awaiting_required_checks','awaiting_clean_merge_state'}: return 'awaiting_checks'
    raise StudioError('Auto-merge produced invalid status')

def _stage_command(name,stage,request_path,work,project_out):
    args=[request_path,'--work',work,'--out',str(project_out)]
    if name in STAGES: return [sys.executable,stage.script,*args]
    return [sys.executable,'studio/evolution_stage_runner.py',stage.script,*args]

def run_registered_stages(request_path,project_out,work,report,deadline,runner,clock=time.monotonic,baseline_sha=None):
    seen=set()
    while True:
        completion=report.get('completion',{})
        if not isinstance(completion,dict): raise StudioError('Completion report must be an object')
        if completion.get('finished'): return {'status':'complete','report':report,'next_stage':None}
        name=completion.get('next_stage'); stage=get_stage(name) if isinstance(name,str) else None
        if stage is None:
            request=_write_adaptation_handoff(report,project_out,baseline_sha)
            if request.get('status')=='adaptation_required':
                pending_status=_run_adaptation_pending(project_out,deadline,runner,clock)
                if pending_status=='pending_merge':
                    automerge_status=_run_adaptation_automerge(project_out,deadline,runner,clock)
                    return {'status':'adaptation_required','report':report,'next_stage':name,'pending_status':'restart_required' if automerge_status=='merged' else 'pending_merge','research_status':'not_started','synthesis_status':'not_ready','benchmark_status':'not_ready','promotion_status':'not_ready','persistence_status':'awaiting_merge','automerge_status':automerge_status}
                if pending_status in {'restart_required','blocked','deferred'}:
                    return {'status':'adaptation_required','report':report,'next_stage':name,'pending_status':pending_status,'research_status':'not_started','synthesis_status':'not_ready','benchmark_status':'not_ready','promotion_status':'not_ready','persistence_status':'awaiting_merge' if pending_status=='restart_required' else pending_status,'automerge_status':'already_merged' if pending_status=='restart_required' else pending_status}
                research_status=_run_adaptation_research(project_out,deadline,runner,clock); synthesis_status='not_ready'; benchmark_status='not_ready'; promotion_status='not_ready'; persistence_status='not_ready'; automerge_status='not_ready'
                if research_status=='complete': synthesis_status=_run_adaptation_synthesis(project_out,deadline,runner,clock)
                if synthesis_status=='validated': benchmark_status=_run_adaptation_benchmark(project_out,deadline,runner,clock)
                if benchmark_status=='approved': promotion_status=_run_adaptation_promotion(project_out,deadline,runner,clock)
                if promotion_status=='promoted': persistence_status=_run_adaptation_persistence(project_out,deadline,runner,clock)
                if persistence_status=='persisted': automerge_status=_run_adaptation_automerge(project_out,deadline,runner,clock)
                if os.environ.get('STUDIO_CI_PROVIDER')=='github':
                    return {'status':'adaptation_required','report':report,'next_stage':name,'pending_status':'restart_required' if automerge_status=='merged' else pending_status,'research_status':research_status,'synthesis_status':synthesis_status,'benchmark_status':benchmark_status,'promotion_status':promotion_status,'persistence_status':persistence_status,'automerge_status':automerge_status}
                if promotion_status=='promoted' and persistence_status=='not_applicable':
                    stage=get_stage(name)
                    if stage is None: raise StudioError('Promoted stage was not registered')
                else:
                    return {'status':'adaptation_required','report':report,'next_stage':name,'pending_status':pending_status,'research_status':research_status,'synthesis_status':synthesis_status,'benchmark_status':benchmark_status,'promotion_status':promotion_status,'persistence_status':persistence_status,'automerge_status':automerge_status}
            else: raise StudioError('Unfinished project has no executable next stage')
        if name in seen: raise StudioError('Stage did not advance completion state: '+name)
        seen.add(name)
        try: remaining=_remaining(deadline,clock)
        except TimeoutError: return {'status':stage.deferred_status,'report':report,'next_stage':name}
        result=runner(_stage_command(name,stage,request_path,work,project_out),timeout=remaining)
        if result.returncode!=0: return {'status':stage.failed_status,'report':load_report(project_out),'next_stage':name}
        updated=load_report(project_out); updated_completion=updated.get('completion',{}); next_name=updated_completion.get('next_stage') if isinstance(updated_completion,dict) else None
        if next_name==name and not updated_completion.get('finished'): raise StudioError('Successful stage did not advance completion state: '+name)
        report=updated

def run_project(request_path,project_out,work,runner,deadline,clock=time.monotonic,baseline_sha=None):
    project_out.mkdir(parents=True,exist_ok=True)
    try: remaining=_remaining(deadline,clock)
    except TimeoutError: return {'status':'deferred','report':{},'next_stage':'preview'}
    preview=runner([sys.executable,'studio/run.py',request_path,'--work',work,'--out',str(project_out)],timeout=remaining)
    if preview.returncode!=0:
        report=load_report(project_out) if (project_out/'report.json').is_file() else {}; return {'status':'failed','report':report,'next_stage':'preview'}
    try: remaining=_remaining(deadline,clock)
    except TimeoutError: return {'status':'deferred_release','report':load_report(project_out),'next_stage':'release_build'}
    release=runner([sys.executable,'studio/post_preview.py',request_path,'--work',work,'--out',str(project_out)],timeout=remaining)
    if release.returncode!=0: return {'status':'release_failed','report':load_report(project_out),'next_stage':'release_build'}
    return run_registered_stages(request_path,project_out,work,load_report(project_out),deadline,runner,clock,baseline_sha)
