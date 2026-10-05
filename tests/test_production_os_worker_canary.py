from pathlib import Path
import unittest

from production_os_worker_canary import (
    canary_instruction,
    run_canary,
    validate_control,
    wait_for_workflow,
)


class FakeClient:
    def __init__(self, statuses=("succeeded",)):
        self.statuses = list(statuses)
        self.submissions = []
        self.lookups = []

    def submit(self, path, payload):
        self.submissions.append((path, payload))
        return {
            "project": {
                "project_id": "a" * 32,
                "current_workflow_id": "b" * 32,
            },
            "launch": {"worker_wake": {"status": "dispatched"}},
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
        ):
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_control(value)

    def test_canary_instruction_is_bounded_and_sequence_specific(self):
        instruction = canary_instruction(12)
        self.assertIn(".production-os/worker-canary-12.txt", instruction)
        self.assertIn("production-os-worker-canary sequence 12", instruction)
        self.assertIn("Do not change dependencies", instruction)

    def test_launch_is_idempotent_and_uses_dashboard_api(self):
        client = FakeClient()
        result = run_canary(client, {"sequence": 4, "repository": "dbrckk/repo-standards"})
        self.assertTrue(result["succeeded"])
        path, payload = client.submissions[0]
        self.assertEqual(path, "/v1/dashboard/launch")
        self.assertEqual(payload["repository"], "dbrckk/repo-standards")
        self.assertEqual(payload["request_id"], "worker-canary-4")
        self.assertEqual(result["worker_wake"], "dispatched")

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


if __name__ == "__main__":
    unittest.main()


def test_canary_workflow_does_not_hold_runner_while_waiting_for_worker():
    workflow = Path(".github/workflows/production-os-worker-canary.yml").read_text(encoding="utf-8")
    assert "--wait-seconds 0" in workflow
    assert "--wait-seconds 4200" not in workflow
    assert "cancel-in-progress: true" in workflow
