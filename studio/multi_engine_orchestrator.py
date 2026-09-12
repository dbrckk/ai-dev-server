"""Route preview orchestration without weakening the existing Flutter pipeline."""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys

from core import StudioError
from orchestrator import load_report, run_project as run_flutter_project
from generic_project import run_project as run_generic_project


def _remaining(deadline, clock):
    value=deadline-clock()
    if value<=0: raise TimeoutError('Autonomous pipeline deadline exhausted')
    return value


def _detect(request_path,project_out,runner,deadline,clock):
    try: remaining=_remaining(deadline,clock)
    except TimeoutError: return None
    result=runner([sys.executable,'studio/engine_detect.py',request_path,'--out',str(project_out)],timeout=remaining)
    if result.returncode!=0: raise StudioError('Project engine detection failed')
    path=project_out/'engine-detection.json'
    if not path.is_file():
        if not os.environ.get('STUDIO_GITHUB_TOKEN') and (project_out/'report.json').is_file(): return 'flutter'
        raise StudioError('Engine detection produced no evidence')
    try: evidence=json.loads(path.read_text())
    except (OSError,json.JSONDecodeError): raise StudioError('Engine detection evidence is invalid') from None
    if not isinstance(evidence,dict) or evidence.get('status')!='detected' or evidence.get('engine') not in {'flutter','godot','generic'}: raise StudioError('Engine detection evidence is invalid')
    return evidence['engine']


def _run_stage(script,request_path,project_out,work,runner,deadline,clock):
    try: remaining=_remaining(deadline,clock)
    except TimeoutError: return None
    return runner([sys.executable,script,request_path,'--work',work,'--out',str(project_out)],timeout=remaining)


def run_project(request_path,project_out,work,runner,deadline,clock,baseline_sha=None):
    project_out.mkdir(parents=True,exist_ok=True)
    engine=_detect(request_path,project_out,runner,deadline,clock)
    if engine is None: return {'status':'deferred','report':{},'next_stage':'preview'}
    if engine=='flutter':
        return run_flutter_project(request_path,project_out,work,runner,deadline,clock,baseline_sha)
    if engine=='generic':
        try:
            req=json.loads(Path(request_path).read_text())
        except (OSError,json.JSONDecodeError):
            raise StudioError('Generic project request is unreadable') from None
        portfolio={}
        portfolio_path=project_out/'portfolio-research.json'
        if portfolio_path.is_file():
            try: portfolio=json.loads(portfolio_path.read_text())
            except (OSError,json.JSONDecodeError): portfolio={}
        return run_generic_project(req,project_out,Path(work),portfolio=portfolio,max_rounds=6)
    if engine!='godot': raise StudioError('Unsupported project engine')

    stages=[
        ('studio/engine_entry.py',work,'preview','godot_preview_validated','godot_android_export_qa'),
        ('studio/godot_android_stage.py',str(Path(work).with_name(Path(work).name+'-android')),'godot_android_export_qa','godot_android_export_validated','godot_device_qa'),
        ('studio/godot_device_stage.py',str(Path(work).with_name(Path(work).name+'-device')),'godot_device_qa','godot_device_validated','godot_runtime_journey_qa'),
        ('studio/godot_runtime_journey_stage.py',str(Path(work).with_name(Path(work).name+'-journeys')),'godot_runtime_journey_qa','godot_runtime_journeys_validated','godot_visual_qa'),
        ('studio/godot_visual_stage.py',str(Path(work).with_name(Path(work).name+'-visual')),'godot_visual_qa','godot_visual_validated','godot_release_qa'),
    ]
    report={}
    for script,stage_work,current_stage,expected_status,next_stage in stages:
        result=_run_stage(script,request_path,project_out,stage_work,runner,deadline,clock)
        if result is None: return {'status':'deferred','report':report,'next_stage':current_stage}
        report=load_report(project_out) if (project_out/'report.json').is_file() else {}
        if result.returncode!=0: return {'status':'failed','report':report,'next_stage':current_stage}
        completion=report.get('completion')
        if report.get('engine')!='godot' or report.get('status')!=expected_status: raise StudioError('Godot stage returned invalid report: '+current_stage)
        if not isinstance(completion,dict) or completion.get('finished') is not False or completion.get('next_stage')!=next_stage:
            raise StudioError('Godot stage returned invalid completion transition: '+current_stage)
        coverage=report.get('coverage') or {}
        if current_stage=='godot_device_qa' and (coverage.get('device_qa') is not True or coverage.get('journeys_executed') is not False or coverage.get('visual_qa') is not False):
            raise StudioError('Godot device stage returned invalid coverage evidence')
        if current_stage=='godot_runtime_journey_qa' and (coverage.get('device_qa') is not True or coverage.get('journeys_executed') is not True or coverage.get('visual_qa') is not False):
            raise StudioError('Godot journey stage returned invalid coverage evidence')
        if current_stage=='godot_visual_qa' and (coverage.get('device_qa') is not True or coverage.get('journeys_executed') is not True or coverage.get('visual_qa') is not True):
            raise StudioError('Godot visual stage returned invalid coverage evidence')

    release_work=str(Path(work).with_name(Path(work).name+'-release'))
    result=_run_stage('studio/godot_release_stage.py',request_path,project_out,release_work,runner,deadline,clock)
    if result is None: return {'status':'deferred','report':report,'next_stage':'godot_release_qa'}
    report=load_report(project_out) if (project_out/'report.json').is_file() else {}
    if result.returncode!=0: return {'status':'failed','report':report,'next_stage':'godot_release_qa'}
    completion=report.get('completion')
    if report.get('engine')!='godot' or not isinstance(completion,dict) or completion.get('finished') is not False:
        raise StudioError('Godot release stage returned invalid report')
    if report.get('status')=='godot_release_credentials_required':
        if completion.get('next_stage')!='godot_release_qa' or report.get('release_status')!='human_action_required':
            raise StudioError('Godot release credential state invalid')
        return {'status':'human_action_required','report':report,'next_stage':'godot_release_qa'}
    if report.get('status')!='godot_release_preflight_validated' or completion.get('next_stage')!='godot_release_artifact_qa':
        raise StudioError('Godot release stage returned invalid transition')

    artifact_work=str(Path(work).with_name(Path(work).name+'-release-artifact'))
    result=_run_stage('studio/godot_release_artifact_stage.py',request_path,project_out,artifact_work,runner,deadline,clock)
    if result is None: return {'status':'deferred','report':report,'next_stage':'godot_release_artifact_qa'}
    report=load_report(project_out) if (project_out/'report.json').is_file() else {}
    if result.returncode!=0: return {'status':'failed','report':report,'next_stage':'godot_release_artifact_qa'}
    completion=report.get('completion')
    if report.get('engine')!='godot' or not isinstance(completion,dict) or completion.get('finished') is not False:
        raise StudioError('Godot release artifact stage returned invalid report')
    if report.get('status')=='godot_release_credentials_required':
        if completion.get('next_stage')!='godot_release_qa' or report.get('release_status')!='human_action_required':
            raise StudioError('Godot artifact credential state invalid')
        return {'status':'human_action_required','report':report,'next_stage':'godot_release_qa'}
    coverage=report.get('coverage') or {}
    evidence=report.get('release_artifact')
    if (report.get('status')!='godot_release_artifact_validated' or completion.get('next_stage')!='godot_store_metadata_qa'
            or coverage.get('release_artifact') is not True or coverage.get('release_signed') is not True
            or not isinstance(evidence,dict) or evidence.get('project_code_had_signing_material') is not False):
        raise StudioError('Godot release artifact stage returned invalid transition')
    metadata_work=str(Path(work).with_name(Path(work).name+'-store-metadata'))
    result=_run_stage('studio/godot_store_metadata_stage.py',request_path,project_out,metadata_work,runner,deadline,clock)
    if result is None: return {'status':'deferred','report':report,'next_stage':'godot_store_metadata_qa'}
    report=load_report(project_out) if (project_out/'report.json').is_file() else {}
    if result.returncode!=0: return {'status':'failed','report':report,'next_stage':'godot_store_metadata_qa'}
    completion=report.get('completion'); coverage=report.get('coverage') or {}
    if (report.get('engine')!='godot' or report.get('status')!='godot_store_metadata_validated'
            or not isinstance(completion,dict) or completion.get('finished') is not False
            or completion.get('next_stage')!='godot_privacy_security_qa'
            or coverage.get('store_metadata') is not True):
        raise StudioError('Godot store metadata stage returned invalid transition')
    privacy_work=str(Path(work).with_name(Path(work).name+'-privacy-security'))
    result=_run_stage('studio/godot_privacy_security_stage.py',request_path,project_out,privacy_work,runner,deadline,clock)
    if result is None: return {'status':'deferred','report':report,'next_stage':'godot_privacy_security_qa'}
    report=load_report(project_out) if (project_out/'report.json').is_file() else {}
    if result.returncode!=0: return {'status':'failed','report':report,'next_stage':'godot_privacy_security_qa'}
    completion=report.get('completion'); coverage=report.get('coverage') or {}
    if (report.get('engine')!='godot' or report.get('status')!='godot_privacy_security_validated'
            or not isinstance(completion,dict) or completion.get('finished') is not False
            or completion.get('next_stage')!='godot_final_review_qa'
            or coverage.get('privacy_qa') is not True or coverage.get('security_qa') is not True):
        raise StudioError('Godot privacy/security stage returned invalid transition')
    final_work=str(Path(work).with_name(Path(work).name+'-final-review'))
    result=_run_stage('studio/godot_final_review_stage.py',request_path,project_out,final_work,runner,deadline,clock)
    if result is None: return {'status':'deferred','report':report,'next_stage':'godot_final_review_qa'}
    report=load_report(project_out) if (project_out/'report.json').is_file() else {}
    if result.returncode!=0: return {'status':'failed','report':report,'next_stage':'godot_final_review_qa'}
    completion=report.get('completion'); coverage=report.get('coverage') or {}
    if (report.get('engine')!='godot' or report.get('status')!='godot_technical_store_ready'
            or report.get('release_status')!='technical_store_ready'
            or not isinstance(completion,dict) or completion.get('finished') is not False
            or completion.get('next_stage')!='godot_play_submission'
            or coverage.get('final_review') is not True):
        raise StudioError('Godot final review stage returned invalid transition')
    return {'status':'human_action_required','report':report,'next_stage':'godot_play_submission'}
