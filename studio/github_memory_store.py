"""GitHub-backed persistence for trusted cross-project memory outside main."""
from __future__ import annotations

import base64
import json
from pathlib import Path

try:
    from .project_memory import load as load_memory_file, new_memory, save as save_memory_file, validate
except ImportError:
    from project_memory import load as load_memory_file, new_memory, save as save_memory_file, validate

STATE_BRANCH = "studio-project-memory"
STATE_PATH = ".studio-memory/memory.json"
MAX_BYTES = 1024 * 1024


class GitHubMemoryError(RuntimeError):
    pass


def _exact_ref(github):
    refs = github.get("/git/matching-refs/heads/" + STATE_BRANCH)
    if not isinstance(refs, list):
        raise GitHubMemoryError("memory branch lookup invalid")
    exact = [x for x in refs if isinstance(x, dict) and x.get("ref") == "refs/heads/" + STATE_BRANCH]
    if len(exact) > 1:
        raise GitHubMemoryError("memory branch lookup ambiguous")
    return exact[0] if exact else None


def _read_blob(github, sha):
    blob = github.get("/git/blobs/" + sha)
    if not isinstance(blob, dict) or blob.get("encoding") != "base64":
        raise GitHubMemoryError("memory blob invalid")
    try:
        raw = base64.b64decode(blob["content"], validate=False)
        if len(raw) > MAX_BYTES:
            raise GitHubMemoryError("memory blob too large")
        value = json.loads(raw.decode("utf-8"))
    except (KeyError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
        raise GitHubMemoryError("memory blob unreadable") from None
    return validate(value)


def load(github):
    ref = _exact_ref(github)
    if ref is None:
        return new_memory()
    head = ref.get("object", {}).get("sha")
    if not isinstance(head, str) or len(head) != 40:
        raise GitHubMemoryError("memory branch head invalid")
    tree = github.get("/git/trees/" + head + "?recursive=1")
    if not isinstance(tree, dict) or tree.get("truncated") or not isinstance(tree.get("tree"), list):
        raise GitHubMemoryError("memory tree invalid")
    items = [x for x in tree["tree"] if isinstance(x, dict) and x.get("path") == STATE_PATH and x.get("type") == "blob"]
    if len(items) != 1:
        raise GitHubMemoryError("memory state missing or ambiguous")
    return _read_blob(github, items[0].get("sha"))


def save(github, memory):
    validate(memory)
    ref = _exact_ref(github)
    if ref is None:
        meta = github.get("")
        default = meta.get("default_branch") if isinstance(meta, dict) else None
        if not isinstance(default, str) or not default:
            raise GitHubMemoryError("default branch invalid")
        info = github.get("/branches/" + default)
        parent = info.get("commit", {}).get("sha") if isinstance(info, dict) else None
        if not isinstance(parent, str) or len(parent) != 40:
            raise GitHubMemoryError("default branch head invalid")
    else:
        parent = ref.get("object", {}).get("sha")
        if not isinstance(parent, str) or len(parent) != 40:
            raise GitHubMemoryError("memory branch head invalid")
        current = load(github)
        if current == memory:
            return parent

    commit_info = github.get("/git/commits/" + parent)
    base_tree = commit_info.get("tree", {}).get("sha") if isinstance(commit_info, dict) else None
    if not isinstance(base_tree, str) or len(base_tree) != 40:
        raise GitHubMemoryError("memory base tree invalid")
    tree = github.call("POST", github.repo + "/git/trees", {
        "base_tree": base_tree,
        "tree": [{
            "path": STATE_PATH,
            "mode": "100644",
            "type": "blob",
            "content": json.dumps(memory, sort_keys=True, ensure_ascii=False),
        }],
    })
    tree_sha = tree.get("sha") if isinstance(tree, dict) else None
    if not isinstance(tree_sha, str) or len(tree_sha) != 40:
        raise GitHubMemoryError("memory tree creation failed")
    commit = github.call("POST", github.repo + "/git/commits", {
        "message": "Persist trusted project memory",
        "tree": tree_sha,
        "parents": [parent],
    })
    commit_sha = commit.get("sha") if isinstance(commit, dict) else None
    if not isinstance(commit_sha, str) or len(commit_sha) != 40:
        raise GitHubMemoryError("memory commit creation failed")
    if ref is None:
        github.call("POST", github.repo + "/git/refs", {
            "ref": "refs/heads/" + STATE_BRANCH,
            "sha": commit_sha,
        })
    else:
        github.call("PATCH", github.repo + "/git/refs/heads/" + STATE_BRANCH, {
            "sha": commit_sha,
            "force": False,
        })
    return commit_sha


def restore_local(github, path):
    memory = load(github)
    save_memory_file(Path(path), memory)
    return memory


def persist_local(github, path):
    memory = load_memory_file(Path(path))
    return save(github, memory)
