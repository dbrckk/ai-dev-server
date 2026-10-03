from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from production_os_worker import build_studio_request, worker_capabilities


def _job():
    return {
        "key": "job-visual-1",
        "repository": "dbrckk/example",
        "task": "Create premium visual assets",
        "payload": {
            "workflow_id": "f" * 32,
            "workflow_task_id": "implementation",
            "handoff": {
                "repository": "dbrckk/example",
                "task": "Create premium visual assets",
                "final_goal": "Create premium visual assets",
                "token_budget": 30000,
                "tool_contracts": {
                    "asset_forge": {
                        "request_schema": "asset-forge/production-request/v1",
                        "report_schema": "asset-forge/production-report/v1",
                        "command": "asset-forge fulfill",
                        "required_capability": "visual-asset-production",
                    }
                },
            },
        },
    }


def test_remote_asset_forge_adds_visual_capability_only_when_operational():
    with (
        patch("production_os_worker._asset_forge_operational_status", return_value=None),
        patch("production_os_worker._remote_asset_forge_operational", return_value=True),
    ):
        capabilities = worker_capabilities(
            {
                "PRODUCTION_OS_WORKER_SPECIALTIES": "",
                "GITHUB_TOKEN": "token",
            }
        )

    assert "visual-asset-production" in capabilities
    assert "visual-asset-3d-production" not in capabilities


def test_remote_asset_forge_is_not_advertised_when_unavailable():
    with (
        patch("production_os_worker._asset_forge_operational_status", return_value=None),
        patch("production_os_worker._remote_asset_forge_operational", return_value=False),
    ):
        capabilities = worker_capabilities(
            {"PRODUCTION_OS_WORKER_SPECIALTIES": ""}
        )

    assert "visual-asset-production" not in capabilities


def test_visual_handoff_uses_remote_batch_guidance_when_available():
    with patch(
        "production_os_worker._remote_asset_forge_operational",
        return_value=True,
    ):
        request = build_studio_request(_job())

    assert "production-os asset-forge-batch" in request["brief"]
    assert "--mode github" in request["brief"]
    assert "--target-worktree" in request["brief"]
    assert "Do not require local Cloudflare" in request["brief"]


def test_remote_asset_forge_probe_drops_studio_pythonpath():
    seen = {}

    def fake_run(command, **kwargs):
        seen["command"] = command
        seen["env"] = dict(kwargs["env"])

        class Completed:
            returncode = 0

        return Completed()

    with (
        patch("production_os_worker.shutil.which", return_value="/usr/bin/production-os"),
        patch("production_os_worker.subprocess.run", side_effect=fake_run),
    ):
        capabilities = worker_capabilities(
            {
                "PRODUCTION_OS_WORKER_SPECIALTIES": "",
                "GITHUB_TOKEN": "token",
                "PYTHONPATH": "studio",
                "PATH": "/usr/bin",
            }
        )

    assert "PYTHONPATH" not in seen["env"]
    assert seen["command"][-2:] == ["asset-forge-batch", "--probe"]
    assert "visual-asset-production" in capabilities


def test_remote_asset_forge_probe_failure_removes_visual_capability():
    def fake_run(command, **kwargs):
        class Completed:
            returncode = 1

        return Completed()

    with (
        patch("production_os_worker._asset_forge_operational_status", return_value=None),
        patch("production_os_worker.shutil.which", return_value="/usr/bin/production-os"),
        patch("production_os_worker.subprocess.run", side_effect=fake_run),
    ):
        capabilities = worker_capabilities(
            {
                "PRODUCTION_OS_WORKER_SPECIALTIES": "",
                "GITHUB_TOKEN": "token",
                "PATH": "/usr/bin",
            }
        )

    assert "visual-asset-production" not in capabilities
