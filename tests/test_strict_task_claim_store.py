import multiprocessing
import os
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from core import StudioError
from strict_task_claim_store import claim, release


def _claim_in_process(path, result_path):
    os.environ["STUDIO_TASK_LEASE_PATH"] = str(path)
    try:
        claim("task-1", "worker-b", "token-b", 9999999999.0, now=100.0)
    except Exception as exc:
        Path(result_path).write_text(type(exc).__name__, encoding="utf-8")
    else:
        Path(result_path).write_text("claimed", encoding="utf-8")


class StrictTaskClaimStoreTests(unittest.TestCase):
    def test_corrupt_store_is_rejected_under_lock(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "leases.json"
            path.write_text("{broken", encoding="utf-8")
            os.environ["STUDIO_TASK_LEASE_PATH"] = str(path)
            with self.assertRaises(StudioError):
                claim("task-1", "worker-a", "token-a", 200.0, now=100.0)

    def test_second_process_cannot_claim_live_task(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "leases.json"
            os.environ["STUDIO_TASK_LEASE_PATH"] = str(path)
            claim("task-1", "worker-a", "token-a", 9999999999.0, now=100.0)

            result_path = Path(td) / "result.txt"
            worker = multiprocessing.Process(
                target=_claim_in_process,
                args=(path, result_path),
            )
            worker.start()
            worker.join(10)

            self.assertEqual(worker.exitcode, 0)
            self.assertEqual(result_path.read_text(encoding="utf-8"), "RuntimeError")
            release("task-1", owner="worker-a", token="token-a")


if __name__ == "__main__":
    unittest.main()
