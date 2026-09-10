"""Route preview orchestration without weakening the existing Flutter pipeline."""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys

from core import StudioError
from orchestrator import load_report, run_project as run_flutter_project


def _remaining(deadline, clock):
    value = deadline - clock()
    if value <= 0:
        raise TimeoutError('Autonomous pipeline deadline exhausted')
    return value


def _detect(request_path, project_out, runner, deadline, clock):
    try: remaining = _remaining(deadline, clock)
    except TimeoutError: return None
    result = runner([sys.executable,'studio/engine_detect.py',request_path,'--out',str(project_out)], timeout=remaining)
    if result.returncode != 0: raise StudioError('Project engine detection failed')
    path = project_out/'engine-detection.json'
    if not path.is_file():
        if not os.environ.get('STUDIO_GITHUB_TOKEN') and (project_out/'report.json').is_file(): return 'flutter'
        raise StudioError('Engine detection produced no evidence')
    try: evidence = json.loads(path.read_text())
    except (OSError,json.JSONDecodeError): raise StudioError('Engine detection evidence is invalid') from None
    if not isinstance(evidence,dict) or evidence.get('status')!='detected' or evidence.get('engine') not in {'flutter','godot'}:
        raise StudioError('Engine detection evidence is invalid')
    return evidence['engine']


def _run_stage(script, request_path, project_out, work, runner, deadline, clock):
    try: remaining=_remaining(deadline,clock)
    except TimeoutError: return None
    return runner([sys.executable,script,request_path,'--work',work,'--out',str(project_out)],timeout=remaining)


def run_project(request_path, project_out, work, runner, deadline, clock, baseline_sha=None):
    project_out.mkdir(parents=True,exist_ok=True)
    engine=_detect(request_path,project_out,runner,deadline,clock)
    if engine is None: return {'status':'deferred','report':{},'next_stage':'preview'}
    if engine=='flutter': return run_flutter_project(request_path,project_out,work,runner,deadline,clock,baseline_sha)
    if engine!='godot': raise StudioError('Unsupported project engine')

    preview=_run_stage('studio/engine_entry.py',request_path,project_out,work,runner,deadline,clock)
    if preview is None: return {'status':'deferred','report':{},'next_stage':'preview'}
    report=load_report(project_out) if (project_out/'report.json').is_file() else {}
    if preview.returncode!=0: return {'status':'failed','report':report,'next_stage':'preview'}
    completion=report.get('completion')
    if report.get('engine')!='godot' or not isinstance(completion,dict) or completion.get('finished') is not False:
        raise StudioError('Godot preview returned invalid completion evidence')
    if completion.get('next_stage')!='godot_android_export_qa': raise StudioError('Godot preview returned unexpected next stage')

    android_work=str(Path(work).with_name(Path(work).name+'-android'))
    android=_run_stage('studio/godot_android_stage.py',request_path,project_out,android_work,runner,deadline,clock)
    if android is None: return {'status':'deferred','report':report,'next_stage':'godot_android_export_qa'}
    report=load_report(project_out) if (project_out/'report.json').is_file() else {}
    if android.returncode!=0: return {'status':'failed','report':report,'next_stage':'godot_android_export_qa'}
    completion=report.get('completion')
    if report.get('engine')!='godot' or report.get('status')!='godot_android_export_validated': raise StudioError('Godot Android stage returned invalid report')
    if not isinstance(completion,dict) or completion.get('finished') is not False or completion.get('next_stage')!='godot_device_qa':
        raise StudioError('Godot Android stage must advance only to device QA')

    device_work=str(Path(work).with_name(Path(work).name+'-device'))
    device=_run_stage('studio/godot_device_stage.py',request_path,project_out,device_work,runner,deadline,clock)
    if device is None: return {'status':'deferred','report':report,'next_stage':'godot_device_qa'}
    report=load_report(project_out) if (project_out/'report.json').is_file() else {}
    if device.returncode!=0: return {'status':'failed','report':report,'next_stage':'godot_device_qa'}
    completion=report.get('completion')
    if report.get('engine')!='godot' or report.get('status')!='godot_device_validated': raise StudioError('Godot device stage returned invalid report')
    if not isinstance(completion,dict) or completion.get('finished') is not False or completion.get('next_stage')!='godot_runtime_journey_qa':
        raise StudioError('Godot device stage must advance only to runtime journey QA')
    coverage=report.get('coverage') or {}
    if coverage.get('device_qa') is not True or coverage.get('journeys_executed') is not False or coverage.get('visual_qa') is not False:
        raise StudioError('Godot device stage returned invalid coverage evidence')
    return {'status':'godot_device_ready','report':report,'next_stage':'godot_runtime_journey_qa'}
