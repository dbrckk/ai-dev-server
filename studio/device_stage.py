"""Persist trusted Android emulator QA evidence into the autonomous checkpoint."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from completion import apply_completion, next_stage
from core import StudioError, canonical
from device_qa import validate_release_on_device
from run import GitHub


def advance(request_path: Path, root: Path, out: Path) -> dict:
    req = json.loads(request_path.read_text())
    report_path = out / 'report.json'
    if not report_path.is_file():
        raise StudioError('Missing release report')
    state = json.loads(report_path.read_text())
    if next_stage(state) != 'real_device':
        apply_completion(state)
        report_path.write_text(canonical(state))
        return state

    evidence = validate_release_on_device(root, out)
    state.setdefault('release_evidence', {})['real_device'] = evidence
    apply_completion(state)

    parent = state.get('checkpoint_commit')
    if not parent:
        raise StudioError('Release report has no checkpoint commit')
    github = GitHub(req['target_repo'])
    sha = github.publish('studio/' + req['id'], parent, root, state)
    state['checkpoint_commit'] = sha
    report_path.write_text(canonical(state))
    return state


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('request')
    parser.add_argument('--work', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    state = advance(Path(args.request), Path(args.work), Path(args.out))
    evidence = state.get('release_evidence', {}).get('real_device')
    print(canonical({'status': state.get('status'),
                     'next_stage': state.get('completion', {}).get('next_stage'),
                     'device_passed': evidence.get('passed') if isinstance(evidence, dict) else None}))
    return 0 if isinstance(evidence, dict) and evidence.get('passed') else 1


if __name__ == '__main__':
    raise SystemExit(main())
