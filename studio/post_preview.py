"""Autonomous trusted stages executed after a validated preview."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import tempfile

from completion import apply_completion, next_stage
from core import Sandbox, StudioError, apply_patch, canonical
from release import build_release
from run import GitHub


def ensure_workspace(req: dict, root: Path, github: GitHub, branch: str) -> tuple[dict, str]:
    """Restore a validated checkpoint into a fresh trusted Flutter workspace."""
    if (root / 'pubspec.yaml').is_file():
        state = json.loads((Path(req['_out']) / 'report.json').read_text())
        return state, state['checkpoint_commit']

    sandbox = Sandbox(root)
    sandbox.create(req['app_name'])
    github.native_files = getattr(sandbox, 'native_files', {})
    with tempfile.TemporaryDirectory() as td:
        saved = Path(td)
        state, parent = github.restore(branch, saved)
        if not state or state.get('status') != 'validated_preview':
            raise StudioError('Release stage requires a validated preview checkpoint')
        for p in saved.rglob('*'):
            if not p.is_file():
                continue
            rel = p.relative_to(saved).as_posix()
            if rel == 'pubspec.lock':
                (root / rel).write_bytes(p.read_bytes())
            else:
                apply_patch(root, {'files': [{'path': rel, 'content': p.read_text()}]})
    return state, parent


def advance(request_path: Path, root: Path, out: Path) -> dict:
    req = json.loads(request_path.read_text())
    req['_out'] = str(out)
    report_path = out / 'report.json'
    if not report_path.is_file():
        raise StudioError('Missing preview report')
    state = json.loads(report_path.read_text())
    if state.get('status') != 'validated_preview':
        apply_completion(state)
        report_path.write_text(canonical(state))
        return state

    stage = next_stage(state)
    if stage != 'release_build':
        apply_completion(state)
        report_path.write_text(canonical(state))
        return state

    github = GitHub(req['target_repo'])
    branch = 'studio/' + req['id']
    if not (root / 'pubspec.yaml').is_file():
        sandbox = Sandbox(root)
        sandbox.create(req['app_name'])
        github.native_files = getattr(sandbox, 'native_files', {})
        with tempfile.TemporaryDirectory() as td:
            saved = Path(td)
            restored, parent = github.restore(branch, saved)
            if not restored or restored.get('status') != 'validated_preview':
                raise StudioError('Release stage requires validated preview checkpoint')
            state = restored
            for p in saved.rglob('*'):
                if not p.is_file():
                    continue
                rel = p.relative_to(saved).as_posix()
                if rel == 'pubspec.lock':
                    (root / rel).write_bytes(p.read_bytes())
                else:
                    apply_patch(root, {'files': [{'path': rel, 'content': p.read_text()}]})
    else:
        parent = state.get('checkpoint_commit')
        if not parent:
            raise StudioError('Preview report has no checkpoint commit')

    evidence = build_release(root, Sandbox(root))
    state.setdefault('release_evidence', {})['release_build'] = evidence
    if evidence.get('passed'):
        bundle = root / 'build/app/outputs/bundle/release/app-release.aab'
        apk = root / 'build/app/outputs/flutter-apk/app-release.apk'
        shutil.copyfile(bundle, out / 'app-release.aab')
        shutil.copyfile(apk, out / 'app-release.apk')
    apply_completion(state)
    state['status'] = 'validated_preview' if not state['completion']['finished'] else 'finished'
    sha = github.publish(branch, parent, root, state)
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
    print(canonical({'status': state.get('status'), 'next_stage': state.get('completion', {}).get('next_stage')}))
    evidence = state.get('release_evidence', {}).get('release_build')
    return 0 if not isinstance(evidence, dict) or evidence.get('passed') else 1


if __name__ == '__main__':
    raise SystemExit(main())
