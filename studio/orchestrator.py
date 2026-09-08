"""Provider-neutral autonomous completion pipeline.

Runs one project from preview through release and every trusted registered stage.
The caller owns process isolation/timeouts and CI-provider policy; this module owns
stage order, advancement checks, completion semantics and adaptation handoff.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys
import time

from adaptation import write_adaptation_request
from core import StudioError
from evolution_executor import consume as consume_evolution_request
from stage_registry import STAGES, get_stage


def load_report(project_out: Path) -> dict:
    path = project_out / 'report.json'
    if not path.is_file():
        raise StudioError('Stage did not produce report.json')
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        raise StudioError('Stage produced invalid report.json') from None
    if not isinstance(value, dict):
        raise StudioError('Stage report must be an object')
    return value


def _remaining(deadline: float, clock) -> float:
    value = deadline - clock()
    if value <= 0:
        raise TimeoutError('Autonomous pipeline deadline exhausted')
    return value


def _write_adaptation_handoff(report: dict, project_out: Path, baseline_sha: str | None) -> dict:
    request = write_adaptation_request(report, project_out, frozenset(STAGES))
    if request.get('status') != 'adaptation_required':
        return request
    if not isinstance(baseline_sha, str) or not re.fullmatch(r'[0-9a-f]{40}', baseline_sha):
        raise StudioError('Adaptation requires a trusted control-repository baseline SHA')
    consume_evolution_request(project_out / 'evolution-request.json', project_out, baseline_sha)
    return request


def run_registered_stages(request_path: str, project_out: Path, work: str,
                          report: dict, deadline: float, runner, clock=time.monotonic,
                          baseline_sha: str | None = None) -> dict:
    seen: set[str] = set()
    while True:
        completion = report.get('completion', {})
        if not isinstance(completion, dict):
            raise StudioError('Completion report must be an object')
        if completion.get('finished'):
            return {'status': 'complete', 'report': report, 'next_stage': None}

        name = completion.get('next_stage')
        stage = get_stage(name) if isinstance(name, str) else None
        if stage is None:
            request = _write_adaptation_handoff(report, project_out, baseline_sha)
            if request.get('status') == 'adaptation_required':
                return {'status': 'adaptation_required', 'report': report, 'next_stage': name}
            raise StudioError('Unfinished project has no executable next stage')
        if name in seen:
            raise StudioError('Stage did not advance completion state: ' + name)
        seen.add(name)

        try:
            remaining = _remaining(deadline, clock)
        except TimeoutError:
            return {'status': stage.deferred_status, 'report': report, 'next_stage': name}
        result = runner([
            sys.executable, stage.script, request_path,
            '--work', work, '--out', str(project_out),
        ], timeout=remaining)
        if result.returncode != 0:
            return {'status': stage.failed_status, 'report': load_report(project_out), 'next_stage': name}

        updated = load_report(project_out)
        updated_completion = updated.get('completion', {})
        next_name = updated_completion.get('next_stage') if isinstance(updated_completion, dict) else None
        if next_name == name and not updated_completion.get('finished'):
            raise StudioError('Successful stage did not advance completion state: ' + name)
        report = updated


def run_project(request_path: str, project_out: Path, work: str, runner,
                deadline: float, clock=time.monotonic, baseline_sha: str | None = None) -> dict:
    """Run preview, release build, then every dynamically required trusted stage."""
    project_out.mkdir(parents=True, exist_ok=True)
    try:
        remaining = _remaining(deadline, clock)
    except TimeoutError:
        return {'status': 'deferred', 'report': {}, 'next_stage': 'preview'}

    preview = runner([
        sys.executable, 'studio/run.py', request_path,
        '--work', work, '--out', str(project_out),
    ], timeout=remaining)
    if preview.returncode != 0:
        report = load_report(project_out) if (project_out / 'report.json').is_file() else {}
        return {'status': 'failed', 'report': report, 'next_stage': 'preview'}

    try:
        remaining = _remaining(deadline, clock)
    except TimeoutError:
        return {'status': 'deferred_release', 'report': load_report(project_out), 'next_stage': 'release_build'}
    release = runner([
        sys.executable, 'studio/post_preview.py', request_path,
        '--work', work, '--out', str(project_out),
    ], timeout=remaining)
    if release.returncode != 0:
        return {'status': 'release_failed', 'report': load_report(project_out), 'next_stage': 'release_build'}

    return run_registered_stages(
        request_path, project_out, work, load_report(project_out), deadline,
        runner, clock, baseline_sha)
