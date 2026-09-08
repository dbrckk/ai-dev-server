"""CircleCI queue adapter. Uses the same engine, budgets and remote checkpoints."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from ci_provider import enabled
from core import StudioError, canonical
from queue import matrix

def run_queue(directory='control/mobile-requests', out=Path('studio-output'),
              runner=subprocess.run, clock=time.monotonic):
    projects = matrix(directory)  # Validate every request before any side effect.
    out.mkdir(parents=True, exist_ok=True)
    results = []
    deadline = clock() + 70 * 60
    for project in projects:
        remaining = deadline - clock()
        if remaining <= 0:
            results.append({'id': project['id'], 'status': 'deferred'})
            continue
        with tempfile.TemporaryDirectory(prefix='studio-ci-') as work:
            try:
                result = runner([sys.executable, 'studio/run.py', project['file'],
                    '--work', work, '--out', str(out / project['id'])], timeout=remaining)
                results.append({'id': project['id'], 'status': 'finished' if result.returncode == 0 else 'failed'})
            except subprocess.TimeoutExpired:
                results.append({'id': project['id'], 'status': 'timed_out'})
    (out / 'queue.json').write_text(canonical({'provider': 'circleci', 'projects': results}))
    return int(any(p['status'] != 'finished' for p in results))

def main():
    # The CircleCI context is also restricted to main in the service configuration.
    if os.environ.get('CIRCLE_BRANCH') != 'main':
        raise StudioError('Privileged CircleCI jobs require main')
    if not enabled('circleci'):
        print('CircleCI generation inactive')
        return 0
    os.environ['STUDIO_CI_PROVIDER'] = 'circleci'
    os.environ['GITHUB_REPOSITORY'] = '/'.join(
        os.environ.get(k, '') for k in ('CIRCLE_PROJECT_USERNAME', 'CIRCLE_PROJECT_REPONAME'))
    # Project/context variables are independent of GitHub Actions secrets.
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
