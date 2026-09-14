import time
import unittest
from pathlib import Path
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from lease_keepalive import keepalive


class LeaseKeepaliveTests(unittest.TestCase):
    def test_long_operation_renews_active_lease(self):
        task = {
            "lease_owner": "worker-a",
            "lease_token": "token-a",
        }
        calls = []

        def fake_heartbeat(task, *, owner, token, lease_seconds):
            calls.append((owner, token, lease_seconds))
            return task

        with patch("lease_keepalive.heartbeat", side_effect=fake_heartbeat):
            with keepalive(task, interval_seconds=0.01, lease_seconds=60):
                time.sleep(0.04)

        self.assertGreaterEqual(len(calls), 1)
        self.assertTrue(all(call == ("worker-a", "token-a", 60) for call in calls))

    def test_unleased_task_is_noop(self):
        with patch("lease_keepalive.heartbeat") as heartbeat:
            with keepalive({}, interval_seconds=0.01):
                pass
        heartbeat.assert_not_called()


if __name__ == "__main__":
    unittest.main()
