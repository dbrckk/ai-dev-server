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
    try:
        remaining = _remaining(deadline, clock)
    except TimeoutError:
        return None
    result = runner([sys.executable,'studio/engine_detect.py',request_path,'--out',str(project_out)], timeout=remaining)
    if result.returncode != 0:
        raise StudioError('Project engine detection failed')
    path = project_out/'engine-detection.json'
    if not path.is_file():
        if not os.environ.get('STUDIO_GITHUB_TOKEN') and (project_out/'report.json').is_file():
            return 'flutter'
        raise StudioError('Engine detection produced no evidence')
    try:
        evidence = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        raise StudioError('Engine detection evidence is invalid') from None
    if not isinstance(evidence, dict) or evidence.get('status') != 'detected' or evidence.get('engine') not in {'flutter','godot'}:
        raise StudioError('Engine detection evidence is invalid')
    return evidence['engine']


def run_project(request_path, project_out, work, runner, deadline, clock, baseline_sha=None):
    project_out.mkdir(parents=True, exist_ok=True)
    engine = _detect(request_path, project_out, runner, deadline, clock)
    if engine is None:
        return {'status':'deferred','report':{},'next_stage':'preview'}
    if engine == 'flutter':
        return run_flutter_project(request_path, project_out, work, runner, deadline, clock, baseline_sha)
    if engine != 'godot':
        raise StudioError('Unsupported project engine')

    try:
        remaining = _remaining(deadline, clock)
    except TimeoutError:
        return {'status':'deferred','report':{},'next_stage':'preview'}
    preview = runner([sys.executable,'studio/engine_entry.py',request_path,'--work',work,'--out',str(project_out)], timeout=remaining)
    report = load_report(project_out) if (project_out/'report.json').is_file() else {}
    if preview.returncode != 0:
        return {'status':'failed','report':report,'next_stage':'preview'}
    if report.get('engine') != 'godot':
        raise StudioError('Godot preview returned wrong engine')
    completion = report.get('completion')
    if not isinstance(completion, dict) or completion.get('finished') is not False:
        raise StudioError('Godot preview must remain unfinished before Android/device QA')
    if completion.get('next_stage') != 'godot_android_export_qa':
        raise StudioError('Godot preview returned unexpected next stage')

    try:
        remaining = _remaining(deadline, clock)
    except TimeoutError:
        return {'status':'deferred','report':report,'next_stage':'godot_android_export_qa'}
    android_work = str(Path(work).with_name(Path(work).name + '-android'))
    android = runner([sys.executable,'studio/godot_android_stage.py',request_path,'--work',android_work,'--out',str(project_out)], timeout=remaining)
    report = load_report(project_out) if (project_out/'report.json').is_file() else {}
    if android.returncode != 0:
        return {'status':'failed','report':report,'next_stage':'godot_android_export_qa'}
    completion = report.get('completion')
    if report.get('engine') != 'godot' or report.get('status') != 'godot_android_export_validated':
        raise StudioError('Godot Android stage returned invalid report')
    if not isinstance(completion, dict) or completion.get('finished') is not False or completion.get('next_stage') != 'godot_device_qa':
        raise StudioError('Godot Android stage must advance only to device QA')
    return {'status':'godot_android_ready','report':report,'next_stage':'godot_device_qa'}
