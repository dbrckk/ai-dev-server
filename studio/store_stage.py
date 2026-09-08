"""Create and checkpoint the autonomous Play Store metadata package."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from completion import apply_completion, next_stage
from core import StudioError, canonical
from run import GitHub
from store_package import build_store_package, listing_from_state


def advance(request_path: Path, root: Path, out: Path) -> dict:
    req = json.loads(request_path.read_text())
    report_path = out / 'report.json'
    if not report_path.is_file():
        raise StudioError('Missing device QA report')
    state = json.loads(report_path.read_text())
    if next_stage(state) != 'store_metadata':
        apply_completion(state)
        report_path.write_text(canonical(state))
        return state

    try:
        listing = listing_from_state(req, state)
        evidence = build_store_package(root, out, state, listing)
    except ValueError as e:
        evidence = {'passed': False, 'blockers': [str(e)]}

    state.setdefault('release_evidence', {})['store_metadata'] = evidence
    apply_completion(state)

    parent = state.get('checkpoint_commit')
    if not parent:
        raise StudioError('Device QA report has no checkpoint commit')
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
    evidence = state.get('release_evidence', {}).get('store_metadata')
    print(canonical({
        'status': state.get('status'),
        'next_stage': state.get('completion', {}).get('next_stage'),
        'store_metadata_passed': evidence.get('passed') if isinstance(evidence, dict) else None,
    }))
    return 0 if isinstance(evidence, dict) and evidence.get('passed') else 1


if __name__ == '__main__':
    raise SystemExit(main())
