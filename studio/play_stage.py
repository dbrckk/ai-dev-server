"""Trusted Google Play validation/publication stage."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil

from android_signing import sign_aab, signing_credentials
from completion import apply_completion, next_stage
from core import Sandbox, StudioError, canonical, request_check
from play_publisher import publish_bundle, publication_credentials
from release import build_release
from run import GitHub

PACKAGE_PATTERNS = (
    re.compile(r'applicationId\s*[= ]\s*["\']([^"\']+)["\']'),
    re.compile(r'namespace\s*[= ]\s*["\']([^"\']+)["\']'),
)
PACKAGE_RE = re.compile(r'[A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z][A-Za-z0-9_]*)+')


def detect_package_name(root: Path) -> str:
    candidates = [
        root / 'android/app/build.gradle.kts',
        root / 'android/app/build.gradle',
    ]
    for path in candidates:
        if not path.is_file() or path.is_symlink():
            continue
        text = path.read_text(errors='replace')
        for pattern in PACKAGE_PATTERNS:
            match = pattern.search(text)
            if match and PACKAGE_RE.fullmatch(match.group(1)):
                return match.group(1)
    raise StudioError('Android package name unavailable for Play publication')


def _human_action(state: dict, action: str, detail: str) -> dict:
    state['human_action'] = {'action': action, 'detail': detail}
    state['status'] = 'human_action_required'
    state['release_status'] = 'human_action_required'
    state.setdefault('release_evidence', {})['play_publish'] = {
        'passed': False,
        'human_action_required': True,
        'blocker': action,
    }
    apply_completion(state)
    state['status'] = 'human_action_required'
    state['release_status'] = 'human_action_required'
    return state


def _ensure_signed_aab(root: Path, out: Path, state: dict, env: dict | None = None) -> Path | None:
    release = state.setdefault('release_evidence', {}).setdefault('release_build', {})
    artifact = out / 'app-release.aab'
    signing = release.get('production_signing')
    if (
        isinstance(signing, dict)
        and signing.get('passed') is True
        and artifact.is_file()
        and hashlib.sha256(artifact.read_bytes()).hexdigest() == signing.get('signed_aab_sha256')
    ):
        return artifact

    credentials = signing_credentials(env, project_root=root)
    if not credentials.get('available'):
        return None

    unsigned = root / 'build/app/outputs/bundle/release/app-release.aab'
    if not unsigned.is_file():
        rebuilt = build_release(root, Sandbox(root))
        if not rebuilt.get('passed'):
            raise StudioError('Unable to rebuild release AAB for Play publication')
        release.update(rebuilt)
    if not unsigned.is_file():
        raise StudioError('Release AAB unavailable after successful rebuild')

    signing = sign_aab(
        unsigned,
        artifact,
        credentials['keystore'],
        credentials['alias'],
        credentials['store_password'],
        credentials['key_password'],
    )
    release['production_signing'] = signing
    release['artifact_sha256'] = signing['signed_aab_sha256']
    release['certificate_sha256'] = signing['certificate_sha256']
    release['signing_scope'] = signing['signing_scope']
    return artifact


def advance(
    request_path: Path,
    root: Path,
    out: Path,
    *,
    env: dict | None = None,
    publisher=publish_bundle,
) -> dict:
    req = request_check(json.loads(request_path.read_text()))
    report_path = out / 'report.json'
    if not report_path.is_file():
        raise StudioError('Missing security report')
    state = json.loads(report_path.read_text())
    if next_stage(state) != 'play_publish':
        apply_completion(state)
        report_path.write_text(canonical(state))
        return state

    publication = state.get('publication_request')
    if not isinstance(publication, dict) or publication.get('enabled') is not True:
        raise StudioError('Play stage reached without explicit publication request')

    for prerequisite in ('release_build', 'store_metadata', 'privacy_policy', 'security_scan'):
        evidence = state.get('release_evidence', {}).get(prerequisite)
        if not isinstance(evidence, dict) or evidence.get('passed') is not True:
            raise StudioError('Play publication prerequisite missing: ' + prerequisite)

    current = os.environ if env is None else env
    artifact = _ensure_signed_aab(root, out, state, current)
    if artifact is None:
        _human_action(
            state,
            'android_upload_keystore_required',
            'Configure trusted Android upload signing credentials outside the project workspace.',
        )
    else:
        play_credentials = publication_credentials(current)
        if not play_credentials.get('available'):
            _human_action(
                state,
                play_credentials.get('blocker') or 'play_access_token_required',
                'Provide an authorized short-lived Android Publisher access token.',
            )
        else:
            commit = publication.get('commit') is True
            track = publication.get('track', 'internal')
            if commit and current.get('STUDIO_PLAY_COMMIT_APPROVED') != '1':
                _human_action(
                    state,
                    'play_commit_approval_required',
                    'Set STUDIO_PLAY_COMMIT_APPROVED=1 in the trusted runner to authorize the Play edit commit.',
                )
            elif commit and track == 'production' and current.get('STUDIO_PLAY_PRODUCTION_APPROVED') != '1':
                _human_action(
                    state,
                    'play_production_approval_required',
                    'Set STUDIO_PLAY_PRODUCTION_APPROVED=1 after explicit production-release approval.',
                )
            else:
                package_name = detect_package_name(root)
                result = publisher(
                    package_name=package_name,
                    signed_aab=artifact,
                    track=track,
                    access_token=play_credentials['access_token'],
                    commit=commit,
                )
                if not isinstance(result, dict) or result.get('passed') is not True or result.get('edit_validated') is not True:
                    raise StudioError('Google Play publication evidence invalid')
                if bool(result.get('committed')) != commit:
                    raise StudioError('Google Play commit evidence mismatch')
                result = dict(result)
                result['artifact_sha256'] = hashlib.sha256(artifact.read_bytes()).hexdigest()
                result['certificate_sha256'] = state['release_evidence']['release_build']['production_signing']['certificate_sha256']
                state.setdefault('release_evidence', {})['play_publish'] = result
                state.pop('human_action', None)
                apply_completion(state)

    parent = state.get('checkpoint_commit')
    if not parent:
        raise StudioError('Security report has no checkpoint commit')
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
    print(canonical({
        'status': state.get('status'),
        'next_stage': state.get('completion', {}).get('next_stage'),
        'human_action': state.get('human_action'),
        'play_publish': state.get('release_evidence', {}).get('play_publish'),
    }))
    if state.get('status') == 'human_action_required':
        return 2
    evidence = state.get('release_evidence', {}).get('play_publish')
    return 0 if isinstance(evidence, dict) and evidence.get('passed') is True else 1


if __name__ == '__main__':
    raise SystemExit(main())
