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



def test_actions_worker_reports_rejected_worker_token_without_exposing_it():
    assert "if exc.code in {401, 403}:" in WORKFLOW
    assert "Production-OS worker token rejected" in WORKFLOW
    assert "synchronize " in WORKFLOW
    assert "PRODUCTION_OS_WORKER_TOKEN between GitHub Actions" in WORKFLOW


def test_actions_worker_availability_probe_fails_closed():
    assert "Production-OS availability probe failed: HTTP" in WORKFLOW
    assert "Production-OS availability probe returned invalid JSON" in WORKFLOW
    assert "except urllib.error.HTTPError as exc:" in WORKFLOW
    assert "raise SystemExit(" in WORKFLOW


def test_actions_worker_bootstraps_remote_asset_forge_before_preflight():
    checkout = WORKFLOW.index("Checkout Production-OS tools")
    install = WORKFLOW.index("Install Production-OS remote tools")
    probe = WORKFLOW.index("Probe compatible Production-OS work")
    assert checkout < install < probe
    assert "repository: dbrckk/Production-OS" in WORKFLOW
    assert "b8be27a65200629553200f912b0caa9112ff8f4c" in WORKFLOW
    assert "python -m pip install ./production-os-tools" in WORKFLOW
    assert "production-os asset-forge-batch --help" in WORKFLOW
    assert "GITHUB_TOKEN: ${{ secrets.STUDIO_GITHUB_TOKEN || secrets.CODESPACES_PAT }}" in WORKFLOW


def test_actions_worker_preflight_uses_runtime_capability_detection():
    probe = WORKFLOW.split("- name: Probe compatible Production-OS work", 1)[1]
    assert "from production_os_worker import worker_capabilities" in probe
    assert 'base_env["PRODUCTION_OS_WORKER_SPECIALTIES"] = ""' in probe
    assert "base_capabilities = worker_capabilities(base_env)" in probe
    assert '"visual-asset-production"' not in probe.split("def probe", 1)[0]


def test_actions_worker_isolates_production_os_cli_from_studio_pythonpath():
    assert "env -u PYTHONPATH python -m pip install ./production-os-tools" in WORKFLOW
    assert "env -u PYTHONPATH production-os asset-forge-batch --help" in WORKFLOW


def test_actions_worker_has_resilient_model_provider_fallbacks():
    assert "STUDIO_PROVIDERS_JSON:" in WORKFLOW
    assert "nvidia-lightning-fallback" in WORKFLOW
    assert "nvidia/nemotron-3.5-lightning-30b-a3b" in WORKFLOW
    assert "poolside-laguna-fallback" in WORKFLOW
    assert "poolside/laguna-xs-2.1" in WORKFLOW


def test_actions_worker_fails_ci_when_production_result_failed():
    assert 'if status == "failed":' in WORKFLOW
    assert 'Production-OS base-capability job failed' in WORKFLOW
