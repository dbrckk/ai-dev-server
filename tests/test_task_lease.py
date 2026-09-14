import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from task_lease import active, claim, expired, heartbeat, recover, release


class TaskLeaseTests(unittest.TestCase):
    def test_second_worker_cannot_claim_active_lease(self):
        task = {"status": "running"}
        claim(task, owner="worker-a", lease_seconds=60, now=100.0)

        with self.assertRaises(RuntimeError):
            claim(task, owner="worker-b", lease_seconds=60, now=120.0)

        self.assertEqual(task["lease_owner"], "worker-a")

    def test_owner_can_refresh_lease(self):
        task = {"status": "running"}
        claim(task, owner="worker-a", lease_seconds=60, now=100.0)
        token = task["lease_token"]

        heartbeat(task, owner="worker-a", token=token, lease_seconds=120, now=120.0)

        self.assertTrue(active(task, now=200.0))
        self.assertEqual(task["lease_heartbeat_at"], 120.0)
        self.assertEqual(task["lease_expires_at"], 240.0)

    def test_wrong_heartbeat_owner_is_rejected(self):
        task = {"status": "running"}
        claim(task, owner="worker-a", lease_seconds=60, now=100.0)

        with self.assertRaises(RuntimeError):
            heartbeat(
                task,
                owner="worker-b",
                token=task["lease_token"],
                lease_seconds=60,
                now=110.0,
            )

    def test_expired_running_task_is_recovered_for_retry(self):
        task = {"status": "running"}
        claim(task, owner="worker-a", lease_seconds=30, now=100.0)

        self.assertTrue(expired(task, now=131.0))
        self.assertTrue(recover(task, now=131.0))
        self.assertEqual(task["status"], "retry")
        self.assertEqual(task["lease_recovery_count"], 1)
        self.assertNotIn("lease_owner", task)
        self.assertNotIn("lease_token", task)

    def test_release_clears_lease_metadata(self):
        task = {"status": "running"}
        claim(task, owner="worker-a", lease_seconds=60, now=100.0)
        token = task["lease_token"]

        release(task, owner="worker-a", token=token)

        self.assertNotIn("lease_owner", task)
        self.assertNotIn("lease_token", task)
        self.assertNotIn("lease_expires_at", task)


if __name__ == "__main__":
    unittest.main()
