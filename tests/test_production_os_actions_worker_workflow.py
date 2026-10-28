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
    for cron in (
        "1-59/5 * * * *",
        "2-59/5 * * * *",
        "3-59/5 * * * *",
        "4-59/5 * * * *",
    ):
        assert f"cron: '{cron}'" not in WORKFLOW
    assert "workflow_dispatch:" in WORKFLOW
    assert "control/production-os-worker-kick.json" in WORKFLOW
    # The canary workflow enqueues the task before dispatching the worker.
    # A direct canary-file push wake races admission and creates duplicate runs.
    assert "control/production-os-worker-canary.json" not in WORKFLOW
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
    assert "steps.base_job.outputs.mobile_fallback == 'true'" in WORKFLOW
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
    # Prove the real embedded startup code rejects a missing Render server
    # on manual dispatch but conserves scheduled runner minutes, with no
    # checkout, worker registration or GitHub credential use.
    from contextlib import redirect_stdout
    from io import StringIO
    import json
    import os
    import tempfile
    import urllib.error
    import urllib.request
    from textwrap import dedent
    from unittest.mock import patch

    preflight = WORKFLOW.split(
        "- name: Wait for Production-OS readiness", 1
    )[1].split("\n      - name: Checkout AI Dev Server", 1)[0]
    script = dedent(
        preflight.split("python - <<'PY'\n", 1)[1].split("\n          PY", 1)[0]
    )
    executable = compile(script, "production-os-live-readiness", "exec")
    for gate in (
        "Checkout AI Dev Server", "Resolve qualified Production-OS revision",
        "Checkout Production-OS tools", "Set up Python",
        "Install Production-OS remote tools", "Validate worker configuration",
        "Probe compatible Production-OS work",
    ):
        section = WORKFLOW.split("      - name: " + gate + "\n", 1)[1]
        assert section.startswith("        if: steps.readiness.outputs.ready == 'true'\n")
    assert "id: readiness" in preflight
    assert "worker_task_executed" in preflight
    assert "class NoRedirect(urllib.request.HTTPRedirectHandler):" in preflight

    class MockResponse:
        status = 200

        def read(self, size):
            assert size <= 8192
            return b'{"status":"ready","database":"reachable"}'

        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

    class Endpoint:
        def __init__(self, available):
            self.available = available
            self.calls = []

        def open(self, request, timeout):
            self.calls.append((request.full_url, timeout))
            assert timeout == 5
            assert request.full_url == "https://example.org/readyz"
            assert request.get_header("Authorization") is None
            if self.available:
                return MockResponse()
            raise urllib.error.HTTPError(request.full_url, 503, "Service Unavailable", {}, None)

    def evaluate(event, available):
        endpoint = Endpoint(available)
        with tempfile.TemporaryDirectory() as root:
            env = {
                "GITHUB_EVENT_NAME": event,
                "GITHUB_OUTPUT": str(Path(root) / "output"),
                "GITHUB_STEP_SUMMARY": str(Path(root) / "summary"),
                "PRODUCTION_OS_STATUS_FILE": str(Path(root) / "output" / "worker.json"),
                "PRODUCTION_OS_URL": "https://example.org",
                "PRODUCTION_OS_WORKER_TOKEN": "test-secret-do-not-echo",
            }
            with patch.dict(os.environ, env), patch(
                "urllib.request.build_opener", return_value=endpoint,
            ), patch("time.sleep") as sleep:
                capture = StringIO()
                with redirect_stdout(capture):
                    if event != "schedule" and not available:
                        try:
                            exec(executable, {"__name__": "__main__"})
                        except SystemExit as exc:
                            assert "readiness failed after bounded retries" in str(exc)
                        else:
                            raise AssertionError("manual unavailable backend must fail")
                    else:
                        exec(executable, {"__name__": "__main__"})
            record = json.loads((Path(root) / "output" / "readiness.json").read_text())
            output = (Path(root) / "output").read_text()
            summary = (Path(root) / "summary").read_text()
            assert "test-secret-do-not-echo" not in str(record) + summary + capture.getvalue()
            return endpoint.calls, record, output, summary, sleep.call_count

    calls, record, output, summary, sleeps = evaluate("schedule", False)
    assert len(calls) == 6 and sleeps == 5
    assert record["status"] == "unavailable" and record["worker_task_executed"] is False
    assert record["reason"] == "http_503"
    assert output == "ready=false\n"
    assert "No task was executed" in summary

    calls, record, output, summary, sleeps = evaluate("workflow_dispatch", False)
    assert len(calls) == 12 and sleeps == 11
    assert record["status"] == "unavailable" and output == "ready=false\n"

    calls, record, output, summary, sleeps = evaluate("schedule", True)
    assert len(calls) == 1 and sleeps == 0
    assert record["status"] == "ready" and output == "ready=true\n"


def test_actions_worker_is_single_flight_and_bounded():
    assert "group: production-os-actions-worker" in WORKFLOW
    assert "cancel-in-progress: false" in WORKFLOW
    assert "timeout-minutes: 90" in WORKFLOW
    assert "Process one base-capability Production-OS job" in WORKFLOW
    assert "Process one mobile-capable Production-OS job" in WORKFLOW


def test_actions_worker_retains_hidden_autonomy_diagnostics():
    assert "include-hidden-files: true" in WORKFLOW
    assert '"queue-health.json"' in WORKFLOW
    assert '"failed_task_pipeline_status_sample"' in WORKFLOW
    assert '"GITHUB_STEP_SUMMARY"' in WORKFLOW



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
    probe = WORKFLOW.split(
        "- name: Probe compatible Production-OS work", 1
    )[1].split("- name: Install autonomous coding agent", 1)[0]
    assert "opener = urllib.request.build_opener(_NoRedirect())" in probe
    assert "with opener.open(request, timeout=10) as response:" in probe
    assert "urllib.request.urlopen(request, timeout=10)" not in probe


def test_actions_worker_bootstraps_remote_asset_forge_before_preflight():
    resolve = WORKFLOW.index("Resolve qualified Production-OS revision")
    checkout = WORKFLOW.index("Checkout Production-OS tools")
    install = WORKFLOW.index("Install Production-OS remote tools")
    probe = WORKFLOW.index("Probe compatible Production-OS work")
    assert resolve < checkout < install < probe
    assert "repository: dbrckk/Production-OS" in WORKFLOW
    assert "ref: ${{ steps.production_os_revision.outputs.sha }}" in WORKFLOW
    assert "python -m pip install ./production-os-tools" in WORKFLOW
    assert "production-os asset-forge-batch --help" in WORKFLOW
    assert "GITHUB_TOKEN: ${{ secrets.STUDIO_GITHUB_TOKEN || secrets.CODESPACES_PAT }}" in WORKFLOW


def test_actions_worker_resolves_only_ci_green_current_production_os_main():
    resolver = WORKFLOW.split(
        "- name: Resolve qualified Production-OS revision", 1
    )[1].split("- name: Checkout Production-OS tools", 1)[0]
    assert "actions/runs" in resolver
    assert "?branch=main&per_page=100" in resolver
    assert "/branches/main" in resolver
    assert "main_before" in resolver
    assert "main_after" in resolver
    assert "main_before != main_after" in resolver
    assert 'run.get("path") != ".github/workflows/ci.yml"' in resolver
    assert 'run.get("conclusion") != "success"' in resolver
    assert 'run.get("event") not in {"push", "workflow_dispatch"}' in resolver
    assert '"pull_request"' not in resolver
    assert 'run.get("head_branch") != "main"' in resolver
    assert 'repository != "dbrckk/Production-OS"' in resolver
    assert "sha == main_before" in resolver
    assert "No successful CI for current Production-OS main revision" in resolver
    assert "Production-OS main moved during qualified revision lookup" in resolver
    assert "print(main_before)" in resolver
    assert "qualified.sort(reverse=True)" not in resolver
    assert "print(qualified[0][1])" not in resolver
    assert "timeout=20" in resolver
    assert "b8be27a65200629553200f912b0caa9112ff8f4c" not in WORKFLOW


def test_actions_worker_authenticates_qualified_revision_lookup_without_logging_token():
    resolver = WORKFLOW.split(
        "- name: Resolve qualified Production-OS revision", 1
    )[1].split("- name: Checkout Production-OS tools", 1)[0]
    assert 'token = os.environ.get("GITHUB_TOKEN", "").strip()' in resolver
    assert 'headers["Authorization"] = f"Bearer {token}"' in resolver
    assert "urllib.request.Request(url, headers=headers)" in resolver
    assert 'print(token)' not in resolver
    assert 'printf' not in resolver.split("PY", 1)[0]
    assert "class NoRedirect(urllib.request.HTTPRedirectHandler):" in resolver
    assert "if url not in {runs_url, branch_url}:" in resolver
    assert "opener = urllib.request.build_opener(NoRedirect())" in resolver
    assert "with opener.open(request, timeout=20) as response:" in resolver
    assert "urllib.request.urlopen(request, timeout=20)" not in resolver

    # Exercise the embedded production resolver itself with deterministic
    # public GitHub responses, not just source-string assertions. The PAT
    # deliberately lacks Actions-read access to the other public repository.
    import contextlib
    import io
    import json
    import os
    import urllib.error
    import urllib.request
    from textwrap import dedent
    from unittest.mock import patch

    script = dedent(
        resolver.split("<<'PY'\n", 1)[1].split("\n          PY", 1)[0]
    )
    qualified_sha = "d" * 40
    branch_url = "https://api.github.com/repos/dbrckk/Production-OS/branches/main"
    runs_url = (
        "https://api.github.com/repos/dbrckk/Production-OS/actions/runs"
        "?branch=main&per_page=100"
    )
    success_payload = {
        "workflow_runs": [{
            "path": ".github/workflows/ci.yml",
            "conclusion": "success",
            "event": "push",
            "head_branch": "main",
            "head_repository": {"full_name": "dbrckk/Production-OS"},
            "head_sha": qualified_sha,
        }]
    }

    class Response:
        def __init__(self, payload):
            self.raw = json.dumps(payload).encode("utf-8")

        def read(self, *_args):
            return self.raw

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

    class ScopedTransport:
        def __init__(self, *, deny_public=False):
            self.calls = []
            self.deny_public = deny_public

        def open(self, request, *, timeout):
            url = request.full_url
            authorization = request.get_header("Authorization")
            self.calls.append((url, authorization, timeout))
            assert url in {branch_url, runs_url}
            assert timeout == 20
            if authorization or self.deny_public:
                raise urllib.error.HTTPError(url, 403, "Denied", {}, None)
            return Response(
                {"commit": {"sha": qualified_sha}}
                if url == branch_url else success_payload
            )

    def run_resolver(transport):
        capture = io.StringIO()
        with patch.dict(os.environ, {"GITHUB_TOKEN": "scoped-test-token"}):
            with patch("urllib.request.build_opener", return_value=transport):
                with contextlib.redirect_stdout(capture):
                    exec(
                        compile(script, "production-os-revision-resolver", "exec"),
                        {"__name__": "__main__"},
                    )
        return capture.getvalue()

    working = ScopedTransport()
    assert run_resolver(working).strip() == qualified_sha
    assert [url for url, _, _ in working.calls] == [
        branch_url, branch_url, runs_url, runs_url, branch_url, branch_url,
    ]
    for first, retry in zip(working.calls[::2], working.calls[1::2]):
        assert first[1] == "Bearer scoped-test-token"
        assert retry[1] is None
    assert "scoped-test-token" not in run_resolver(ScopedTransport())

    blocked = ScopedTransport(deny_public=True)
    try:
        run_resolver(blocked)
    except urllib.error.HTTPError as exc:
        assert exc.code == 403
    else:
        raise AssertionError("Public 403 must fail closed without a qualified SHA")
    assert len(blocked.calls) == 2



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
    # Exercise the actual Actions configuration step, not a replacement
    # validator: primary NVIDIA keys must not be mandatory when an eligible
    # alternate or keyless local coding provider is configured.
    import json
    import os
    import subprocess
    import tempfile
    from textwrap import dedent

    assert "STUDIO_PROVIDERS_JSON: ${{ vars.STUDIO_PROVIDERS_JSON }}" in WORKFLOW
    assert "STUDIO_FALLBACK_API_KEY: ${{ secrets.STUDIO_FALLBACK_API_KEY }}" in WORKFLOW
    assert "python studio/production_os_provider_config.py" in WORKFLOW
    block = WORKFLOW.split("      - name: Validate worker configuration\n", 1)[1]
    script = dedent(block.split("        run: |\n", 1)[1].split("\n      - name:", 1)[0])
    with tempfile.TemporaryDirectory() as root:
        env = {
            "PATH": os.environ["PATH"],
            "HOME": root,
            "PYTHONPATH": "studio",
            "GITHUB_ENV": str(Path(root) / "github-env"),
            "PRODUCTION_OS_WORKER_TOKEN": "test-worker-secret",
            "STUDIO_GITHUB_TOKEN": "test-repository-secret",
            "PRODUCTION_OS_URL": "https://production.example",
            "STUDIO_API_BASE": "https://custom.example.invalid/v1",
        }

        def run(config):
            result = subprocess.run(
                ["bash", "-c", script], env={**env, **config},
                cwd=Path(__file__).resolve().parents[1],
                text=True, capture_output=True, timeout=20,
            )
            assert "test-worker-secret" not in result.stdout + result.stderr
            assert "test-repository-secret" not in result.stdout + result.stderr
            assert "test-fallback-secret" not in result.stdout + result.stderr
            return result

        fallback = [{
            "name": "free-alternate",
            "base": "https://free.example.invalid/v1",
            "key_env": "STUDIO_FALLBACK_API_KEY",
            "model": "qwen-coder",
        }]
        accepted = run({
            "STUDIO_FALLBACK_API_KEY": "test-fallback-secret",
            "STUDIO_PROVIDERS_JSON": json.dumps(fallback),
        })
        assert accepted.returncode == 0, accepted.stderr
        assert "configuration: ready" in accepted.stdout
        local = run({
            "STUDIO_API_BASE": "http://127.0.0.1:11434/v1",
            "STUDIO_PROVIDERS_JSON": "",
        })
        assert local.returncode == 0, local.stderr
        missing = run({"STUDIO_PROVIDERS_JSON": ""})
        assert missing.returncode != 0
        assert "No configured coding inference provider" in missing.stderr
        missing_fallback = run({
            "STUDIO_PROVIDERS_JSON": json.dumps(fallback),
        })
        assert missing_fallback.returncode != 0


def test_actions_worker_fails_ci_when_production_result_failed():
    assert 'if status == "failed":' in WORKFLOW
    assert 'Production-OS base-capability job failed' in WORKFLOW

def test_actions_worker_reports_remote_asset_forge_probe_without_blocking_code_work():
    assert "production-os asset-forge-batch --probe" in WORKFLOW
    assert "Remote Asset Forge dispatch is unavailable; visual capability will remain disabled." in WORKFLOW
    assert "if env -u PYTHONPATH production-os asset-forge-batch --probe; then" in WORKFLOW


def test_control_only_pushes_do_not_fan_out_into_unrelated_heavy_ci():
    for path in (
        ".github/workflows/ci.yml",
        ".github/workflows/validate.yml",
        ".github/workflows/fault-injection.yml",
        ".github/workflows/resilience-soak.yml",
        ".github/workflows/studio-smoke.yml",
        ".github/workflows/multi-engine-benchmark.yml",
        ".github/workflows/ai-repo-map.yml",
        ".github/workflows/production-os-worker-integration.yml",
    ):
        workflow = Path(path).read_text(encoding="utf-8")
        assert 'paths-ignore:' in workflow
        assert '"control/**"' in workflow
