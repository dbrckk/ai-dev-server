"""GitHub-backed persistence for autonomous goal state outside main."""
from __future__ import annotations

import base64
import json
import re
from pathlib import Path

try:
    from .capability_registry import validate as validate_registry
    from .goal_engine import validate as validate_goal
    from .improvement_backlog import new_backlog, validate as validate_backlog
    from .capability_adaptation_state import validate as validate_adaptation_state
    from .capability_synthesis import validate_candidate_envelope
    from .generic_capability_isolated_validation import validate_isolated_validation_result
except ImportError:
    from capability_registry import validate as validate_registry
    from goal_engine import validate as validate_goal
    from improvement_backlog import new_backlog, validate as validate_backlog
    from capability_adaptation_state import validate as validate_adaptation_state
    from capability_synthesis import validate_candidate_envelope
    from generic_capability_isolated_validation import validate_isolated_validation_result

STATE_BRANCH = "studio-autonomy-state"
ROOT = ".studio-autonomy"
MAX_STATE_BYTES = 512 * 1024


class RemoteStateError(RuntimeError):
    pass


def _safe_project_id(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_.-]{1,80}", value):
        raise RemoteStateError("project id invalid")
    return value


def _paths(project_id):
    project_id = _safe_project_id(project_id)
    prefix = f"{ROOT}/{project_id}"
    return (
        prefix + "/goal.json",
        prefix + "/capabilities.json",
        prefix + "/improvement-backlog.json",
        prefix + "/improvement-goal.json",
        prefix + "/capability-adaptation.json",
        prefix + "/capability-candidate.json",
        prefix + "/capability-validation.json",
    )


def _exact_ref(github):
    refs = github.get("/git/matching-refs/heads/" + STATE_BRANCH)
    if not isinstance(refs, list):
        raise RemoteStateError("state branch lookup invalid")
    exact = [x for x in refs if isinstance(x, dict) and x.get("ref") == "refs/heads/" + STATE_BRANCH]
    if len(exact) > 1:
        raise RemoteStateError("state branch lookup ambiguous")
    return exact[0] if exact else None


def _decode_blob(github, sha):
    blob = github.get("/git/blobs/" + sha)
    if not isinstance(blob, dict) or blob.get("encoding") != "base64":
        raise RemoteStateError("state blob invalid")
    try:
        raw = base64.b64decode(blob["content"], validate=False)
        if len(raw) > MAX_STATE_BYTES:
            raise RemoteStateError("state blob too large")
        value = json.loads(raw.decode("utf-8"))
    except (KeyError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
        raise RemoteStateError("state blob unreadable") from None
    return value


def load(github, project_id):
    goal_path, registry_path, backlog_path, improvement_goal_path, adaptation_path, candidate_path, validation_path = _paths(project_id)
    ref = _exact_ref(github)
    if ref is None:
        return None
    head = ref.get("object", {}).get("sha")
    if not isinstance(head, str) or len(head) != 40:
        raise RemoteStateError("state branch head invalid")
    tree = github.get("/git/trees/" + head + "?recursive=1")
    if not isinstance(tree, dict) or tree.get("truncated") or not isinstance(tree.get("tree"), list):
        raise RemoteStateError("state tree invalid")
    matches = {item.get("path"): item for item in tree["tree"] if isinstance(item, dict) and item.get("type") == "blob"}
    goal_item = matches.get(goal_path)
    registry_item = matches.get(registry_path)
    backlog_item = matches.get(backlog_path)
    improvement_goal_item = matches.get(improvement_goal_path)
    adaptation_item = matches.get(adaptation_path)
    candidate_item = matches.get(candidate_path)
    validation_item = matches.get(validation_path)
    if goal_item is None and registry_item is None:
        return None
    if goal_item is None or registry_item is None:
        raise RemoteStateError("remote autonomous state incomplete")
    goal = validate_goal(_decode_blob(github, goal_item.get("sha")))
    registry = validate_registry(_decode_blob(github, registry_item.get("sha")))
    backlog = new_backlog() if backlog_item is None else validate_backlog(_decode_blob(github, backlog_item.get("sha")))
    improvement_goal = None if improvement_goal_item is None else validate_goal(_decode_blob(github, improvement_goal_item.get("sha")))
    adaptation = None if adaptation_item is None else validate_adaptation_state(_decode_blob(github, adaptation_item.get("sha")))
    candidate = None if candidate_item is None else validate_candidate_envelope(_decode_blob(github, candidate_item.get("sha")))
    validation = None if validation_item is None else validate_isolated_validation_result(_decode_blob(github, validation_item.get("sha")))
    return {
        "goal": goal,
        "registry": registry,
        "backlog": backlog,
        "improvement_goal": improvement_goal,
        "capability_adaptation": adaptation,
        "capability_candidate": candidate,
        "capability_validation": validation,
        "head_sha": head,
    }


def save(github, project_id, goal, registry, backlog=None, improvement_goal=None, capability_adaptation=None, capability_candidate=None, capability_validation=None):
    goal_path, registry_path, backlog_path, improvement_goal_path, adaptation_path, candidate_path, validation_path = _paths(project_id)
    validate_goal(goal)
    validate_registry(registry)
    backlog = new_backlog() if backlog is None else validate_backlog(backlog)
    if improvement_goal is not None:
        improvement_goal = validate_goal(improvement_goal)
    if capability_adaptation is not None:
        capability_adaptation = validate_adaptation_state(capability_adaptation)
    if capability_candidate is not None:
        capability_candidate = validate_candidate_envelope(capability_candidate)
    if capability_validation is not None:
        capability_validation = validate_isolated_validation_result(capability_validation)
    ref = _exact_ref(github)
    if ref is None:
        meta = github.get("")
        default = meta.get("default_branch") if isinstance(meta, dict) else None
        if not isinstance(default, str) or not default:
            raise RemoteStateError("default branch invalid")
        info = github.get("/branches/" + default)
        parent = info.get("commit", {}).get("sha") if isinstance(info, dict) else None
        if not isinstance(parent, str) or len(parent) != 40:
            raise RemoteStateError("default branch head invalid")
    else:
        parent = ref.get("object", {}).get("sha")
        if not isinstance(parent, str) or len(parent) != 40:
            raise RemoteStateError("state branch head invalid")
    commit_info = github.get("/git/commits/" + parent)
    base_tree = commit_info.get("tree", {}).get("sha") if isinstance(commit_info, dict) else None
    if not isinstance(base_tree, str) or len(base_tree) != 40:
        raise RemoteStateError("state base tree invalid")
    entries = [
        {"path": goal_path, "mode": "100644", "type": "blob", "content": json.dumps(goal, sort_keys=True, ensure_ascii=False)},
        {"path": registry_path, "mode": "100644", "type": "blob", "content": json.dumps(registry, sort_keys=True, ensure_ascii=False)},
        {"path": backlog_path, "mode": "100644", "type": "blob", "content": json.dumps(backlog, sort_keys=True, ensure_ascii=False)},
    ]
    if improvement_goal is not None:
        entries.append({"path": improvement_goal_path, "mode": "100644", "type": "blob", "content": json.dumps(improvement_goal, sort_keys=True, ensure_ascii=False)})
    if capability_adaptation is not None:
        entries.append({"path": adaptation_path, "mode": "100644", "type": "blob", "content": json.dumps(capability_adaptation, sort_keys=True, ensure_ascii=False)})
    if capability_candidate is not None:
        entries.append({"path": candidate_path, "mode": "100644", "type": "blob", "content": json.dumps(capability_candidate, sort_keys=True, ensure_ascii=False)})
    if capability_validation is not None:
        entries.append({"path": validation_path, "mode": "100644", "type": "blob", "content": json.dumps(capability_validation, sort_keys=True, ensure_ascii=False)})
    tree = github.call("POST", github.repo + "/git/trees", {"base_tree": base_tree, "tree": entries})
    tree_sha = tree.get("sha") if isinstance(tree, dict) else None
    if not isinstance(tree_sha, str) or len(tree_sha) != 40:
        raise RemoteStateError("state tree creation failed")
    commit = github.call("POST", github.repo + "/git/commits", {
        "message": "Persist autonomous state: " + project_id,
        "tree": tree_sha,
        "parents": [parent],
    })
    commit_sha = commit.get("sha") if isinstance(commit, dict) else None
    if not isinstance(commit_sha, str) or len(commit_sha) != 40:
        raise RemoteStateError("state commit creation failed")
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


def restore_local(github, project_id, project_out):
    remote = load(github, project_id)
    if remote is None:
        return False
    root = Path(project_out) / ".autonomy"
    root.mkdir(parents=True, exist_ok=True)
    (root / "goal.json").write_text(json.dumps(remote["goal"], sort_keys=True, ensure_ascii=False, indent=2) + "\n")
    (root / "capabilities.json").write_text(json.dumps(remote["registry"], sort_keys=True, ensure_ascii=False, indent=2) + "\n")
    (root / "improvement-backlog.json").write_text(json.dumps(remote["backlog"], sort_keys=True, ensure_ascii=False, indent=2) + "\n")
    if remote["improvement_goal"] is not None:
        (root / "improvement-goal.json").write_text(json.dumps(remote["improvement_goal"], sort_keys=True, ensure_ascii=False, indent=2) + "\n")
    if remote["capability_adaptation"] is not None:
        (root / "capability-adaptation.json").write_text(json.dumps(remote["capability_adaptation"], sort_keys=True, ensure_ascii=False, indent=2) + "\n")
    if remote["capability_candidate"] is not None:
        (root / "capability-candidate.json").write_text(json.dumps(remote["capability_candidate"], sort_keys=True, ensure_ascii=False, indent=2) + "\n")
    if remote["capability_validation"] is not None:
        (root / "capability-validation.json").write_text(json.dumps(remote["capability_validation"], sort_keys=True, ensure_ascii=False, indent=2) + "\n")
    return True


def persist_local(github, project_id, project_out):
    root = Path(project_out) / ".autonomy"
    try:
        goal = json.loads((root / "goal.json").read_text())
        registry = json.loads((root / "capabilities.json").read_text())
        backlog_path = root / "improvement-backlog.json"
        backlog = json.loads(backlog_path.read_text()) if backlog_path.is_file() else new_backlog()
        improvement_goal_path = root / "improvement-goal.json"
        improvement_goal = json.loads(improvement_goal_path.read_text()) if improvement_goal_path.is_file() else None
        adaptation_path = root / "capability-adaptation.json"
        capability_adaptation = json.loads(adaptation_path.read_text()) if adaptation_path.is_file() else None
        candidate_path = root / "capability-candidate.json"
        capability_candidate = json.loads(candidate_path.read_text()) if candidate_path.is_file() else None
        validation_path = root / "capability-validation.json"
        capability_validation = json.loads(validation_path.read_text()) if validation_path.is_file() else None
    except (OSError, json.JSONDecodeError):
        raise RemoteStateError("local autonomous state unavailable") from None
    validate_goal(goal)
    validate_registry(registry)
    validate_backlog(backlog)
    if improvement_goal is not None:
        validate_goal(improvement_goal)
    if capability_adaptation is not None:
        validate_adaptation_state(capability_adaptation)
    if capability_candidate is not None:
        validate_candidate_envelope(capability_candidate)
    if capability_validation is not None:
        validate_isolated_validation_result(capability_validation)
    remote = load(github, project_id)
    if (remote is not None and remote["goal"] == goal and remote["registry"] == registry
            and remote["backlog"] == backlog
            and remote.get("improvement_goal") == improvement_goal
            and remote.get("capability_adaptation") == capability_adaptation
            and remote.get("capability_candidate") == capability_candidate
            and remote.get("capability_validation") == capability_validation):
        return remote["head_sha"]
    return save(github, project_id, goal, registry, backlog, improvement_goal, capability_adaptation, capability_candidate, capability_validation)
