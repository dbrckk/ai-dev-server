"""Offline safety tests for the GitHub Actions OIDC bootstrap client."""
import io
import json
import os
import tempfile
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError

import pytest
from production_os_oidc import acquire_session, main

TOKEN = "pos-gha-" + "t" * 48
BOOTSTRAP = "bootstrap-never-echo"


class Response:
    status = 200
    def __init__(self, payload):
        self.raw = json.dumps(payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, n):
        return self.raw[:n]


def environment(root):
    return {
        "GITHUB_ACTIONS": "true",
        "PRODUCTION_OS_URL": "https://production-os-control-plane.onrender.com",
        "ACTIONS_ID_TOKEN_REQUEST_URL": "https://pipelines.actions.githubusercontent.com/idtoken?job=123",
        "ACTIONS_ID_TOKEN_REQUEST_TOKEN": BOOTSTRAP,
        "GITHUB_ENV": str(Path(root) / "github-env"),
    }


def test_oidc_client_uses_two_bound_credential_exchanges_and_role():
    with tempfile.TemporaryDirectory() as td:
        env = environment(td)
        calls = []
        def open_request(request, timeout):
            calls.append((request, timeout))
            if len(calls) == 1:
                return Response({"value": "signed-gh-oidc-token-without-a-credential"})
            return Response({
                "access_token": TOKEN,
                "expires_in": 6300,
                "role": "worker",
                "token_type": "Bearer",
            })
        assert acquire_session(role="worker", env=env, opener=open_request) == TOKEN
        assert len(calls) == 2
        first, second = [x[0] for x in calls]
        assert first.get_method() == "GET"
        assert first.full_url.startswith("https://pipelines.actions.githubusercontent.com/idtoken?")
        assert "audience=production-os-control-plane" in first.full_url
        assert first.get_header("Authorization") == "bearer " + BOOTSTRAP
        assert second.get_method() == "POST"
        assert second.full_url == "https://production-os-control-plane.onrender.com/v1/auth/github-actions"
        assert json.loads(second.data) == {
            "id_token": "signed-gh-oidc-token-without-a-credential", "role": "worker",
        }
        assert second.get_header("Authorization") is None


def test_untrusted_oidc_provider_or_context_is_rejected_before_network():
    with tempfile.TemporaryDirectory() as td:
        basic = environment(td)
        cases = [
            {"ACTIONS_ID_TOKEN_REQUEST_URL": "http://pipelines.actions.githubusercontent.com/token"},
            {"ACTIONS_ID_TOKEN_REQUEST_URL": "https://attacker.invalid/oidc"},
            {"ACTIONS_ID_TOKEN_REQUEST_URL": "https://pipelines.actions.githubusercontent.com.evil.invalid/id"},
            {"ACTIONS_ID_TOKEN_REQUEST_TOKEN": ""},
            {"GITHUB_ACTIONS": "false"},
            {"PRODUCTION_OS_URL": "http://production-os-control-plane.onrender.com"},
            {"PRODUCTION_OS_URL": "https://production-os-control-plane.onrender.com@evil.invalid"},
        ]
        for change in cases:
            env = {**basic, **change}
            with pytest.raises(ValueError):
                acquire_session(role="worker", env=env, opener=lambda *_a, **_k: pytest.fail("network used"))
        with pytest.raises(ValueError):
            acquire_session(role="admin", env=basic)


def test_wrong_role_or_invalid_access_token_fails_closed():
    with tempfile.TemporaryDirectory() as td:
        env = environment(td)
        def client(payload):
            count = [0]
            def open_request(request, timeout):
                count[0] += 1
                return Response({"value": "signed-gh-oidc-token-without-a-credential"} if count[0] == 1 else payload)
            return open_request
        for bad in (
            {"role": "operator", "token_type": "Bearer", "access_token": TOKEN, "expires_in": 6300},
            {"role": "worker", "token_type": "Bearer", "access_token": "bad", "expires_in": 6300},
            {"role": "worker", "token_type": "Bearer", "access_token": TOKEN + "\nINJECT=1", "expires_in": 6300},
            {"role": "worker", "token_type": "Bearer", "access_token": TOKEN, "expires_in": 9000},
        ):
            with pytest.raises(ValueError):
                acquire_session(role="worker", env=env, opener=client(bad))


def test_cli_masks_temporary_session_before_environment_write():
    with tempfile.TemporaryDirectory() as td:
        env = environment(td)
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch.dict(os.environ, env), patch("production_os_oidc.acquire_session", return_value=TOKEN):
            with redirect_stdout(stdout), redirect_stderr(stderr):
                code = main(["operator"])
        assert code == 0
        assert stdout.getvalue().splitlines() == [
            "::add-mask::" + TOKEN, "Production-OS GitHub OIDC session ready: operator",
        ]
        assert (Path(td) / "github-env").read_text() == "PRODUCTION_OS_OPERATOR_TOKEN=" + TOKEN + "\n"
        assert not stderr.getvalue()


def test_cli_http_error_never_exposes_credentials():
    with tempfile.TemporaryDirectory() as td:
        env = environment(td)
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch.dict(os.environ, env), patch(
            "production_os_oidc.acquire_session",
            side_effect=HTTPError("https://example.invalid", 401, BOOTSTRAP, {}, None),
        ), redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(["worker"])
        assert code == 1
        assert BOOTSTRAP not in stdout.getvalue() + stderr.getvalue()
        assert "OIDC exchange failed" in stderr.getvalue()
        assert not Path(env["GITHUB_ENV"]).exists()


def test_actions_workflows_have_oidc_and_no_static_control_plane_secret():
    worker = Path(".github/workflows/production-os-actions-worker.yml").read_text()
    canary = Path(".github/workflows/production-os-worker-canary.yml").read_text()
    for text in (worker, canary):
        assert "id-token: write" in text
        assert "secrets.PRODUCTION_OS_OPERATOR_TOKEN" not in text
        assert "secrets.PRODUCTION_OS_WORKER_TOKEN" not in text
        assert "python studio/production_os_oidc.py worker" in text
    assert "python studio/production_os_oidc.py operator" in canary
