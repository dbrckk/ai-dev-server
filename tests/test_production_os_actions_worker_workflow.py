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


def test_actions_worker_enables_real_mobile_specialist_runtime_on_idle_fallback():
    assert "PRODUCTION_OS_WORKER_SPECIALTIES: mobile" in WORKFLOW
    assert "Process one base-capability Production-OS job" in WORKFLOW
    assert "PRODUCTION_OS_WORKER_SPECIALTIES: ''" in WORKFLOW
    assert "--status-file" in WORKFLOW
    assert "mobile_fallback" in WORKFLOW
    assert "if: steps.base_job.outputs.mobile_fallback == 'true'" in WORKFLOW
    assert "Prepare native mobile validation runtime" in WORKFLOW
    assert "Process one mobile-capable Production-OS job" in WORKFLOW
    for command in ("adb", "sdkmanager", "avdmanager", "emulator"):
        assert command in WORKFLOW
    assert "/dev/kvm" in WORKFLOW
    assert "emulator -accel-check" in WORKFLOW
    assert "scripts/bootstrap-android-ci.sh" in WORKFLOW


def test_actions_worker_skips_heavy_setup_only_on_confirmed_empty_queue():
    connection = WORKFLOW.index("Validate Production-OS connection")
    readiness = WORKFLOW.index("Wait for Production-OS readiness")
    probe = WORKFLOW.index("Probe compatible Production-OS work")
    checkout = WORKFLOW.index("Checkout AI Dev Server")
    setup_python = WORKFLOW.index("Set up Python")
    credentials = WORKFLOW.index("Validate execution credentials")
    install = WORKFLOW.index("Install autonomous coding agent")
    base = WORKFLOW.index("Process one base-capability Production-OS job")
    android = WORKFLOW.index("Prepare native mobile validation runtime")
    assert connection < readiness < probe < checkout < setup_python
    assert setup_python < credentials < install < base < android
    assert 'base + "/v1/jobs/availability"' in WORKFLOW
    assert '"mobile-ui-validation"' in WORKFLOW
    assert '"visual-asset-production"' in WORKFLOW
    assert '"visual-asset-3d-production"' in WORKFLOW
    assert "has_work = True" in WORKFLOW
    assert 'has_work = bool(body.get("available"))' in WORKFLOW
    assert 'probe_status = "fallback"' in WORKFLOW
    assert "Backward-compatible fail-open behavior" in WORKFLOW
    assert "if: steps.queue_probe.outputs.has_work != 'false'" in WORKFLOW
    assert "Queue preflight:" in WORKFLOW


def test_actions_worker_checks_backend_readiness_before_heavy_setup():
    readiness = WORKFLOW.index("Wait for Production-OS readiness")
    checkout = WORKFLOW.index("Checkout AI Dev Server")
    install = WORKFLOW.index("Install autonomous coding agent")
    android = WORKFLOW.index("Prepare native mobile validation runtime")
    assert readiness < checkout < install < android
    assert 'url = base + "/readyz"' in WORKFLOW
    assert "attempts = 12" in WORKFLOW
    assert "timeout=5" in WORKFLOW
    assert "Production-OS readiness failed after bounded retries" in WORKFLOW


def test_actions_worker_defers_execution_secrets_and_toolchains_until_work_exists():
    assert "python3 - <<'PY'" in WORKFLOW
    assert "Missing required GitHub Actions secret: PRODUCTION_OS_WORKER_TOKEN" in WORKFLOW
    assert "Validate execution credentials" in WORKFLOW
    assert "STUDIO_GITHUB_TOKEN STUDIO_API_KEY" in WORKFLOW
    assert WORKFLOW.count("if: steps.queue_probe.outputs.has_work != 'false'") >= 4
    probe = WORKFLOW.index("Probe compatible Production-OS work")
    credentials = WORKFLOW.index("Validate execution credentials")
    assert probe < credentials


def test_actions_worker_is_single_flight_and_bounded():
    assert "group: production-os-actions-worker" in WORKFLOW
    assert "cancel-in-progress: false" in WORKFLOW
    assert "timeout-minutes: 90" in WORKFLOW
    assert "Process one base-capability Production-OS job" in WORKFLOW
    assert "Process one mobile-capable Production-OS job" in WORKFLOW
