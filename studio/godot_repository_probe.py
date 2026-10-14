"""Probe a pinned public Godot repository through the trusted import/runtime boundary."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import tempfile
import urllib.request
import urllib.parse

from core import StudioError, canonical, NoRedirect
from existing_project import ExistingProjectError, materialize, plan
from godot_session import GodotSandbox

MAX_RESPONSE_BYTES = 8_000_000
REPO_RE = re.compile(r'[A-Za-z0-9][A-Za-z0-9-]*/[A-Za-z0-9][A-Za-z0-9_.-]*')
SHA_RE = re.compile(r'[0-9a-f]{40}')


def _get_json(url: str) -> dict:
    # Only forward the read-only Actions token to the canonical GitHub API.
    # Anonymous requests are limited to 60/hour shared by the CI runner IP.
    # Never follow a redirect that could disclose Authorization to another host.
    parsed = urllib.parse.urlsplit(url)
    if (
        parsed.scheme != 'https'
        or parsed.netloc != 'api.github.com'
        or not parsed.path.startswith('/repos/')
    ):
        raise StudioError('Godot probe GitHub API URL is invalid')
    headers = {
        'Accept': 'application/vnd.github+json',
        'User-Agent': 'ai-dev-server-godot-probe',
    }
    token = str(os.environ.get('GITHUB_TOKEN') or '').strip()
    if token:
        headers['Authorization'] = 'Bearer ' + token
    req = urllib.request.Request(url, headers=headers)
    opener = urllib.request.build_opener(NoRedirect())
    with opener.open(req, timeout=45) as response:
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
