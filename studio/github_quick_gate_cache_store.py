"""Persist toolchain-scoped quick-gate cache on trusted memory branch."""
from __future__ import annotations

import base64
import json
from pathlib import Path

STATE_BRANCH = "studio-project-memory"
STATE_PATH = ".studio-memory/quick-gate-cache.json"
MAX_BYTES = 512 * 1024
MAX_ENTRIES = 512


class QuickGateCacheStoreError(RuntimeError):
    pass


def _validate(data):
    if not isinstance(data, dict):
        raise QuickGateCacheStoreError("quick gate cache invalid")
    if set(data) != {"schema", "toolchain_fingerprint", "entries"}:
        raise QuickGateCacheStoreError("quick gate cache fields invalid")
    if type(data["schema"]) is not int or data["schema"] < 1:
        raise QuickGateCacheStoreError("quick gate cache schema invalid")
    fingerprint = data["toolchain_fingerprint"]
    if not isinstance(fingerprint, str) or len(fingerprint) != 64:
        raise QuickGateCacheStoreError("quick gate cache fingerprint invalid")
    entries = data["entries"]
    if not isinstance(entries, dict) or len(entries) > MAX_ENTRIES:
        raise QuickGateCacheStoreError("quick gate cache entries invalid")
    clean = {}
    for key, row in entries.items():
        if not isinstance(key, str) or len(key) != 64 or not isinstance(row, dict):
            raise QuickGateCacheStoreError("quick gate cache entry invalid")
        if set(row) != {"passed", "logs"} or not isinstance(row["passed"], bool) or not isinstance(row["logs"], list):
            raise QuickGateCacheStoreError("quick gate cache entry fields invalid")
        if len(row["logs"]) > 16:
            raise QuickGateCacheStoreError("quick gate cache logs too large")
        clean_logs = []
        for log in row["logs"]:
            if not isinstance(log, dict):
                raise QuickGateCacheStoreError("quick gate cache log invalid")
            command = log.get("command")
            exit_code = log.get("exit_code")
            output = log.get("output")
            if (
                not isinstance(command, list)
                or not all(isinstance(part, str) for part in command)
                or type(exit_code) is not int
                or not isinstance(output, str)
                or len(output) > 20000
            ):
                raise QuickGateCacheStoreError("quick gate cache log fields invalid")
            clean_logs.append({
                "command": command,
                "exit_code": exit_code,
                "output": output,
            })
        clean[key] = {"passed": row["passed"], "logs": clean_logs}
    return {
        "schema": data["schema"],
        "toolchain_fingerprint": fingerprint,
        "entries": clean,
    }


def _ref(github):
    refs = github.get("/git/matching-refs/heads/" + STATE_BRANCH)
    if not isinstance(refs, list):
        raise QuickGateCacheStoreError("memory branch lookup invalid")
    exact = [x for x in refs if isinstance(x, dict) and x.get("ref") == "refs/heads/" + STATE_BRANCH]
    if len(exact) > 1:
        raise QuickGateCacheStoreError("memory branch ambiguous")
    return exact[0] if exact else None


def load(github):
    ref = _ref(github)
    if ref is None:
        return None
    head = ref.get("object", {}).get("sha")
    if not isinstance(head, str) or len(head) != 40:
        raise QuickGateCacheStoreError("memory branch head invalid")
    tree = github.get("/git/trees/" + head + "?recursive=1")
    if not isinstance(tree, dict) or tree.get("truncated") or not isinstance(tree.get("tree"), list):
        raise QuickGateCacheStoreError("memory tree invalid")
    item = next(
        (
            x
            for x in tree["tree"]
            if isinstance(x, dict) and x.get("path") == STATE_PATH and x.get("type") == "blob"
        ),
        None,
    )
    if item is None:
        return None
    blob = github.get("/git/blobs/" + item.get("sha", ""))
    if not isinstance(blob, dict) or blob.get("encoding") != "base64":
        raise QuickGateCacheStoreError("quick gate cache blob invalid")
    try:
        raw = base64.b64decode(blob["content"], validate=False)
        if len(raw) > MAX_BYTES:
            raise QuickGateCacheStoreError("quick gate cache too large")
        value = json.loads(raw.decode("utf-8"))
    except (KeyError, ValueError, UnicodeDecodeError, json.JSONDecodeError):
        raise QuickGateCacheStoreError("quick gate cache unreadable") from None
    return _validate(value)


def save(github, data):
    data = _validate(data)
    ref = _ref(github)
    if ref is None:
        meta = github.get("")
        default = meta.get("default_branch") if isinstance(meta, dict) else None
        if not isinstance(default, str) or not default:
            raise QuickGateCacheStoreError("default branch invalid")
        info = github.get("/branches/" + default)
        parent = info.get("commit", {}).get("sha") if isinstance(info, dict) else None
    else:
        parent = ref.get("object", {}).get("sha")
        existing = load(github)
        if existing == data:
            return parent
    if not isinstance(parent, str) or len(parent) != 40:
        raise QuickGateCacheStoreError("memory branch parent invalid")
    commit_info = github.get("/git/commits/" + parent)
    base_tree = commit_info.get("tree", {}).get("sha") if isinstance(commit_info, dict) else None
    if not isinstance(base_tree, str) or len(base_tree) != 40:
        raise QuickGateCacheStoreError("memory base tree invalid")
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
        raise QuickGateCacheStoreError("quick gate cache tree creation failed")
    commit = github.call(
        "POST",
        github.repo + "/git/commits",
        {
            "message": "Persist quick gate cache",
            "tree": tree_sha,
            "parents": [parent],
        },
    )
    commit_sha = commit.get("sha") if isinstance(commit, dict) else None
    if not isinstance(commit_sha, str) or len(commit_sha) != 40:
        raise QuickGateCacheStoreError("quick gate cache commit creation failed")
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
        raise QuickGateCacheStoreError("local quick gate cache unreadable") from None
    return save(github, _validate(data))
