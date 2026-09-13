"""Persist execution checkpoint on the autonomous-state branch."""
from __future__ import annotations

import base64
import json
import re
from pathlib import Path

from execution_checkpoint import load as load_local, validate

STATE_BRANCH = "studio-autonomy-state"
ROOT = ".studio-autonomy"
MAX_BYTES = 256 * 1024


class ExecutionCheckpointStoreError(RuntimeError):
    pass


def _safe_project_id(value: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_.-]{1,80}", value):
        raise ExecutionCheckpointStoreError("project id invalid")
    return value


def _path(project_id: str) -> str:
    return f"{ROOT}/{_safe_project_id(project_id)}/execution-checkpoint.json"


def _ref(github):
    refs = github.get("/git/matching-refs/heads/" + STATE_BRANCH)
    if not isinstance(refs, list):
        raise ExecutionCheckpointStoreError("state branch lookup invalid")
    exact = [x for x in refs if isinstance(x, dict) and x.get("ref") == "refs/heads/" + STATE_BRANCH]
    if len(exact) > 1:
        raise ExecutionCheckpointStoreError("state branch ambiguous")
    return exact[0] if exact else None


def load(github, project_id: str):
    ref = _ref(github)
    if ref is None:
        return None
    head = ref.get("object", {}).get("sha")
    if not isinstance(head, str) or len(head) != 40:
        raise ExecutionCheckpointStoreError("state branch head invalid")
    tree = github.get("/git/trees/" + head + "?recursive=1")
    if not isinstance(tree, dict) or tree.get("truncated") or not isinstance(tree.get("tree"), list):
        raise ExecutionCheckpointStoreError("state tree invalid")
    target = _path(project_id)
    item = next((x for x in tree["tree"] if isinstance(x, dict) and x.get("path") == target and x.get("type") == "blob"), None)
    if item is None:
        return None
    blob = github.get("/git/blobs/" + item.get("sha", ""))
    if not isinstance(blob, dict) or blob.get("encoding") != "base64":
        raise ExecutionCheckpointStoreError("checkpoint blob invalid")
    try:
        raw = base64.b64decode(blob["content"], validate=False)
        if len(raw) > MAX_BYTES:
            raise ExecutionCheckpointStoreError("checkpoint too large")
        value = json.loads(raw.decode("utf-8"))
    except (KeyError, ValueError, UnicodeDecodeError, json.JSONDecodeError):
        raise ExecutionCheckpointStoreError("checkpoint unreadable") from None
    try:
        return validate(value)
    except ValueError as exc:
        raise ExecutionCheckpointStoreError(str(exc)) from None


def save(github, project_id: str, checkpoint: dict):
    try:
        checkpoint = validate(checkpoint)
    except ValueError as exc:
        raise ExecutionCheckpointStoreError(str(exc)) from None
    ref = _ref(github)
    if ref is None:
        meta = github.get("")
        default = meta.get("default_branch") if isinstance(meta, dict) else None
        if not isinstance(default, str) or not default:
            raise ExecutionCheckpointStoreError("default branch invalid")
        info = github.get("/branches/" + default)
        parent = info.get("commit", {}).get("sha") if isinstance(info, dict) else None
    else:
        parent = ref.get("object", {}).get("sha")
        current = load(github, project_id)
        if current == checkpoint:
            return parent
    if not isinstance(parent, str) or len(parent) != 40:
        raise ExecutionCheckpointStoreError("state branch parent invalid")
    commit_info = github.get("/git/commits/" + parent)
    base_tree = commit_info.get("tree", {}).get("sha") if isinstance(commit_info, dict) else None
    if not isinstance(base_tree, str) or len(base_tree) != 40:
        raise ExecutionCheckpointStoreError("state base tree invalid")
    tree = github.call("POST", github.repo + "/git/trees", {
        "base_tree": base_tree,
        "tree": [{
            "path": _path(project_id),
            "mode": "100644",
            "type": "blob",
            "content": json.dumps(checkpoint, sort_keys=True, ensure_ascii=False),
        }],
    })
    tree_sha = tree.get("sha") if isinstance(tree, dict) else None
    if not isinstance(tree_sha, str) or len(tree_sha) != 40:
        raise ExecutionCheckpointStoreError("checkpoint tree creation failed")
    commit = github.call("POST", github.repo + "/git/commits", {
        "message": "Persist execution checkpoint: " + project_id,
        "tree": tree_sha,
        "parents": [parent],
    })
    commit_sha = commit.get("sha") if isinstance(commit, dict) else None
    if not isinstance(commit_sha, str) or len(commit_sha) != 40:
        raise ExecutionCheckpointStoreError("checkpoint commit creation failed")
    if ref is None:
        github.call("POST", github.repo + "/git/refs", {"ref": "refs/heads/" + STATE_BRANCH, "sha": commit_sha})
    else:
        github.call("PATCH", github.repo + "/git/refs/heads/" + STATE_BRANCH, {"sha": commit_sha, "force": False})
    return commit_sha


def restore_local(github, project_id: str, path: Path) -> bool:
    checkpoint = load(github, project_id)
    if checkpoint is None:
        return False
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(checkpoint, sort_keys=True, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return True


def persist_local(github, project_id: str, path: Path):
    path = Path(path)
    if not path.is_file():
        return None
    return save(github, project_id, load_local(path))
