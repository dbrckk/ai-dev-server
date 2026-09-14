"""Persist CAS promotion audit records on trusted memory branch."""
from __future__ import annotations

import base64
import json
from pathlib import Path

STATE_BRANCH = "studio-project-memory"
STATE_PATH = ".studio-memory/artifact-cas-audit.json"
MAX_BYTES = 512 * 1024
MAX_RECORDS = 512


class ArtifactCasAuditStoreError(RuntimeError):
    pass


def _validate(rows):
    if not isinstance(rows, list) or len(rows) > MAX_RECORDS:
        raise ArtifactCasAuditStoreError("artifact CAS audit invalid")
    clean = []
    previous = 0
    for row in rows:
        if (
            not isinstance(row, dict)
            or set(row) != {
                "sequence",
                "project_namespace",
                "artifact_class",
                "sha256",
                "size",
            }
            or type(row["sequence"]) is not int
            or row["sequence"] <= previous
            or not isinstance(row["project_namespace"], str)
            or not isinstance(row["artifact_class"], str)
            or not isinstance(row["sha256"], str)
            or len(row["sha256"]) != 64
            or type(row["size"]) is not int
            or row["size"] < 0
        ):
            raise ArtifactCasAuditStoreError("artifact CAS audit row invalid")
        previous = row["sequence"]
        clean.append(dict(row))
    return clean


def _ref(github):
    refs = github.get("/git/matching-refs/heads/" + STATE_BRANCH)
    if not isinstance(refs, list):
        raise ArtifactCasAuditStoreError("memory branch lookup invalid")
    exact = [
        x for x in refs
        if isinstance(x, dict) and x.get("ref") == "refs/heads/" + STATE_BRANCH
    ]
    if len(exact) > 1:
        raise ArtifactCasAuditStoreError("memory branch ambiguous")
    return exact[0] if exact else None


def load(github):
    ref = _ref(github)
    if ref is None:
        return None
    head = ref.get("object", {}).get("sha")
    if not isinstance(head, str) or len(head) != 40:
        raise ArtifactCasAuditStoreError("memory branch head invalid")
    tree = github.get("/git/trees/" + head + "?recursive=1")
    if not isinstance(tree, dict) or tree.get("truncated") or not isinstance(tree.get("tree"), list):
        raise ArtifactCasAuditStoreError("memory tree invalid")
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
        raise ArtifactCasAuditStoreError("artifact CAS audit blob invalid")
    try:
        raw = base64.b64decode(blob["content"], validate=False)
        if len(raw) > MAX_BYTES:
            raise ArtifactCasAuditStoreError("artifact CAS audit too large")
        rows = json.loads(raw.decode("utf-8"))
    except (KeyError, ValueError, UnicodeDecodeError, json.JSONDecodeError):
        raise ArtifactCasAuditStoreError("artifact CAS audit unreadable") from None
    return _validate(rows)


def save(github, rows):
    rows = _validate(rows)
    ref = _ref(github)
    if ref is None:
        meta = github.get("")
        default = meta.get("default_branch") if isinstance(meta, dict) else None
        if not isinstance(default, str) or not default:
            raise ArtifactCasAuditStoreError("default branch invalid")
        info = github.get("/branches/" + default)
        parent = info.get("commit", {}).get("sha") if isinstance(info, dict) else None
    else:
        parent = ref.get("object", {}).get("sha")
        if load(github) == rows:
            return parent
    if not isinstance(parent, str) or len(parent) != 40:
        raise ArtifactCasAuditStoreError("memory branch parent invalid")
    commit_info = github.get("/git/commits/" + parent)
    base_tree = commit_info.get("tree", {}).get("sha") if isinstance(commit_info, dict) else None
    if not isinstance(base_tree, str) or len(base_tree) != 40:
        raise ArtifactCasAuditStoreError("memory base tree invalid")
    tree = github.call(
        "POST",
        github.repo + "/git/trees",
        {
            "base_tree": base_tree,
            "tree": [{
                "path": STATE_PATH,
                "mode": "100644",
                "type": "blob",
                "content": json.dumps(rows, sort_keys=True),
            }],
        },
    )
    tree_sha = tree.get("sha") if isinstance(tree, dict) else None
    if not isinstance(tree_sha, str) or len(tree_sha) != 40:
        raise ArtifactCasAuditStoreError("artifact CAS audit tree creation failed")
    commit = github.call(
        "POST",
        github.repo + "/git/commits",
        {
            "message": "Persist artifact CAS promotion audit",
            "tree": tree_sha,
            "parents": [parent],
        },
    )
    commit_sha = commit.get("sha") if isinstance(commit, dict) else None
    if not isinstance(commit_sha, str) or len(commit_sha) != 40:
        raise ArtifactCasAuditStoreError("artifact CAS audit commit creation failed")
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
    rows = load(github)
    if rows is None:
        return None
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return rows


def persist_local(github, path: Path):
    path = Path(path)
    if not path.is_file():
        return None
    try:
        rows = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        raise ArtifactCasAuditStoreError("local artifact CAS audit unreadable") from None
    return save(github, _validate(rows))
