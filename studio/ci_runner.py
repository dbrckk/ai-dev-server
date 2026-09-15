"""CircleCI queue adapter using the shared autonomous completion pipeline."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import threading
import time
import uuid

from autonomous_project import run_persistent_project
from ci_provider import enabled
from core import StudioError, canonical
from orchestrator import run_project, run_registered_stages as _shared_run_registered_stages
from queue import matrix
from fleet_capacity import persist as persist_capacity_plan
from capacity_ledger import claim_preemption_lease, release as release_capacity_reservation
from worker_heartbeat import renew_if_progressed


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


def _admission_for_project(capacity_plan: dict, project_id: str) -> dict | None:
    rows = capacity_plan.get("projects") if isinstance(capacity_plan, dict) else None
    if not isinstance(rows, list):
        return None
    for row in rows:
        if isinstance(row, dict) and row.get("id") == project_id:
            admission = row.get("admission")
            return admission if isinstance(admission, dict) else None
    return None


def _heartbeat_loop(stop_event, ledger_path, reservation_id, project_out, *, interval=60.0):
    while not stop_event.wait(interval):
        try:
            result = renew_if_progressed(ledger_path, reservation_id, project_out)
        except (OSError, ValueError):
            continue
        if result.get("reason") == "reservation_missing":
            return


def save_report(out, results):
    temporary = out / 'queue.json.tmp'
    temporary.write_text(canonical({'provider': 'circleci', 'projects': results}))
    temporary.replace(out / 'queue.json')


def _run_registered_stages(project, project_out, work, report, deadline, runner, clock):
    """Compatibility wrapper for callers/tests while stage logic lives in orchestrator.py."""
    result = _shared_run_registered_stages(
        project['file'], project_out, work, report, deadline, runner, clock,
        os.environ.get('CIRCLE_SHA1'))
    status = None if result['status'] == 'complete' else result['status']
    return result['report'], status


def _run_project_for_queue(project, project_out, work, runner, deadline, clock, baseline_sha):
    if os.environ.get('STUDIO_PERSISTENT_GOALS') != '1':
        return run_project(project['file'], project_out, work, runner, deadline, clock, baseline_sha)

    state = run_persistent_project(
        project['file'], project_out, work, runner, deadline, clock, baseline_sha,
        goal_id=project['id'],
        objective='Complete project ' + project['id'] + ' with verified release evidence',
        max_cycles=4,
    )
    status = state.get('status')
    if status == 'complete':
        return {'status': 'complete', 'next_stage': None}
    if status == 'human_action_required':
        return {'status': 'human_action_required', 'next_stage': state.get('human_action')}
    if status == 'blocked':
        return {'status': 'blocked', 'next_stage': state.get('blocked_reason')}
    return {'status': 'deferred', 'next_stage': None}


def run_queue(directory='control/mobile-requests', out=Path('studio-output'),
              runner=bounded_run, clock=time.monotonic):
    projects = matrix(directory)
    out.mkdir(parents=True, exist_ok=True)
    capacity_plan = persist_capacity_plan(out, directory)
    results = [{'id': p['id'], 'status': 'pending'} for p in projects]
    save_report(out, results)
    deadline = clock() + 70 * 60
    baseline_sha = os.environ.get('CIRCLE_SHA1')
    for index, project in enumerate(projects):
        admission = _admission_for_project(capacity_plan, project["id"])
        if isinstance(admission, dict) and admission.get("admitted") is False:
            results[index]["status"] = "deferred_by_admission"
            results[index]["admission_reason"] = admission.get("reason")
            save_report(out, results)
            continue
        if deadline - clock() <= 0:
            results[index]['status'] = 'deferred'
            save_report(out, results)
            continue
        admission_claim = None
        if isinstance(admission, dict) and admission.get("action") == "admit_preemption_lease":
            admission_claim = claim_preemption_lease(
                out / "capacity-ledger.json",
                project["id"],
            )
            if admission_claim.get("claimed") is not True:
                results[index]["status"] = "deferred_by_admission"
                results[index]["admission_reason"] = "preemption_lease_claim_failed"
                save_report(out, results)
                continue
            results[index]["admission_lease_claimed"] = True
        results[index]['status'] = 'running'
        save_report(out, results)
        with tempfile.TemporaryDirectory(prefix='studio-ci-') as work:
            project_out = out / project['id']
            heartbeat_stop = None
            heartbeat_thread = None
            if isinstance(admission_claim, dict) and admission_claim.get("claimed") is True:
                heartbeat_stop = threading.Event()
                heartbeat_thread = threading.Thread(
                    target=_heartbeat_loop,
                    args=(heartbeat_stop, out / "capacity-ledger.json", admission_claim["reservation_id"], project_out),
                    daemon=True,
                    name="studio-capacity-heartbeat-" + project["id"],
                )
                heartbeat_thread.start()
            try:
                result = _run_project_for_queue(project, project_out, work, runner, deadline, clock, baseline_sha)
                results[index]['status'] = result['status']
                results[index]['next_stage'] = result.get('next_stage')
                if result.get('research_status') is not None:
                    results[index]['research_status'] = result['research_status']
            except subprocess.TimeoutExpired:
                results[index]['status'] = 'timed_out'
                deadline = 0
            except (OSError, StudioError, ValueError, json.JSONDecodeError):
                results[index]['status'] = 'worker_error'
                deadline = 0
            finally:
                if heartbeat_stop is not None:
                    heartbeat_stop.set()
                if heartbeat_thread is not None:
                    heartbeat_thread.join(timeout=2.0)
                if isinstance(admission_claim, dict) and admission_claim.get("claimed") is True:
                    released = release_capacity_reservation(
                        out / "capacity-ledger.json",
                        admission_claim["reservation_id"],
                    )
                    results[index]["admission_lease_released"] = released.get("released") is True
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
        os.environ.setdefault('STUDIO_PERSISTENT_GOALS', '1')
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
