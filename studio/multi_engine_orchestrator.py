"""Route preview orchestration without weakening the existing Flutter pipeline."""
from __future__ import annotations

import json
from pathlib import Path
import sys

from core import StudioError, request_check
from engine_entry import detect_engine
from orchestrator import load_report, run_project as run_flutter_project
from run import GitHub


def _remaining(deadline, clock):
    value = deadline - clock()
    if value <= 0:
        raise TimeoutError('Autonomous pipeline deadline exhausted')
    return value


def run_project(request_path, project_out, work, runner, deadline, clock, baseline_sha=None):
    """Keep Flutter on the mature pipeline; route existing Godot to its dedicated preview.

    Godot intentionally stops at godot_android_export_qa until that trusted stage exists.
    It must never fall through into Flutter post_preview/release/device stages.
    """
    request = request_check(json.loads(Path(request_path).read_text()))
    github = GitHub(request['target_repo'])
    engine = detect_engine(request, github)
    if engine == 'flutter':
        return run_flutter_project(request_path, project_out, work, runner, deadline, clock, baseline_sha)
    if engine != 'godot':
        raise StudioError('Unsupported project engine')
    project_out.mkdir(parents=True, exist_ok=True)
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
    next_stage = completion.get('next_stage')
    if next_stage != 'godot_android_export_qa':
        raise StudioError('Godot preview returned unexpected next stage')
    return {'status':'godot_preview_ready','report':report,'next_stage':next_stage}
