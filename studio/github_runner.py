"""GitHub Actions adapter for the provider-neutral autonomous completion pipeline."""
from __future__ import annotations

import argparse
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
from core import StudioError, canonical, request_check
from orchestrator import run_project


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
            containers = subprocess.run([
                'docker', 'ps', '-aq', '--filter', 'label=mobile-studio-run=' + run_id,
            ], capture_output=True, text=True, timeout=15, check=True).stdout.split()
            if containers:
                subprocess.run(['docker', 'rm', '-f', *containers],
                    capture_output=True, timeout=30, check=True)
        except (OSError, subprocess.SubprocessError):
            raise StudioError('Timed-out worker stopped but container cleanup failed') from None
        raise


def run(request_path: Path, out=Path('studio-output'), runner=bounded_run,
        clock=time.monotonic, budget_seconds=85 * 60) -> dict:
    request = request_check(json.loads(request_path.read_text()))
    if not request['enabled']:
        result = {'status': 'disabled', 'next_stage': None}
        out.mkdir(parents=True, exist_ok=True)
        (out / 'github-pipeline.json').write_text(canonical(result))
        return result
    deadline = clock() + budget_seconds
    with tempfile.TemporaryDirectory(prefix='studio-github-') as work:
        result = run_project(str(request_path), out, work, runner, deadline, clock)
    summary = {
        'status': result['status'],
        'next_stage': result.get('next_stage'),
        'finished': bool(result.get('report', {}).get('completion', {}).get('finished')),
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / 'github-pipeline.json').write_text(canonical(summary))
    return summary


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('request')
    parser.add_argument('--out', default='studio-output')
    args = parser.parse_args(argv)
    if os.environ.get('GITHUB_REF') != 'refs/heads/main':
        raise StudioError('Privileged GitHub generation requires main')
    if not enabled('github'):
        print('GitHub generation inactive')
        return 0
    os.environ['STUDIO_CI_PROVIDER'] = 'github'
    result = run(Path(args.request), Path(args.out))
    print(canonical(result))
    return 0 if result['status'] in ('complete', 'disabled') else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (StudioError, ValueError, OSError, json.JSONDecodeError) as exc:
        Path('studio-output').mkdir(exist_ok=True)
        Path('studio-output/github-pipeline-error.json').write_text(canonical({
            'status': 'blocked',
            'error': str(exc) if isinstance(exc, StudioError) else type(exc).__name__,
        }))
        print('GitHub autonomous pipeline blocked; see artifact evidence.', file=sys.stderr)
        sys.exit(1)
