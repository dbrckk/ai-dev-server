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


def test_actions_worker_checks_backend_readiness_and_queue_before_heavy_setup():
    readiness = WORKFLOW.index("Wait for Production-OS readiness")
    probe = WORKFLOW.index("Probe compatible Production-OS work")
    install = WORKFLOW.index("Install autonomous coding agent")
    android = WORKFLOW.index("Prepare native mobile validation runtime")
    assert readiness < probe < install < android
    assert 'url = base + "/readyz"' in WORKFLOW
    assert "attempts = 12" in WORKFLOW
    assert "timeout=5" in WORKFLOW
    assert "Production-OS readiness failed after bounded retries" in WORKFLOW


def test_actions_worker_is_single_flight_and_bounded():
    assert "group: production-os-actions-worker" in WORKFLOW
    assert "cancel-in-progress: false" in WORKFLOW
    assert "timeout-minutes: 90" in WORKFLOW
    assert "Process one base-capability Production-OS job" in WORKFLOW
    assert "Process one mobile-capable Production-OS job" in WORKFLOW



def test_actions_worker_exits_heavy_path_when_no_compatible_work_exists():
    assert 'base + "/v1/jobs/availability"' in WORKFLOW
    assert '"mobile-ui-validation"' in WORKFLOW
    assert "base_available" in WORKFLOW
    assert "mobile_available" in WORKFLOW
    assert "any_available" in WORKFLOW
    assert "if: steps.queue_probe.outputs.any_available == 'true'" in WORKFLOW
    install = WORKFLOW.split("- name: Install autonomous coding agent", 1)[1]
    assert "if: steps.queue_probe.outputs.any_available == 'true'" in install[:300]


def test_actions_worker_skips_base_pass_for_mobile_only_work():
    base_step = WORKFLOW.split(
        "- name: Process one base-capability Production-OS job", 1
    )[1].split("- name: Prepare native mobile validation runtime", 1)[0]
    assert "if: steps.queue_probe.outputs.base_available == 'true'" in base_step
    mobile_condition = (
        "steps.queue_probe.outputs.mobile_only == 'true' || "
        "(steps.queue_probe.outputs.mobile_available == 'true' && "
        "steps.base_job.outputs.mobile_fallback == 'true')"
    )
    assert WORKFLOW.count(mobile_condition) == 2


def test_actions_worker_does_not_prepare_android_for_base_only_claim_race():
    assert 'mobile_available = int(mobile_work.get("mobile_jobs") or 0) > 0' in WORKFLOW
    assert "steps.queue_probe.outputs.mobile_available == 'true'" in WORKFLOW
