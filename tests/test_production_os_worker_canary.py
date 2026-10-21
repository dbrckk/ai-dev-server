import base64
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

from core import APIError, NoRedirect

from production_os_worker_canary import (
    canary_instruction,
    dispatch_worker_after_enqueue,
    run_canary,
    validate_control,
    wait_for_workflow,
)


class FakeClient:
    def __init__(self, statuses=("succeeded",), wake_status="dispatched"):
        self.statuses = list(statuses)
        self.wake_status = wake_status
        self.submissions = []
        self.lookups = []

    def submit(self, path, payload):
        self.submissions.append((path, payload))
        return {
            "project": {
                "project_id": "a" * 32,
                "current_workflow_id": "b" * 32,
            },
            "launch": {"worker_wake": {"status": self.wake_status}},
        }

    def get(self, path):
        self.lookups.append(path)
        status = self.statuses.pop(0) if len(self.statuses) > 1 else self.statuses[0]
        return {"workflow": {"status": status}}


class WorkerCanaryTests(unittest.TestCase):
    def test_control_is_strict(self):
        self.assertEqual(validate_control({"sequence": 7, "repository": "owner/repo"}), (7, "owner/repo"))
        for value in (
            {},
            {"sequence": 0, "repository": "owner/repo"},
            {"sequence": True, "repository": "owner/repo"},
            {"sequence": 1, "repository": "../repo"},
            {"sequence": 1, "repository": "owner/.."},
            {"sequence": 1, "repository": "./repo"},
            {"sequence": 1, "repository": "owner/repo", "extra": 1},
            {"sequence": 1, "repository": "owner/repo", "scenario": "unknown"},
            {"sequence": 1, "repository": "owner/repo", "scenario": "jumpy_landing_feedback"},
            {"sequence": 1, "repository": "owner/repo", "scenario": "jumpy_settings_tap_guard"},
            {"sequence": 1, "repository": "owner/repo", "scenario": "jumpy_share_clipboard_guard"},
            {"sequence": 1, "repository": "dbrckk/Jumpy", "scenario": 4},
        ):
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_control(value)

    def test_canary_instruction_is_bounded_and_sequence_specific(self):
        instruction = canary_instruction(12)
        self.assertIn(".production-os/worker-canary-12.txt", instruction)
        self.assertIn("production-os-worker-canary sequence 12", instruction)
        self.assertIn("Do not change dependencies", instruction)
        gameplay = canary_instruction(32, "jumpy_landing_feedback")
        self.assertIn("scripts/main.gd", gameplay)
        self.assertIn("PERFECT and CLUTCH", gameplay)
        self.assertIn("reduced_motion and high_contrast", gameplay)
        self.assertIn("existing Godot 4.7.2", gameplay)
        self.assertNotIn(".production-os/worker-canary-", gameplay)
        guarded = canary_instruction(34, "jumpy_settings_tap_guard")
        self.assertIn("scripts/main.gd", guarded)
        self.assertIn("settings_open == true", guarded)
        self.assertIn("_unhandled_input", guarded)
        self.assertIn("Godot 4.7.2 headless", guarded)
        self.assertIn("normal tap-to-start", guarded)
        self.assertNotIn(".production-os/worker-canary-", guarded)
        self.assertEqual(
            validate_control({"sequence": 34, "repository": "dbrckk/Jumpy",
                              "scenario": "jumpy_settings_tap_guard"}),
            (34, "dbrckk/Jumpy"),
        )
        share = canary_instruction(39, "jumpy_share_clipboard_guard")
        self.assertIn("scripts/integrations.gd", share)
        self.assertIn("FEATURE_CLIPBOARD", share)
        self.assertIn("share_unavailable", share)
        self.assertNotIn(".production-os/worker-canary-", share)
        self.assertEqual(
            validate_control({"sequence": 39, "repository": "dbrckk/Jumpy",
                              "scenario": "jumpy_share_clipboard_guard"}),
            (39, "dbrckk/Jumpy"),
        )
        with self.assertRaises(ValueError):
            canary_instruction(32, "untrusted")

    def test_launch_is_idempotent_and_uses_dashboard_api(self):
        client = FakeClient()
        dispatches = []
        result = run_canary(
            client, {"sequence": 4, "repository": "dbrckk/repo-standards"},
            dispatch=lambda: (dispatches.append(len(client.submissions)), "accepted")[1],
        )
        self.assertIsNone(result["succeeded"])
        self.assertEqual(result["result"], {"status": "launched"})
        path, payload = client.submissions[0]
        self.assertEqual(path, "/v1/dashboard/launch")
        self.assertEqual(payload["repository"], "dbrckk/repo-standards")
        self.assertEqual(payload["request_id"], "worker-canary-4")
        self.assertNotIn("launch_profile", payload)
        self.assertNotIn("token_budget", payload)
        self.assertEqual(result["worker_wake"], "dispatched")
        self.assertEqual(result["actions_worker_wake"], "already_dispatched")
        self.assertEqual(dispatches, [])  # the control plane already woke a worker
        fallback = FakeClient(wake_status="scheduled_fallback")
        fallback_result = run_canary(
            fallback, {"sequence": 6, "repository": "dbrckk/repo-standards"},
            dispatch=lambda: (dispatches.append(len(fallback.submissions)), "accepted")[1],
        )
        self.assertEqual(fallback_result["actions_worker_wake"], "accepted")
        self.assertIsNone(fallback_result["succeeded"])
        self.assertEqual(dispatches, [1])  # dispatch only after successful admission
        available = FakeClient(wake_status="not_needed")
        available_result = run_canary(
            available, {"sequence": 7, "repository": "dbrckk/repo-standards"},
            dispatch=lambda: self.fail("persistent worker needs no dispatch"),
        )
        self.assertEqual(available_result["actions_worker_wake"], "not_needed")
        self.assertIsNone(available_result["succeeded"])
        source_api = Mock()
        vulnerable_source = (
            'func _unhandled_input(event: InputEvent) -> void:\n'
            '\tif state == "READY":\n\t\tstart_run()\n'
            'func landing():\n\tjudgement = "PERFECT"\n\tjudgement = "CLUTCH"\n'
        )
        source_api.call.return_value = {
            "type": "file", "encoding": "base64", "sha": "c" * 40,
            "content": base64.b64encode(vulnerable_source.encode()).decode(),
        }
        gameplay_client = FakeClient()
        gameplay_result = run_canary(gameplay_client, {
            "sequence": 32, "repository": "dbrckk/Jumpy",
            "scenario": "jumpy_landing_feedback",
        }, source_api=source_api)
        self.assertEqual(gameplay_result["scenario"], "jumpy_landing_feedback")
        self.assertEqual(gameplay_client.submissions[0][1]["request_id"], "worker-canary-32")
        self.assertEqual(gameplay_client.submissions[0][1]["launch_profile"], "portfolio-integration")
        self.assertEqual(gameplay_client.submissions[0][1]["token_budget"], 60000)
        self.assertIn("scripts/main.gd", gameplay_client.submissions[0][1]["instruction"])
        guard_client = FakeClient()
        guard_result = run_canary(guard_client, {
            "sequence": 34, "repository": "dbrckk/Jumpy",
            "scenario": "jumpy_settings_tap_guard",
        }, source_api=source_api)
        self.assertEqual(guard_result["scenario"], "jumpy_settings_tap_guard")
        self.assertEqual(guard_client.submissions[0][1]["request_id"], "worker-canary-34")
        self.assertEqual(guard_client.submissions[0][1]["launch_profile"], "portfolio-integration")
        self.assertEqual(guard_client.submissions[0][1]["token_budget"], 60000)
        self.assertIn("settings_open", guard_client.submissions[0][1]["instruction"])
        self.assertEqual(guard_result["source_preflight"]["source_blob_sha"], "c" * 40)
        self.assertEqual(source_api.call.call_args.kwargs, {"timeout_seconds": 15, "max_attempts": 1})
        source_api.call.return_value["content"] = base64.b64encode(
            (vulnerable_source.replace('if state == "READY":',
                                       'if state == "READY" and not settings_open:')
             + 'func show_landing_cue(message, color):\n\tpass\n').encode()
        ).decode()
        for scenario in ("jumpy_settings_tap_guard", "jumpy_landing_feedback"):
            blocked_client = FakeClient()
            blocked = run_canary(blocked_client, {
                "sequence": 35, "repository": "dbrckk/Jumpy", "scenario": scenario,
            }, source_api=source_api, wait_seconds=60,
                dispatch=lambda: self.fail("obsolete objective must not wake worker"))
            self.assertFalse(blocked["succeeded"])
            self.assertEqual(blocked["result"]["reason"], "scenario_no_longer_applicable")
            self.assertEqual(blocked_client.submissions, [])
            self.assertEqual(blocked_client.lookups, [])
        unsafe_share = (
            "func share_score(score: int, daily: bool = false) -> void:\n"
            "\tDisplayServer.clipboard_set(text)\n"
            '\tevent("share_score", {"score": score})\n'
            "func leaderboard_submit(score):\n\tpass\n"
        )
        source_api.call.return_value["content"] = base64.b64encode(
            unsafe_share.encode()
        ).decode()
        share_client = FakeClient()
        share_control = {"sequence": 39, "repository": "dbrckk/Jumpy",
                         "scenario": "jumpy_share_clipboard_guard"}
        share_result = run_canary(share_client, share_control, source_api=source_api)
        self.assertEqual(share_result["source_preflight"]["path"], "scripts/integrations.gd")
        self.assertEqual(share_client.submissions[0][1]["token_budget"], 60000)
        self.assertIn("share_score", share_client.submissions[0][1]["instruction"])
        self.assertEqual(
            source_api.call.call_args.args[1],
            "/repos/dbrckk/Jumpy/contents/scripts/integrations.gd?ref=main",
        )
        source_api.call.return_value["content"] = base64.b64encode(
            unsafe_share.replace(
                "\tDisplayServer.clipboard_set(text)",
                "\tif not DisplayServer.has_feature(DisplayServer.FEATURE_CLIPBOARD):\n"
                "\t\treturn\n\tDisplayServer.clipboard_set(text)",
            ).encode()
        ).decode()
        already_fixed = FakeClient()
        self.assertEqual(
            run_canary(already_fixed, share_control, source_api=source_api)["result"]["reason"],
            "scenario_no_longer_applicable",
        )
        self.assertEqual(already_fixed.submissions, [])
        source_api.call.side_effect = APIError(503)
        with self.assertRaises(APIError):
            run_canary(blocked_client, {"sequence": 36, "repository": "dbrckk/Jumpy",
                                       "scenario": "jumpy_settings_tap_guard"}, source_api=source_api)
        self.assertEqual(blocked_client.submissions, [])
        with self.assertRaises(ValueError):
            dispatch_worker_after_enqueue(token="not-used", repository="untrusted/repo")

        # A bearer-authenticated GitHub dispatch must reject redirects,
        # even if an unexpected HTTP 3xx response points off-site.
        with patch("production_os_worker_canary.urllib.request.build_opener") as opener:
            opener.return_value.open.return_value.__enter__.return_value.status = 204
            self.assertEqual(
                dispatch_worker_after_enqueue(
                    token="test-only-token", repository="dbrckk/ai-dev-server"
                ), "accepted",
            )
            self.assertEqual(opener.call_count, 1)
            self.assertIsInstance(opener.call_args.args[0], NoRedirect)
            request = opener.return_value.open.call_args.args[0]
            self.assertEqual(
                request.full_url,
                "https://api.github.com/repos/dbrckk/ai-dev-server/actions/workflows/"
                "production-os-actions-worker.yml/dispatches",
            )

    def test_wait_observes_real_terminal_success(self):
        client = FakeClient(("queued", "running", "succeeded"))
        now = [0.0]
        def clock():
            return now[0]
        def sleep(seconds):
            now[0] += seconds
        result = wait_for_workflow(
            client, "b" * 32, timeout_seconds=60, poll_seconds=10,
            clock=clock, sleeper=sleep,
        )
        self.assertEqual(result, {"status": "succeeded"})
        self.assertEqual(len(client.lookups), 3)

    def test_terminal_failure_returns_without_retrying_mutation(self):
        client = FakeClient(("running", "failed"))
        now = [0.0]
        result = run_canary(
            client, {"sequence": 5, "repository": "dbrckk/repo-standards"},
            wait_seconds=60, poll_seconds=10,
            clock=lambda: now[0],
            sleeper=lambda seconds: now.__setitem__(0, now[0] + seconds),
        )
        self.assertFalse(result["succeeded"])
        self.assertEqual(result["result"]["status"], "failed")
        self.assertEqual(len(client.submissions), 1)

    def test_wait_is_bounded(self):
        client = FakeClient(("running",))
        now = [0.0]
        result = wait_for_workflow(
            client, "b" * 32, timeout_seconds=20, poll_seconds=10,
            clock=lambda: now[0],
            sleeper=lambda seconds: now.__setitem__(0, now[0] + seconds),
        )
        self.assertEqual(result, {"status": "timed_out", "last_status": "running"})
        for wait, poll in ((-1, 10), (7201, 10), (float("nan"), 10),
                           (float("inf"), 10), (60, 0), (60, 61), (60, float("nan"))):
            with self.subTest(wait=wait, poll=poll):
                untouched = FakeClient()
                with self.assertRaises(ValueError):
                    run_canary(untouched, {"sequence": 1, "repository": "dbrckk/repo-standards"},
                               wait_seconds=wait, poll_seconds=poll,
                               dispatch=lambda: self.fail("invalid timing must not dispatch"))
                self.assertEqual(untouched.submissions, [])
                self.assertEqual(untouched.lookups, [])


if __name__ == "__main__":
    unittest.main()


def test_canary_workflow_verifies_terminal_worker_completion():
    workflow = Path(".github/workflows/production-os-worker-canary.yml").read_text(encoding="utf-8")
    assert "--wait-seconds 1800" in workflow
    assert "--poll-seconds 10" in workflow
    assert "timeout-minutes: 40" in workflow
    assert "cancel-in-progress: true" in workflow
    assert "actions: write" in workflow
    assert "contents: read" in workflow
    assert "secrets.GITHUB_TOKEN" in workflow
    assert "PRODUCTION_OS_CANARY_DISPATCH_TOKEN" in workflow
    # The canary enqueues first and dispatches only if the control plane did
    # not already wake a worker. A push trigger would race the queue.
    worker_workflow = Path(".github/workflows/production-os-actions-worker.yml").read_text(
        encoding="utf-8"
    )
    assert "- 'control/production-os-worker-kick.json'" in worker_workflow
    assert "- 'control/production-os-worker-canary.json'" not in worker_workflow
