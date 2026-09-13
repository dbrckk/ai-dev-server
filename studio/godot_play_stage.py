"""Trusted Google Play submission stage for a validated Godot release."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

from core import StudioError, canonical, request_check
from godot_preview import _publish, _restore
from play_publisher import publication_credentials, publish_bundle
from run import GitHub


def _human_action(state: dict, action: str, detail: str) -> dict:
    state["status"] = "human_action_required"
    state["release_status"] = "human_action_required"
    state["human_action"] = {"action": action, "detail": detail}
    state["completion"] = {
        "finished": False,
        "next_stage": "godot_play_submission",
        "reason": detail,
    }
    return state


def execute(
    req: dict,
    root: Path,
    out: Path,
    github,
    *,
    env: dict | None = None,
    publisher=publish_bundle,
) -> dict:
    req = request_check(req)
    root.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)
    if any(root.iterdir()):
        raise StudioError("Workspace must be fresh for Godot Play submission stage")

    branch = "studio/" + req["id"]
    state, parent, checkpoint = _restore(github, branch, root)
    if not checkpoint or not isinstance(state, dict):
        raise StudioError("Godot Play submission requires studio checkpoint")
    if state.get("engine") != "godot" or state.get("status") != "godot_technical_store_ready":
        raise StudioError("Godot Play submission requires technical store-ready checkpoint")
    completion = state.get("completion")
    if (
        not isinstance(completion, dict)
        or completion.get("finished") is not False
        or completion.get("next_stage") != "godot_play_submission"
    ):
        raise StudioError("Godot Play submission checkpoint contract invalid")

    publication = req.get("play_publish")
    if not isinstance(publication, dict) or publication.get("enabled") is not True:
        _human_action(
            state,
            "manual_play_submission_required",
            "Play publication was not explicitly enabled in the immutable request.",
        )
    else:
        artifact_info = state.get("release_artifact") or {}
        expected_hash = artifact_info.get("aab_sha256")
        package_name = artifact_info.get("package")
        artifact = out / "app-release.aab"
        if (
            not isinstance(expected_hash, str)
            or len(expected_hash) != 64
            or not artifact.is_file()
            or hashlib.sha256(artifact.read_bytes()).hexdigest() != expected_hash
        ):
            _human_action(
                state,
                "signed_aab_artifact_required",
                "The exact validated signed AAB must be present in the trusted run output before Play submission.",
            )
        elif not isinstance(package_name, str) or not package_name:
            raise StudioError("Godot release package name missing")
        else:
            current = os.environ if env is None else env
            credentials = publication_credentials(current)
            if not credentials.get("available"):
                _human_action(
                    state,
                    credentials.get("blocker") or "play_access_token_required",
                    "Provide an authorized short-lived Android Publisher access token.",
                )
            else:
                commit = publication.get("commit") is True
                track = publication.get("track", "internal")
                if commit and current.get("STUDIO_PLAY_COMMIT_APPROVED") != "1":
                    _human_action(
                        state,
                        "play_commit_approval_required",
                        "Set STUDIO_PLAY_COMMIT_APPROVED=1 in the trusted runner to authorize the Play edit commit.",
                    )
                elif commit and track == "production" and current.get("STUDIO_PLAY_PRODUCTION_APPROVED") != "1":
                    _human_action(
                        state,
                        "play_production_approval_required",
                        "Set STUDIO_PLAY_PRODUCTION_APPROVED=1 after explicit production-release approval.",
                    )
                else:
                    evidence = publisher(
                        package_name=package_name,
                        signed_aab=artifact,
                        track=track,
                        access_token=credentials["access_token"],
                        commit=commit,
                    )
                    if (
                        not isinstance(evidence, dict)
                        or evidence.get("passed") is not True
                        or evidence.get("edit_validated") is not True
                        or bool(evidence.get("committed")) != commit
                    ):
                        raise StudioError("Godot Play publication evidence invalid")
                    evidence = dict(evidence)
                    evidence["artifact_sha256"] = expected_hash
                    evidence["certificate_sha256"] = artifact_info.get("certificate_sha256")
                    state["play_publish"] = evidence
                    coverage = dict(state.get("coverage") or {})
                    coverage["play_publish"] = True
                    state["coverage"] = coverage
                    state.pop("human_action", None)
                    state["status"] = "godot_published" if commit else "godot_play_validated"
                    state["release_status"] = "published" if commit else "play_validated"
                    state["completion"] = {
                        "finished": True,
                        "next_stage": None,
                        "reason": (
                            "Google Play edit committed."
                            if commit
                            else "Google Play edit validated without commit, as explicitly requested."
                        ),
                    }

    parent = _publish(github, branch, parent, root, state)
    state["checkpoint_commit"] = parent
    (out / "report.json").write_text(canonical(state))
    return state


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("request")
    parser.add_argument("--work", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    req = request_check(json.loads(Path(args.request).read_text()))
    state = execute(req, Path(args.work), Path(args.out), GitHub(req["target_repo"]))
    if state.get("status") == "human_action_required":
        return 2
    return 0 if state.get("completion", {}).get("finished") is True else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (StudioError, ValueError, OSError, json.JSONDecodeError) as exc:
        print(str(exc) if isinstance(exc, StudioError) else type(exc).__name__)
        raise SystemExit(1)
