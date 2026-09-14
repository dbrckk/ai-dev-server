"""Persist artifact CAS retention statistics on trusted memory branch."""
from __future__ import annotations

import base64
import json
from pathlib import Path

STATE_BRANCH = "studio-project-memory"
STATE_PATH = ".studio-memory/artifact-cas-stats.json"
MAX_BYTES = 512 * 1024
MAX_BLOBS = 4096


class ArtifactCasStatsStoreError(RuntimeError):
    pass


def _validate(data):
    if not isinstance(data, dict):
        raise ArtifactCasStatsStoreError("artifact CAS stats invalid")
    if set(data) != {"schema", "clock", "blobs"}:
        raise ArtifactCasStatsStoreError("artifact CAS stats fields invalid")
    if data["schema"] != 1 or type(data["clock"]) is not int or data["clock"] < 0:
        raise ArtifactCasStatsStoreError("artifact CAS stats header invalid")
    blobs = data["blobs"]
    if not isinstance(blobs, dict) or len(blobs) > MAX_BLOBS:
        raise ArtifactCasStatsStoreError("artifact CAS stats blobs invalid")
    clean = {}
    for digest, row in blobs.items():
        if (
            not isinstance(digest, str)
            or len(digest) != 64
            or any(ch not in "0123456789abcdef" for ch in digest)
            or not isinstance(row, dict)
            or set(row) != {"hits", "last_used", "size", "rebuild_cost_seconds"}
            or type(row["hits"]) is not int
            or row["hits"] < 0
            or type(row["last_used"]) is not int
            or row["last_used"] < 0
            or type(row["size"]) is not int
            or row["size"] < 0
            or not isinstance(row["rebuild_cost_seconds"], (int, float))
            or row["rebuild_cost_seconds"] < 0
        ):
            raise ArtifactCasStatsStoreError("artifact CAS stats row invalid")
        clean[digest] = {
            "hits": row["hits"],
            "last_used": row["last_used"],
            "size": row["size"],
            "rebuild_cost_seconds": float(row["rebuild_cost_seconds"]),
        }
    return {"schema": 1, "clock": data["clock"], "blobs": clean}


def _ref(github):
    refs = github.get("/git/matching-refs/heads/" + STATE_BRANCH)
    if not isinstance(refs, list):
        raise ArtifactCasStatsStoreError("memory branch lookup invalid")
    exact = [
        x for x in refs
        if isinstance(x, dict) and x.get("ref") == "refs/heads/" + STATE_BRANCH
    ]
    if len(exact) > 1:
        raise ArtifactCasStatsStoreError("memory branch ambiguous")
    return exact[0] if exact else None


def load(github):
    ref = _ref(github)
    if ref is None:
        return None
    head = ref.get("object", {}).get("sha")
    if not isinstance(head, str) or len(head) != 40:
        raise ArtifactCasStatsStoreError("memory branch head invalid")
    tree = github.get("/git/trees/" + head + "?recursive=1")
    if not isinstance(tree, dict) or tree.get("truncated") or not isinstance(tree.get("tree"), list):
        raise ArtifactCasStatsStoreError("memory tree invalid")
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
        raise ArtifactCasStatsStoreError("artifact CAS stats blob invalid")
    try:
        raw = base64.b64decode(blob["content"], validate=False)
        if len(raw) > MAX_BYTES:
            raise ArtifactCasStatsStoreError("artifact CAS stats too large")
        data = json.loads(raw.decode("utf-8"))
    except (KeyError, ValueError, UnicodeDecodeError, json.JSONDecodeError):
        raise ArtifactCasStatsStoreError("artifact CAS stats unreadable") from None
    return _validate(data)


def save(github, data):
    data = _validate(data)
    ref = _ref(github)
    if ref is None:
        meta = github.get("")
        default = meta.get("default_branch") if isinstance(meta, dict) else None
        if not isinstance(default, str) or not default:
            raise ArtifactCasStatsStoreError("default branch invalid")
        info = github.get("/branches/" + default)
        parent = info.get("commit", {}).get("sha") if isinstance(info, dict) else None
    else:
        parent = ref.get("object", {}).get("sha")
        if load(github) == data:
            return parent
    if not isinstance(parent, str) or len(parent) != 40:
        raise ArtifactCasStatsStoreError("memory branch parent invalid")
    commit_info = github.get("/git/commits/" + parent)
    base_tree = commit_info.get("tree", {}).get("sha") if isinstance(commit_info, dict) else None
    if not isinstance(base_tree, str) or len(base_tree) != 40:
        raise ArtifactCasStatsStoreError("memory base tree invalid")
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
        raise ArtifactCasStatsStoreError("artifact CAS stats tree creation failed")
    commit = github.call(
        "POST",
        github.repo + "/git/commits",
        {
            "message": "Persist artifact CAS retention statistics",
            "tree": tree_sha,
            "parents": [parent],
        },
    )
    commit_sha = commit.get("sha") if isinstance(commit, dict) else None
    if not isinstance(commit_sha, str) or len(commit_sha) != 40:
        raise ArtifactCasStatsStoreError("artifact CAS stats commit creation failed")
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
        raise ArtifactCasStatsStoreError("local artifact CAS stats unreadable") from None
    return save(github, _validate(data))
