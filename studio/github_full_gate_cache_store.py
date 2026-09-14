"""Persist successful full candidate validation cache on trusted memory branch."""
from __future__ import annotations

import base64
import json
from pathlib import Path

from core import IMAGE

STATE_BRANCH = "studio-project-memory"
STATE_PATH = ".studio-memory/full-gate-cache.json"
MAX_BYTES = 128 * 1024
MAX_ENTRIES = 128


class FullGateCacheStoreError(RuntimeError):
    pass


def _validate(data):
    if not isinstance(data, dict):
        raise FullGateCacheStoreError("full gate cache invalid")
    if set(data) != {"schema", "flutter_image", "entries"}:
        raise FullGateCacheStoreError("full gate cache fields invalid")
    if data["schema"] != 1:
        raise FullGateCacheStoreError("full gate cache schema invalid")
    if data["flutter_image"] != IMAGE:
        raise FullGateCacheStoreError("full gate cache toolchain mismatch")
    entries = data["entries"]
    if not isinstance(entries, dict) or len(entries) > MAX_ENTRIES:
        raise FullGateCacheStoreError("full gate cache entries invalid")
    clean = {}
    for key, row in entries.items():
        if (
            not isinstance(key, str)
            or len(key) != 64
            or not isinstance(row, dict)
            or row != {"passed": True}
        ):
            raise FullGateCacheStoreError("full gate cache entry invalid")
        clean[key] = {"passed": True}
    return {
        "schema": 1,
        "flutter_image": IMAGE,
        "entries": clean,
    }


def _ref(github):
    refs = github.get("/git/matching-refs/heads/" + STATE_BRANCH)
    if not isinstance(refs, list):
        raise FullGateCacheStoreError("memory branch lookup invalid")
    exact = [
        x for x in refs
        if isinstance(x, dict) and x.get("ref") == "refs/heads/" + STATE_BRANCH
    ]
    if len(exact) > 1:
        raise FullGateCacheStoreError("memory branch ambiguous")
    return exact[0] if exact else None


def load(github):
    ref = _ref(github)
    if ref is None:
        return None
    head = ref.get("object", {}).get("sha")
    if not isinstance(head, str) or len(head) != 40:
        raise FullGateCacheStoreError("memory branch head invalid")
    tree = github.get("/git/trees/" + head + "?recursive=1")
    if not isinstance(tree, dict) or tree.get("truncated") or not isinstance(tree.get("tree"), list):
        raise FullGateCacheStoreError("memory tree invalid")
    item = next(
        (
            x for x in tree["tree"]
            if isinstance(x, dict)
            and x.get("path") == STATE_PATH
            and x.get("type") == "blob"
        ),
        None,
    )
    if item is None:
        return None
    blob = github.get("/git/blobs/" + item.get("sha", ""))
    if not isinstance(blob, dict) or blob.get("encoding") != "base64":
        raise FullGateCacheStoreError("full gate cache blob invalid")
    try:
        raw = base64.b64decode(blob["content"], validate=False)
        if len(raw) > MAX_BYTES:
            raise FullGateCacheStoreError("full gate cache too large")
        value = json.loads(raw.decode("utf-8"))
    except (KeyError, ValueError, UnicodeDecodeError, json.JSONDecodeError):
        raise FullGateCacheStoreError("full gate cache unreadable") from None
    return _validate(value)


def save(github, data):
    data = _validate(data)
    ref = _ref(github)
    if ref is None:
        meta = github.get("")
        default = meta.get("default_branch") if isinstance(meta, dict) else None
        if not isinstance(default, str) or not default:
            raise FullGateCacheStoreError("default branch invalid")
        info = github.get("/branches/" + default)
        parent = info.get("commit", {}).get("sha") if isinstance(info, dict) else None
    else:
        parent = ref.get("object", {}).get("sha")
        if load(github) == data:
            return parent
    if not isinstance(parent, str) or len(parent) != 40:
        raise FullGateCacheStoreError("memory branch parent invalid")
    commit_info = github.get("/git/commits/" + parent)
    base_tree = commit_info.get("tree", {}).get("sha") if isinstance(commit_info, dict) else None
    if not isinstance(base_tree, str) or len(base_tree) != 40:
        raise FullGateCacheStoreError("memory base tree invalid")
    tree = github.call(
        "POST",
        github.repo + "/git/trees",
        {
            "base_tree": base_tree,
            "tree": [{
                "path": STATE_PATH,
                "mode": "100644",
                "type": "blob",
                "content": json.dumps(data, sort_keys=True),
            }],
        },
    )
    tree_sha = tree.get("sha") if isinstance(tree, dict) else None
    if not isinstance(tree_sha, str) or len(tree_sha) != 40:
        raise FullGateCacheStoreError("full gate cache tree creation failed")
    commit = github.call(
        "POST",
        github.repo + "/git/commits",
        {
            "message": "Persist full candidate validation cache",
            "tree": tree_sha,
            "parents": [parent],
        },
    )
    commit_sha = commit.get("sha") if isinstance(commit, dict) else None
    if not isinstance(commit_sha, str) or len(commit_sha) != 40:
        raise FullGateCacheStoreError("full gate cache commit creation failed")
    if ref is None:
        github.call(
            "POST",
            github.repo + "/git/refs",
            {"ref": "refs/heads/" + STATE_BRANCH, "sha": commit_sha},
        )
    else:
        github.call(
            "PATCH",
            github.repo + "/git/refs/heads/" + STATE_BRANCH,
            {"sha": commit_sha, "force": False},
        )
    return commit_sha


def restore_local(github, path: Path):
    data = load(github)
    if data is None:
        return None
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return data


def persist_local(github, path: Path):
    path = Path(path)
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        raise FullGateCacheStoreError("local full gate cache unreadable") from None
    return save(github, _validate(data))
