"""Create and checkpoint privacy policy and Play Data Safety evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from completion import apply_completion, next_stage
from core import StudioError, canonical
from privacy_audit import build_privacy_package
from run import GitHub


def advance(request_path: Path, root: Path, out: Path) -> dict:
    req = json.loads(request_path.read_text())
    report_path = out / 'report.json'
    if not report_path.is_file():
        raise StudioError('Missing store metadata report')
    state = json.loads(report_path.read_text())
    if next_stage(state) != 'privacy_policy':
        apply_completion(state)
        report_path.write_text(canonical(state))
        return state

    evidence = build_privacy_package(root, out, state)
    state.setdefault('release_evidence', {})['privacy_policy'] = evidence
    apply_completion(state)

    parent = state.get('checkpoint_commit')
    if not parent:
        raise StudioError('Store metadata report has no checkpoint commit')
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
    evidence = state.get('release_evidence', {}).get('privacy_policy')
    print(canonical({
        'status': state.get('status'),
        'next_stage': state.get('completion', {}).get('next_stage'),
        'privacy_passed': evidence.get('passed') if isinstance(evidence, dict) else None,
    }))
    return 0 if isinstance(evidence, dict) and evidence.get('passed') else 1


if __name__ == '__main__':
    raise SystemExit(main())
