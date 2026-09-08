"""CircleCI queue adapter. Uses the same engine, budgets and remote checkpoints."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import uuid
from adaptation import write_adaptation_request
from ci_provider import enabled
from core import StudioError, canonical
from queue import matrix
from stage_registry import STAGES, get_stage

def bounded_run(args, timeout):
    run_id = uuid.uuid4().hex
    env = dict(os.environ, STUDIO_RUN_ID=run_id)
    process = subprocess.Popen(args, env=env, start_new_session=True)
    try:
        return subprocess.CompletedProcess(args, process.wait(timeout=timeout))
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGTERM)
            process.wait(timeout=10)
        except (ProcessLookupError, subprocess.TimeoutExpired):
            pass
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait()
        try:
            containers = subprocess.run(['docker', 'ps', '-aq', '--filter',
                'label=mobile-studio-run=' + run_id], capture_output=True, text=True,
                timeout=15, check=True).stdout.split()
            if containers:
                subprocess.run(['docker', 'rm', '-f', *containers],
                    capture_output=True, timeout=30, check=True)
        except (OSError, subprocess.SubprocessError):
            raise StudioError('Timed-out worker stopped but container cleanup failed') from None
        raise

def save_report(out, results):
    temporary = out / 'queue.json.tmp'
    temporary.write_text(canonical({'provider': 'circleci', 'projects': results}))
    temporary.replace(out / 'queue.json')

def _load_report(project_out):
    return json.loads((project_out / 'report.json').read_text())

def _run_registered_stages(project, project_out, work, report, deadline, runner, clock):
    seen = set()
    while True:
        completion = report.get('completion', {})
        if completion.get('finished'):
            return report, None
        name = completion.get('next_stage')
        stage = get_stage(name)
        if stage is None:
            request = write_adaptation_request(report, project_out, frozenset(STAGES))
            if request.get('status') == 'adaptation_required':
                return report, 'adaptation_required'
            raise StudioError('Unfinished project has no executable next stage')
        if name in seen:
            raise StudioError('Stage did not advance completion state: ' + name)
        seen.add(name)
        remaining = deadline - clock()
        if remaining <= 0:
            return report, stage.deferred_status
        result = runner([sys.executable, stage.script, project['file'],
            '--work', work, '--out', str(project_out)], timeout=remaining)
        if result.returncode != 0:
            return _load_report(project_out), stage.failed_status
        updated = _load_report(project_out)
        next_name = updated.get('completion', {}).get('next_stage')
        if next_name == name and not updated.get('completion', {}).get('finished'):
            raise StudioError('Successful stage did not advance completion state: ' + name)
        report = updated

def run_queue(directory='control/mobile-requests', out=Path('studio-output'),
              runner=bounded_run, clock=time.monotonic):
    projects = matrix(directory)
    out.mkdir(parents=True, exist_ok=True)
    results = [{'id': p['id'], 'status': 'pending'} for p in projects]
    save_report(out, results)
    deadline = clock() + 70 * 60
    for index, project in enumerate(projects):
        remaining = deadline - clock()
        if remaining <= 0:
            results[index]['status'] = 'deferred'
            save_report(out, results)
            continue
        results[index]['status'] = 'running'
        save_report(out, results)
        with tempfile.TemporaryDirectory(prefix='studio-ci-') as work:
            project_out = out / project['id']
            try:
                preview = runner([sys.executable, 'studio/run.py', project['file'],
                    '--work', work, '--out', str(project_out)], timeout=remaining)
                if preview.returncode != 0:
                    results[index]['status'] = 'failed'
                    continue

                remaining = deadline - clock()
                if remaining <= 0:
                    results[index]['status'] = 'deferred_release'
                    continue
                release = runner([sys.executable, 'studio/post_preview.py', project['file'],
                    '--work', work, '--out', str(project_out)], timeout=remaining)
                if release.returncode != 0:
                    results[index]['status'] = 'release_failed'
                    continue

                report, terminal_status = _run_registered_stages(
                    project, project_out, work, _load_report(project_out), deadline, runner, clock)
                if terminal_status:
                    results[index]['status'] = terminal_status
                    results[index]['next_stage'] = report.get('completion', {}).get('next_stage')
                    continue

                completion = report.get('completion', {})
                if not completion.get('finished'):
                    raise StudioError('Stage runner stopped before completion')
                results[index]['status'] = 'complete'
                results[index]['next_stage'] = None
            except subprocess.TimeoutExpired:
                results[index]['status'] = 'timed_out'
                deadline = 0
            except (OSError, StudioError, ValueError, json.JSONDecodeError):
                results[index]['status'] = 'worker_error'
                deadline = 0
            finally:
                save_report(out, results)
    save_report(out, results)
    return int(any(p['status'] != 'complete' for p in results))

def main():
    if os.environ.get('CIRCLE_BRANCH') != 'main':
        raise StudioError('Privileged CircleCI jobs require main')
    if not enabled('circleci'):
        print('CircleCI generation inactive')
        return 0
    os.environ['STUDIO_CI_PROVIDER'] = 'circleci'
    os.environ['GITHUB_REPOSITORY'] = '/'.join(
        os.environ.get(k, '') for k in ('CIRCLE_PROJECT_USERNAME', 'CIRCLE_PROJECT_REPONAME'))
    for dest, fallback in [('STUDIO_API_KEY', 'NVIDIA_NIM_API_KEY'), ('STUDIO_GITHUB_TOKEN', 'CODESPACES_PAT')]:
        if not os.environ.get(dest) and os.environ.get(fallback):
            os.environ[dest] = os.environ[fallback]
    mode = sys.argv[1] if len(sys.argv) == 2 else 'queue'
    if mode == 'queue':
        return run_queue()
    if mode == 'preview':
        import provider_probe
        return provider_probe.main()
    raise StudioError('Unsupported CircleCI generation mode')

if __name__ == '__main__':
    try:
        sys.exit(main())
    except (StudioError, ValueError, OSError) as e:
        Path('studio-output').mkdir(exist_ok=True)
        Path('studio-output/ci-error.json').write_text(canonical({
            'status': 'blocked', 'error': str(e) if isinstance(e, StudioError) else type(e).__name__}))
        print('CI adapter blocked; see ci-error.json', file=sys.stderr)
        sys.exit(1)
