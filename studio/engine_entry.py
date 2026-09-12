"""Trusted preview dispatcher preserving the mature Flutter runner unchanged."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from core import StudioError, canonical, request_check
from project_engine import EngineError, infer
from run import GitHub, execute as execute_flutter
from godot_preview import execute as execute_godot


def _exact_branch_ref(github: GitHub, branch: str):
    refs = github.get('/git/matching-refs/heads/' + branch)
    if not isinstance(refs, list):
        raise StudioError('Target branch lookup returned invalid data')
    exact = [item for item in refs if isinstance(item, dict) and item.get('ref') == 'refs/heads/' + branch]
    if len(exact) > 1:
        raise StudioError('Target branch lookup is ambiguous')
    return exact[0] if exact else None


def detect_engine(req: dict, github: GitHub) -> str:
    """Infer engine from the checkpoint branch when present, otherwise target default branch.

    Empty/bootstrap repositories stay Flutter for backwards compatibility. Existing repositories
    must expose exactly one trusted marker; ambiguous/unknown projects fail closed.
    """
    metadata = github.get('')
    if not isinstance(metadata, dict) or metadata.get('archived'):
        raise StudioError('Target repository is unavailable or archived')
    if metadata.get('size', 0) == 0:
        brief = str(req.get('brief', '')).lower()
        mobile_hints = ('flutter', 'android', 'application mobile', 'mobile app', 'apk')
        return 'flutter' if any(hint in brief for hint in mobile_hints) else 'generic'
    branch = 'studio/' + req['id']
    exact = _exact_branch_ref(github, branch)
    if exact:
        source = exact.get('object', {}).get('sha')
    else:
        default = metadata.get('default_branch')
        if not isinstance(default, str) or not default:
            raise StudioError('Existing target requires a default branch')
        info = github.get('/branches/' + default)
        source = info.get('commit', {}).get('sha') if isinstance(info, dict) else None
    if not isinstance(source, str) or len(source) != 40:
        raise StudioError('Target branch head is invalid')
    tree = github.get('/git/trees/' + source + '?recursive=1')
    if not isinstance(tree, dict) or tree.get('truncated') is True or not isinstance(tree.get('tree'), list):
        raise StudioError('Target tree is unavailable or truncated')
    paths = [item.get('path') for item in tree['tree'] if isinstance(item, dict) and item.get('type') == 'blob' and isinstance(item.get('path'), str)]
    # Preserve legacy Flutter bootstrap repositories containing only documentation files.
    if set(paths) <= {'README.md', 'LICENSE', '.gitignore'}:
        brief = str(req.get('brief', '')).lower()
        mobile_hints = ('flutter', 'android', 'application mobile', 'mobile app', 'apk')
        return 'flutter' if any(hint in brief for hint in mobile_hints) else 'generic'
    try:
        return infer(paths).name
    except EngineError as exc:
        raise StudioError(str(exc)) from None


def execute(req: dict, root: Path, out: Path, github=None) -> dict:
    req = request_check(req)
    if not req['enabled']:
        return {'status': 'disabled'}
    github = github or GitHub(req['target_repo'])
    engine = detect_engine(req, github)
    if engine == 'godot':
        return execute_godot(req, root, out, github)
    if engine == 'flutter':
        return execute_flutter(req, root, out, github)
    if engine == 'generic':
        raise StudioError('Generic projects are executed by the multi-engine orchestrator')
    raise StudioError('Unsupported project engine')


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('request')
    parser.add_argument('--work', default='/tmp/mobile-studio-app')
    parser.add_argument('--out', default='studio-output')
    args = parser.parse_args(argv)
    out = Path(args.out)
    try:
        req = json.loads(Path(args.request).read_text())
        state = execute(req, Path(args.work), out)
        print(canonical({'status': state.get('status'), 'engine': state.get('engine', 'flutter'), 'checkpoint_commit': state.get('checkpoint_commit')}))
        return 0 if state.get('status') in ('disabled', 'validated_preview', 'awaiting_visual_review', 'godot_preview_validated') else 1
    except (StudioError, ValueError, OSError, json.JSONDecodeError) as exc:
        out.mkdir(parents=True, exist_ok=True)
        detail = str(exc) if isinstance(exc, StudioError) else 'Invalid configuration or local IO failure'
        (out / 'error.json').write_text(canonical({'status': 'blocked', 'error': type(exc).__name__, 'detail': detail}))
        print('Studio blocked; see error.json and existing checkpoint.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
