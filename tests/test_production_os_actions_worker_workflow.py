from pathlib import Path


WORKFLOW = Path(".github/workflows/production-os-actions-worker.yml").read_text(
    encoding="utf-8"
)


def test_actions_worker_has_no_codespace_dependency():
    assert "gh codespace" not in WORKFLOW
    assert "CODESPACE_NAME" not in WORKFLOW
    assert "runs-on: ubuntu-24.04" in WORKFLOW


def test_actions_worker_polls_production_os_on_schedule():
    assert "cron: '*/5 * * * *'" in WORKFLOW
    assert "workflow_dispatch:" in WORKFLOW
    assert "control/production-os-worker-kick.json" in WORKFLOW
    assert "studio/production_os_worker.py" in WORKFLOW
    assert "--once" in WORKFLOW


def test_actions_worker_uses_existing_secure_credentials():
    assert "secrets.PRODUCTION_OS_WORKER_TOKEN" in WORKFLOW
    assert "secrets.PRODUCTION_OS_OPERATOR_TOKEN" not in WORKFLOW
    assert "secrets.STUDIO_GITHUB_TOKEN || secrets.CODESPACES_PAT" in WORKFLOW
    assert "secrets.STUDIO_API_KEY || secrets.NVIDIA_NIM_API_KEY" in WORKFLOW
    assert "persist-credentials: false" in WORKFLOW


def test_actions_worker_enables_real_mobile_specialist_runtime():
    assert "PRODUCTION_OS_WORKER_SPECIALTIES: mobile" in WORKFLOW
    assert "Prepare native mobile validation runtime" in WORKFLOW
    for command in ("adb", "sdkmanager", "avdmanager", "emulator"):
        assert command in WORKFLOW
    assert "/dev/kvm" in WORKFLOW
    assert "emulator -accel-check" in WORKFLOW
    assert "scripts/bootstrap-android-ci.sh" in WORKFLOW


def test_actions_worker_is_single_flight_and_bounded():
    assert "group: production-os-actions-worker" in WORKFLOW
    assert "cancel-in-progress: false" in WORKFLOW
    assert "timeout-minutes: 90" in WORKFLOW
    assert "Process one Production-OS job" in WORKFLOW



def test_actions_worker_gates_expensive_setup_on_control_plane_readiness():
    readiness = WORKFLOW.index("Verify Production-OS readiness")
    agent_install = WORKFLOW.index("Install autonomous coding agent")
    mobile_setup = WORKFLOW.index("Prepare native mobile validation runtime")
    assert readiness < agent_install < mobile_setup
    assert "/readyz" in WORKFLOW
    assert "--connect-timeout 10" in WORKFLOW
    assert "--max-time 20" in WORKFLOW
    assert "for attempt in 1 2 3" in WORKFLOW
    assert 'payload.get("status") != "ready"' in WORKFLOW
    assert 'payload.get("database") != "reachable"' in WORKFLOW
