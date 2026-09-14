import time
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from lease_guard import maintain
from task_lease import claim


class LeaseGuardTests(unittest.TestCase):
    def test_guard_refreshes_active_lease(self):
        task = {"status": "running"}
        claim(task, owner="worker-a", lease_seconds=30)
        before = task["lease_heartbeat_at"]

        with maintain(task, lease_seconds=30, interval_seconds=0.02):
            time.sleep(0.06)

        self.assertGreater(task["lease_heartbeat_at"], before)


if __name__ == "__main__":
    unittest.main()
