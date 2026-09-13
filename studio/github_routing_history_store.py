"""Persist bounded routing decision history on the trusted memory branch."""
from __future__ import annotations

import base64
import json
from pathlib import Path

from routing_history import load as load_local

STATE_BRANCH = "studio-project-memory"
STATE_PATH = ".studio-memory/routing-history.json"
MAX_BYTES = 1024 * 1024
MAX_EVENTS = 500


class RoutingHistoryStoreError(RuntimeError):
    pass


def _validate(events):
    if not isinstance(events, list) or len(events) > MAX_EVENTS:
        raise RoutingHistoryStoreError("routing history invalid")
    clean = []
    for event in events:
        if not isinstance(event, dict):
            raise RoutingHistoryStoreError("routing history entry invalid")
        if event.get("kind") not in {"provider", "agent"}:
            raise RoutingHistoryStoreError("routing history kind invalid")
        if not isinstance(event.get("name"), str) or not event["name"]:
            raise RoutingHistoryStoreError("routing history name invalid")
        if not isinstance(event.get("role"), str) or not event["role"]:
            raise RoutingHistoryStoreError("routing history role invalid")
        if type(event.get("success")) is not bool:
            raise RoutingHistoryStoreError("routing history outcome invalid")
        if not isinstance(event.get("duration_seconds"), (int, float)) or isinstance(event.get("duration_seconds"), bool) or event["duration_seconds"] < 0:
            raise RoutingHistoryStoreError("routing history duration invalid")
        score = event.get("score")
        if not isinstance(score, dict) or set(score) != {"total", "components"} or not isinstance(score["components"], dict):
            raise RoutingHistoryStoreError("routing history score invalid")
        if not isinstance(score["total"], (int, float)) or isinstance(score["total"], bool):
            raise RoutingHistoryStoreError("routing history total invalid")
        components = {}
        for key, value in score["components"].items():
            if not isinstance(key, str) or not isinstance(value, (int, float)) or isinstance(value, bool):
                raise RoutingHistoryStoreError("routing history component invalid")
            components[key] = float(value)
        clean.append({
            "kind": event["kind"],
            "name": event["name"],
            "role": event["role"],
            "score": {"total": float(score["total"]), "components": components},
            "success": event["success"],
            "duration_seconds": float(event["duration_seconds"]),
        })
    return clean


def _ref(github):
    refs = github.get("/git/matching-refs/heads/" + STATE_BRANCH)
    if not isinstance(refs, list):
        raise RoutingHistoryStoreError("memory branch lookup invalid")
    exact = [x for x in refs if isinstance(x, dict) and x.get("ref") == "refs/heads/" + STATE_BRANCH]
    if len(exact) > 1:
        raise RoutingHistoryStoreError("memory branch ambiguous")
    return exact[0] if exact else None


def load(github):
    ref = _ref(github)
    if ref is None:
        return []
    head = ref.get("object", {}).get("sha")
    if not isinstance(head, str) or len(head) != 40:
        raise RoutingHistoryStoreError("memory branch head invalid")
    tree = github.get("/git/trees/" + head + "?recursive=1")
    if not isinstance(tree, dict) or tree.get("truncated") or not isinstance(tree.get("tree"), list):
        raise RoutingHistoryStoreError("memory tree invalid")
    item = next((x for x in tree["tree"] if isinstance(x, dict) and x.get("path") == STATE_PATH and x.get("type") == "blob"), None)
    if item is None:
        return []
    blob = github.get("/git/blobs/" + item.get("sha", ""))
    if not isinstance(blob, dict) or blob.get("encoding") != "base64":
        raise RoutingHistoryStoreError("routing history blob invalid")
    try:
        raw = base64.b64decode(blob["content"], validate=False)
        if len(raw) > MAX_BYTES:
            raise RoutingHistoryStoreError("routing history too large")
        value = json.loads(raw.decode("utf-8"))
    except (KeyError, ValueError, UnicodeDecodeError, json.JSONDecodeError):
        raise RoutingHistoryStoreError("routing history unreadable") from None
    return _validate(value)


def save(github, events):
    events = _validate(events)
    ref = _ref(github)
    if ref is None:
        meta = github.get("")
        default = meta.get("default_branch") if isinstance(meta, dict) else None
        if not isinstance(default, str) or not default:
            raise RoutingHistoryStoreError("default branch invalid")
        info = github.get("/branches/" + default)
        parent = info.get("commit", {}).get("sha") if isinstance(info, dict) else None
    else:
        parent = ref.get("object", {}).get("sha")
        if load(github) == events:
            return parent
    if not isinstance(parent, str) or len(parent) != 40:
        raise RoutingHistoryStoreError("memory branch parent invalid")
    commit_info = github.get("/git/commits/" + parent)
    base_tree = commit_info.get("tree", {}).get("sha") if isinstance(commit_info, dict) else None
    if not isinstance(base_tree, str) or len(base_tree) != 40:
        raise RoutingHistoryStoreError("memory base tree invalid")
    tree = github.call("POST", github.repo + "/git/trees", {
        "base_tree": base_tree,
        "tree": [{
            "path": STATE_PATH,
            "mode": "100644",
            "type": "blob",
            "content": json.dumps(events, sort_keys=True, ensure_ascii=False),
        }],
    })
    tree_sha = tree.get("sha") if isinstance(tree, dict) else None
    if not isinstance(tree_sha, str) or len(tree_sha) != 40:
        raise RoutingHistoryStoreError("routing history tree creation failed")
    commit = github.call("POST", github.repo + "/git/commits", {
        "message": "Persist routing decision history",
        "tree": tree_sha,
        "parents": [parent],
    })
    commit_sha = commit.get("sha") if isinstance(commit, dict) else None
    if not isinstance(commit_sha, str) or len(commit_sha) != 40:
        raise RoutingHistoryStoreError("routing history commit creation failed")
    if ref is None:
        github.call("POST", github.repo + "/git/refs", {"ref": "refs/heads/" + STATE_BRANCH, "sha": commit_sha})
    else:
        github.call("PATCH", github.repo + "/git/refs/heads/" + STATE_BRANCH, {"sha": commit_sha, "force": False})
    return commit_sha


def restore_local(github, path: Path):
    events = load(github)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(events, sort_keys=True, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return events


def persist_local(github, path: Path):
    path = Path(path)
    events = load_local(path) if path.is_file() else []
    return save(github, _validate(events))
