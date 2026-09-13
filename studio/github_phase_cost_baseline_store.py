"""Persist historical phase-cost baselines."""
from __future__ import annotations

import base64
import json
from pathlib import Path

from phase_cost_baseline import load as load_local

STATE_BRANCH = "studio-project-memory"
STATE_PATH = ".studio-memory/phase-cost-baselines.json"
MAX_BYTES = 256 * 1024
MAX_ROWS = 128


class PhaseCostBaselineStoreError(RuntimeError):
    pass


def _validate(data):
    if not isinstance(data, dict) or len(data) > MAX_ROWS:
        raise PhaseCostBaselineStoreError("phase cost baseline invalid")
    clean = {}
    for key, row in data.items():
        if not isinstance(key, str) or not key or not isinstance(row, dict):
            raise PhaseCostBaselineStoreError("phase cost baseline entry invalid")
        if set(row) != {"samples", "ema_seconds", "ema_abs_deviation"}:
            raise PhaseCostBaselineStoreError("phase cost baseline fields invalid")
        samples = row["samples"]
        ema = row["ema_seconds"]
        mad = row["ema_abs_deviation"]
        if type(samples) is not int or samples < 0:
            raise PhaseCostBaselineStoreError("phase cost baseline samples invalid")
        if not isinstance(ema, (int, float)) or isinstance(ema, bool) or ema < 0:
            raise PhaseCostBaselineStoreError("phase cost baseline ema invalid")
        if not isinstance(mad, (int, float)) or isinstance(mad, bool) or mad < 0:
            raise PhaseCostBaselineStoreError("phase cost baseline deviation invalid")
        clean[key] = {
            "samples": samples,
            "ema_seconds": float(ema),
            "ema_abs_deviation": float(mad),
        }
    return clean


def _ref(github):
    refs = github.get("/git/matching-refs/heads/" + STATE_BRANCH)
    if not isinstance(refs, list):
        raise PhaseCostBaselineStoreError("memory branch lookup invalid")
    exact = [x for x in refs if isinstance(x, dict) and x.get("ref") == "refs/heads/" + STATE_BRANCH]
    if len(exact) > 1:
        raise PhaseCostBaselineStoreError("memory branch ambiguous")
    return exact[0] if exact else None


def load(github):
    ref = _ref(github)
    if ref is None:
        return {}
    head = ref.get("object", {}).get("sha")
    if not isinstance(head, str) or len(head) != 40:
        raise PhaseCostBaselineStoreError("memory branch head invalid")
    tree = github.get("/git/trees/" + head + "?recursive=1")
    if not isinstance(tree, dict) or tree.get("truncated") or not isinstance(tree.get("tree"), list):
        raise PhaseCostBaselineStoreError("memory tree invalid")
    item = next((x for x in tree["tree"] if isinstance(x, dict) and x.get("path") == STATE_PATH and x.get("type") == "blob"), None)
    if item is None:
        return {}
    blob = github.get("/git/blobs/" + item.get("sha", ""))
    if not isinstance(blob, dict) or blob.get("encoding") != "base64":
        raise PhaseCostBaselineStoreError("phase cost baseline blob invalid")
    try:
        raw = base64.b64decode(blob["content"], validate=False)
        if len(raw) > MAX_BYTES:
            raise PhaseCostBaselineStoreError("phase cost baseline too large")
        value = json.loads(raw.decode("utf-8"))
    except (KeyError, ValueError, UnicodeDecodeError, json.JSONDecodeError):
        raise PhaseCostBaselineStoreError("phase cost baseline unreadable") from None
    return _validate(value)


def save(github, data):
    data = _validate(data)
    ref = _ref(github)
    if ref is None:
        meta = github.get("")
        default = meta.get("default_branch") if isinstance(meta, dict) else None
        if not isinstance(default, str) or not default:
            raise PhaseCostBaselineStoreError("default branch invalid")
        info = github.get("/branches/" + default)
        parent = info.get("commit", {}).get("sha") if isinstance(info, dict) else None
    else:
        parent = ref.get("object", {}).get("sha")
        if load(github) == data:
            return parent
    if not isinstance(parent, str) or len(parent) != 40:
        raise PhaseCostBaselineStoreError("memory branch parent invalid")
    commit_info = github.get("/git/commits/" + parent)
    base_tree = commit_info.get("tree", {}).get("sha") if isinstance(commit_info, dict) else None
    if not isinstance(base_tree, str) or len(base_tree) != 40:
        raise PhaseCostBaselineStoreError("memory base tree invalid")
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
        raise PhaseCostBaselineStoreError("phase cost baseline tree creation failed")
    commit = github.call("POST", github.repo + "/git/commits", {
        "message": "Persist phase cost baselines",
        "tree": tree_sha,
        "parents": [parent],
    })
    commit_sha = commit.get("sha") if isinstance(commit, dict) else None
    if not isinstance(commit_sha, str) or len(commit_sha) != 40:
        raise PhaseCostBaselineStoreError("phase cost baseline commit creation failed")
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
