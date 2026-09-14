import multiprocessing
import os
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from task_claim_store import claim, release


def _try_claim(path, queue):
    os.environ["STUDIO_TASK_LEASE_PATH"] = str(path)
    try:
        claim("task-1", "worker-b", "token-b", 9999999999.0, now=100.0)
    except Exception as exc:
        queue.put(type(exc).__name__)
    else:
        queue.put("claimed")


class TaskClaimStoreTests(unittest.TestCase):
    def test_second_process_cannot_claim_live_task(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "leases.json"
            os.environ["STUDIO_TASK_LEASE_PATH"] = str(path)
            claim("task-1", "worker-a", "token-a", 9999999999.0, now=100.0)

            queue = multiprocessing.Queue()
            worker = multiprocessing.Process(target=_try_claim, args=(path, queue))
            worker.start()
            worker.join(10)

            self.assertEqual(worker.exitcode, 0)
            self.assertEqual(queue.get(timeout=2), "RuntimeError")
            release("task-1", owner="worker-a", token="token-a")


if __name__ == "__main__":
    unittest.main()
