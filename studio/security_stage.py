"""Persist trusted security/SBOM evidence and close the completion contract."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from completion import apply_completion, next_stage
from core import StudioError, canonical
from run import GitHub
from security_audit import build_security_package
from security_remediation import MAX_REMEDIATION_ROUNDS, remediate, remediation_candidate
from security_agent import MAX_AGENTIC_ROUNDS, attempt as agentic_attempt, eligible_blockers as agentic_eligible_blockers
from project_budget import budget_status, can_spend, configure as configure_budget, record_repair_outcome


def advance(request_path: Path, root: Path, out: Path) -> dict:
    req = json.loads(request_path.read_text())
    report_path = out / 'report.json'
    if not report_path.is_file():
        raise StudioError('Missing privacy report')
    state = json.loads(report_path.read_text())
    if next_stage(state) != 'security_scan':
        apply_completion(state)
        report_path.write_text(canonical(state))
        return state

    configure_budget(state, req)
    remediation_history = []
    evidence = build_security_package(root, out)
    for round_index in range(MAX_REMEDIATION_ROUNDS):
        if evidence.get('passed') is True or evidence.get('human_review_required') is True:
            break
        if not remediation_candidate(evidence):
            break
        result = remediate(root, evidence)
        remediation_history.append({
            'round': round_index + 1,
            'changed': result.get('changed') is True,
            'actions': list(result.get('actions', [])),
        })
        record_repair_outcome(
            state,
            success=result.get('changed') is True,
            calls=result.get('model_calls', 0),
            blockers_before=blockers_before,
            blockers_after=0 if result.get('changed') is True else blockers_before,
        )
        if result.get('changed') is not True:
            break
        evidence = build_security_package(root, out)
    evidence['auto_remediation'] = {
        'attempted': bool(remediation_history),
        'rounds': remediation_history,
        'max_rounds': MAX_REMEDIATION_ROUNDS,
        'converged': evidence.get('passed') is True,
    }

    agentic_history = []
    for round_index in range(MAX_AGENTIC_ROUNDS):
        if evidence.get('passed') is True or evidence.get('human_review_required') is True:
            break
        if not agentic_eligible_blockers(evidence):
            break
        if not can_spend(state, 1, repair=True):
            agentic_history.append({
                'round': round_index + 1,
                'changed': False,
                'error': 'project_repair_budget_exhausted',
            })
            break
        blockers_before = len(evidence.get('blockers', []))
        try:
            result = agentic_attempt(root, state, evidence, req['app_name'])
        except StudioError as exc:
            record_repair_outcome(
                state,
                success=False,
                calls=0,
                blockers_before=blockers_before,
                blockers_after=blockers_before,
            )
            agentic_history.append({
                'round': round_index + 1,
                'changed': False,
                'error': str(exc),
            })
            break
        agentic_history.append({
            'round': round_index + 1,
            'changed': result.get('changed') is True,
            'blockers': list(result.get('blockers', [])),
            'model_calls': result.get('model_calls', 0),
            'models_used': dict(result.get('models_used', {})),
            'providers_used': dict(result.get('providers_used', {})),
            'gate_count': result.get('gate_count', 0),
        })
        if result.get('changed') is not True:
            break
        evidence = build_security_package(root, out)

    evidence['auto_remediation'] = {
        'attempted': bool(remediation_history),
        'rounds': remediation_history,
        'max_rounds': MAX_REMEDIATION_ROUNDS,
        'converged': evidence.get('passed') is True,
    }
    evidence['agentic_remediation'] = {
        'attempted': bool(agentic_history),
        'rounds': agentic_history,
        'max_rounds': MAX_AGENTIC_ROUNDS,
        'converged': evidence.get('passed') is True,
    }
    evidence['project_budget'] = budget_status(state)
    state.setdefault('release_evidence', {})['security_scan'] = evidence
    state.pop('human_action', None)
    if state.get('status') == 'human_action_required':
        state['status'] = 'validated_preview'
    apply_completion(state)
    if evidence.get('passed') is not True and evidence.get('human_review_required') is True:
        state['human_action'] = {
            'action': 'security_trust_review_required',
            'detail': 'Review security, dependency, permission, registry, or licensing decisions that cannot be safely auto-approved.',
            'reasons': list(evidence.get('human_review_reasons', [])),
            'dangerous_permissions': list(evidence.get('dangerous_permissions', [])),
            'blockers': list(evidence.get('blockers', [])),
        }
        state['status'] = 'human_action_required'
        state['release_status'] = 'human_action_required'

    parent = state.get('checkpoint_commit')
    if not parent:
        raise StudioError('Privacy report has no checkpoint commit')
    github = GitHub(req['target_repo'])
    manifest = root / 'android/app/src/main/AndroidManifest.xml'
    if manifest.is_file() and not manifest.is_symlink():
        github.native_files = {
            'android/app/src/main/AndroidManifest.xml': manifest.read_bytes(),
        }
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
    evidence = state.get('release_evidence', {}).get('security_scan')
    print(canonical({
        'status': state.get('status'),
        'finished': state.get('completion', {}).get('finished'),
        'next_stage': state.get('completion', {}).get('next_stage'),
        'security_passed': evidence.get('passed') if isinstance(evidence, dict) else None,
    }))
    if state.get('status') == 'human_action_required':
        return 2
    return 0 if isinstance(evidence, dict) and evidence.get('passed') else 1


if __name__ == '__main__':
    raise SystemExit(main())
