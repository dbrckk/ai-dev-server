"""Plan and materialize a bounded existing mobile repository snapshot.

GitHub transport stays outside this module. The planner accepts only trusted tree
metadata and uses project_engine policy to decide what may enter the model workspace.
"""
from __future__ import annotations

import base64
from pathlib import Path

from project_engine import EngineError, infer, restorable

MAX_TREE_ENTRIES = 1200
MAX_TEXT_FILE_BYTES = 600_000
MAX_TOTAL_BYTES = 5_000_000


class ExistingProjectError(ValueError):
    pass


def plan(tree: dict, expected_engine: str | None = None) -> dict:
    if not isinstance(tree, dict) or tree.get('truncated') is True:
        raise ExistingProjectError('Existing project tree is unavailable or truncated')
    entries = tree.get('tree')
    if not isinstance(entries, list) or not entries or len(entries) > MAX_TREE_ENTRIES:
        raise ExistingProjectError('Existing project tree size is unsupported')
    blob_paths = [item.get('path') for item in entries
                  if isinstance(item, dict) and item.get('type') == 'blob' and isinstance(item.get('path'), str)]
    try:
        engine = infer(blob_paths).name
    except EngineError as exc:
        raise ExistingProjectError(str(exc)) from None
    if expected_engine is not None and engine != expected_engine:
        raise ExistingProjectError('Existing project engine does not match request')

    selected = []
    total = 0
    for item in entries:
        if not isinstance(item, dict) or item.get('type') != 'blob':
            continue
        path = item.get('path'); mode = item.get('mode'); sha = item.get('sha'); size = item.get('size', 0)
        if not isinstance(path, str) or not restorable(path, engine):
            continue
        if mode != '100644' or not isinstance(sha, str) or len(sha) != 40:
            raise ExistingProjectError('Existing project contains unsupported restorable file metadata')
        if type(size) is not int or size < 0 or size > MAX_TEXT_FILE_BYTES:
            raise ExistingProjectError('Existing project restorable file is too large')
        total += size
        if total > MAX_TOTAL_BYTES:
            raise ExistingProjectError('Existing project restorable scope is too large')
        selected.append({'path': path, 'sha': sha, 'size': size})
    if not selected:
        raise ExistingProjectError('Existing project has no restorable files')
    return {'engine': engine, 'files': selected, 'total_bytes': total}


def materialize(root: Path, import_plan: dict, fetch_blob) -> None:
    root = root.resolve()
    files = import_plan.get('files') if isinstance(import_plan, dict) else None
    if not isinstance(files, list) or not files:
        raise ExistingProjectError('Existing project import plan invalid')
    prepared = []
    total = 0
    for item in files:
        if not isinstance(item, dict) or set(item) != {'path', 'sha', 'size'}:
            raise ExistingProjectError('Existing project import entry malformed')
        target = (root / item['path']).resolve()
        if not target.is_relative_to(root):
            raise ExistingProjectError('Existing project path escaped workspace')
        blob = fetch_blob(item['sha'])
        if not isinstance(blob, dict) or blob.get('encoding') != 'base64' or not isinstance(blob.get('content'), str):
            raise ExistingProjectError('Existing project blob response malformed')
        try:
            content = base64.b64decode(blob['content'], validate=False)
            text = content.decode('utf-8')
        except (ValueError, UnicodeDecodeError):
            raise ExistingProjectError('Existing project restorable file is not UTF-8 text') from None
        if len(content) != item['size'] or len(content) > MAX_TEXT_FILE_BYTES:
            raise ExistingProjectError('Existing project blob size mismatch')
        total += len(content)
        if total > MAX_TOTAL_BYTES:
            raise ExistingProjectError('Existing project materialization exceeded limit')
        prepared.append((target, text))
    for target, text in prepared:
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() or target.is_symlink():
            raise ExistingProjectError('Existing project materialization target already exists')
        target.write_text(text)
