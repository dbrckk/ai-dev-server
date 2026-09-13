"""Persist role-scoped provider metrics on the trusted memory branch."""
from __future__ import annotations

import base64
import json
from pathlib import Path

from provider_metrics import load as load_local

STATE_BRANCH = "studio-project-memory"
STATE_PATH = ".studio-memory/provider-metrics.json"
MAX_BYTES = 256 * 1024
MAX_ROWS = 128


class ProviderMetricsStoreError(RuntimeError):
    pass


def _validate(data):
    if not isinstance(data, dict) or len(data) > MAX_ROWS:
        raise ProviderMetricsStoreError("provider metrics invalid")
    clean = {}
    for key, row in data.items():
        if not isinstance(key, str) or ":" not in key or not isinstance(row, dict):
            raise ProviderMetricsStoreError("provider metrics entry invalid")
        if set(row) != {"calls", "ema_latency_seconds"}:
            raise ProviderMetricsStoreError("provider metrics fields invalid")
        calls = row["calls"]
        ema = row["ema_latency_seconds"]
        if type(calls) is not int or calls < 0:
            raise ProviderMetricsStoreError("provider metrics calls invalid")
        if not isinstance(ema, (int, float)) or isinstance(ema, bool) or ema < 0:
            raise ProviderMetricsStoreError("provider metrics latency invalid")
        clean[key] = {"calls": calls, "ema_latency_seconds": float(ema)}
    return clean


def _ref(github):
    refs = github.get("/git/matching-refs/heads/" + STATE_BRANCH)
    if not isinstance(refs, list):
        raise ProviderMetricsStoreError("memory branch lookup invalid")
    exact = [x for x in refs if isinstance(x, dict) and x.get("ref") == "refs/heads/" + STATE_BRANCH]
    if len(exact) > 1:
        raise ProviderMetricsStoreError("memory branch ambiguous")
    return exact[0] if exact else None


def load(github):
    ref = _ref(github)
    if ref is None:
        return {}
    head = ref.get("object", {}).get("sha")
    if not isinstance(head, str) or len(head) != 40:
        raise ProviderMetricsStoreError("memory branch head invalid")
    tree = github.get("/git/trees/" + head + "?recursive=1")
    if not isinstance(tree, dict) or tree.get("truncated") or not isinstance(tree.get("tree"), list):
        raise ProviderMetricsStoreError("memory tree invalid")
    item = next((x for x in tree["tree"] if isinstance(x, dict) and x.get("path") == STATE_PATH and x.get("type") == "blob"), None)
    if item is None:
        return {}
    blob = github.get("/git/blobs/" + item.get("sha", ""))
    if not isinstance(blob, dict) or blob.get("encoding") != "base64":
        raise ProviderMetricsStoreError("provider metrics blob invalid")
    try:
        raw = base64.b64decode(blob["content"], validate=False)
        if len(raw) > MAX_BYTES:
            raise ProviderMetricsStoreError("provider metrics too large")
        value = json.loads(raw.decode("utf-8"))
    except (KeyError, ValueError, UnicodeDecodeError, json.JSONDecodeError):
        raise ProviderMetricsStoreError("provider metrics unreadable") from None
    return _validate(value)


def save(github, data):
    data = _validate(data)
    ref = _ref(github)
    if ref is None:
        meta = github.get("")
        default = meta.get("default_branch") if isinstance(meta, dict) else None
        if not isinstance(default, str) or not default:
            raise ProviderMetricsStoreError("default branch invalid")
        info = github.get("/branches/" + default)
        parent = info.get("commit", {}).get("sha") if isinstance(info, dict) else None
    else:
        parent = ref.get("object", {}).get("sha")
        if load(github) == data:
            return parent
    if not isinstance(parent, str) or len(parent) != 40:
        raise ProviderMetricsStoreError("memory branch parent invalid")
    commit_info = github.get("/git/commits/" + parent)
    base_tree = commit_info.get("tree", {}).get("sha") if isinstance(commit_info, dict) else None
    if not isinstance(base_tree, str) or len(base_tree) != 40:
        raise ProviderMetricsStoreError("memory base tree invalid")
    tree = github.call("POST", github.repo + "/git/trees", {
        "base_tree": base_tree,
        "tree": [{
            "path": STATE_PATH,
            "mode": "100644",
            "type": "blob",
            "content": json.dumps(data, sort_keys=True),
        }],
    })
    tree_sha = tree.get("sha") if isinstance(tree, dict) else None
    if not isinstance(tree_sha, str) or len(tree_sha) != 40:
        raise ProviderMetricsStoreError("provider metrics tree creation failed")
    commit = github.call("POST", github.repo + "/git/commits", {
        "message": "Persist provider latency metrics",
        "tree": tree_sha,
        "parents": [parent],
    })
    commit_sha = commit.get("sha") if isinstance(commit, dict) else None
    if not isinstance(commit_sha, str) or len(commit_sha) != 40:
        raise ProviderMetricsStoreError("provider metrics commit creation failed")
    if ref is None:
        github.call("POST", github.repo + "/git/refs", {"ref": "refs/heads/" + STATE_BRANCH, "sha": commit_sha})
    else:
        github.call("PATCH", github.repo + "/git/refs/heads/" + STATE_BRANCH, {"sha": commit_sha, "force": False})
    return commit_sha


def restore_local(github, path: Path):
    data = load(github)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return data


def persist_local(github, path: Path):
    path = Path(path)
    data = load_local(path) if path.is_file() else {}
    return save(github, _validate(data))
