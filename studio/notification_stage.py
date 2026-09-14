"""Persist notification QA evidence into the autonomous checkpoint."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from completion import apply_completion, next_stage
from core import StudioError, canonical
from notification_qa import validate_notifications
from run import GitHub
from release_stage_engine import apply_external_gate, evaluate_and_repair, invalidate_for_source_change


def advance(request_path: Path, root: Path, out: Path) -> dict:
    req = json.loads(request_path.read_text())
    report_path = out / 'report.json'
    if not report_path.is_file():
        raise StudioError('Missing capability QA report')
    state = json.loads(report_path.read_text())
    if next_stage(state) != 'notification_qa':
        apply_completion(state)
        report_path.write_text(canonical(state))
        return state

    evidence = evaluate_and_repair(root, out, state, req, 'notification_qa', validate_notifications)
    invalidate_for_source_change(state, evidence)
    state.setdefault('release_evidence', {})['notification_qa'] = evidence
    state.pop('human_action', None)
    if state.get('status') == 'human_action_required':
        state['status'] = 'validated_preview'
    apply_completion(state)
    apply_external_gate(state, 'notification_qa', evidence)

    parent = state.get('checkpoint_commit')
    if not parent:
        raise StudioError('Notification QA report has no checkpoint commit')
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
    evidence = state.get('release_evidence', {}).get('notification_qa')
    print(canonical({
        'status': state.get('status'),
        'next_stage': state.get('completion', {}).get('next_stage'),
        'notification_passed': evidence.get('passed') if isinstance(evidence, dict) else None,
        'notification_observed': evidence.get('app_originated_notification_observed') if isinstance(evidence, dict) else None,
    }))
    if state.get('status') == 'human_action_required':
        return 2
    if isinstance(evidence, dict) and evidence.get('source_repaired') is True:
        return 0
    return 0 if isinstance(evidence, dict) and evidence.get('passed') else 1


if __name__ == '__main__':
    raise SystemExit(main())
