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
from ci_provider import enabled
from core import StudioError, canonical
from queue import matrix

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

                report = json.loads((project_out / 'report.json').read_text())
                if report.get('completion', {}).get('next_stage') == 'real_device':
                    remaining = deadline - clock()
                    if remaining <= 0:
                        results[index]['status'] = 'deferred_device'
                        continue
                    device = runner([sys.executable, 'studio/device_stage.py', project['file'],
                        '--work', work, '--out', str(project_out)], timeout=remaining)
                    if device.returncode != 0:
                        results[index]['status'] = 'device_failed'
                        continue
                    report = json.loads((project_out / 'report.json').read_text())

                if report.get('completion', {}).get('next_stage') == 'store_metadata':
                    remaining = deadline - clock()
                    if remaining <= 0:
                        results[index]['status'] = 'deferred_store'
                        continue
                    store = runner([sys.executable, 'studio/store_stage.py', project['file'],
                        '--work', work, '--out', str(project_out)], timeout=remaining)
                    if store.returncode != 0:
                        results[index]['status'] = 'store_failed'
                        continue
                    report = json.loads((project_out / 'report.json').read_text())

                completion = report.get('completion', {})
                results[index]['status'] = 'complete' if completion.get('finished') else 'progressed'
                results[index]['next_stage'] = completion.get('next_stage')
            except subprocess.TimeoutExpired:
                results[index]['status'] = 'timed_out'
                deadline = 0
            except (OSError, StudioError, ValueError, json.JSONDecodeError):
                results[index]['status'] = 'worker_error'
                deadline = 0
            finally:
                save_report(out, results)
    save_report(out, results)
    acceptable = {'complete', 'progressed'}
    return int(any(p['status'] not in acceptable for p in results))

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
