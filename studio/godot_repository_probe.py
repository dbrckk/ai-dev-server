"""Probe a pinned public Godot repository through the trusted import/runtime boundary."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import tempfile
import urllib.request

from core import StudioError, canonical
from existing_project import ExistingProjectError, materialize, plan
from godot_session import GodotSandbox

MAX_RESPONSE_BYTES = 8_000_000
REPO_RE = re.compile(r'[A-Za-z0-9][A-Za-z0-9-]*/[A-Za-z0-9][A-Za-z0-9_.-]*')
SHA_RE = re.compile(r'[0-9a-f]{40}')


def _get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={'Accept': 'application/vnd.github+json', 'User-Agent': 'ai-dev-server-godot-probe'})
    with urllib.request.urlopen(req, timeout=45) as response:
        raw = response.read(MAX_RESPONSE_BYTES + 1)
    if len(raw) > MAX_RESPONSE_BYTES:
        raise StudioError('Public GitHub probe response exceeded limit')
    try:
        value = json.loads(raw)
    except (ValueError, UnicodeError):
        raise StudioError('Public GitHub probe returned invalid JSON') from None
    if not isinstance(value, dict):
        raise StudioError('Public GitHub probe response must be an object')
    return value


def probe(repo: str, commit: str, fetch_json=_get_json) -> dict:
    if not isinstance(repo, str) or not REPO_RE.fullmatch(repo):
        raise StudioError('Godot probe repository is invalid')
    if not isinstance(commit, str) or not SHA_RE.fullmatch(commit):
        raise StudioError('Godot probe requires a full pinned commit SHA')
    base = 'https://api.github.com/repos/' + repo
    tree = fetch_json(base + '/git/trees/' + commit + '?recursive=1')
    try:
        import_plan = plan(tree, expected_engine='godot')
    except ExistingProjectError as exc:
        raise StudioError(str(exc)) from None
    with tempfile.TemporaryDirectory(prefix='studio-godot-probe-') as td:
        root = Path(td) / 'project'
        root.mkdir()
        def fetch_blob(sha: str) -> dict:
            if not SHA_RE.fullmatch(sha):
                raise StudioError('Godot probe blob SHA is invalid')
            return fetch_json(base + '/git/blobs/' + sha)
        materialize(root, import_plan, fetch_blob)
        sandbox = GodotSandbox(root)
        sandbox.create('probe')
        passed, logs = sandbox.gates('probe', [])
    return {
        'status': 'passed' if passed else 'failed',
        'repository': repo,
        'commit': commit,
        'engine': import_plan['engine'],
        'imported_files': len(import_plan['files']),
        'imported_bytes': import_plan['total_bytes'],
        'runtime': logs[-1] if logs else {},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('repository')
    parser.add_argument('commit')
    parser.add_argument('--out')
    args = parser.parse_args()
    result = probe(args.repository, args.commit)
    text = canonical(result)
    if args.out:
        Path(args.out).write_text(text)
    print(text)
    return 0 if result['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
