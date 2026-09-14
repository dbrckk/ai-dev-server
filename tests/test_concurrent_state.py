import multiprocessing
import os
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import persistent_quick_gate_cache as pqc
import workflow_checkpoint as wc


def _write_quick_cache(path, prefix, count):
    os.environ["STUDIO_QUICK_GATE_CACHE_PATH"] = str(path)
    for i in range(count):
        pqc.save({f"{prefix}-{i}": {"passed": True, "logs": []}})


def _write_checkpoints(path, prefix, count):
    os.environ["STUDIO_CHECKPOINT_PATH"] = str(path)
    for i in range(count):
        key = wc.operation_key("stress", {"prefix": prefix, "i": i})
        wc.put(key, {"prefix": prefix, "i": i}, kind="stress")


class ConcurrentStateTests(unittest.TestCase):
    def test_two_processes_do_not_lose_quick_cache_updates(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "quick.json"
            workers = [
                multiprocessing.Process(target=_write_quick_cache, args=(path, "a", 40)),
                multiprocessing.Process(target=_write_quick_cache, args=(path, "b", 40)),
            ]
            for worker in workers:
                worker.start()
            for worker in workers:
                worker.join(20)
                self.assertEqual(worker.exitcode, 0)

            os.environ["STUDIO_QUICK_GATE_CACHE_PATH"] = str(path)
            loaded = pqc.load()
            self.assertEqual(len(loaded), 80)
            self.assertIn("a-0", loaded)
            self.assertIn("b-39", loaded)

    def test_two_processes_do_not_corrupt_checkpoint_store(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "checkpoints.json"
            workers = [
                multiprocessing.Process(target=_write_checkpoints, args=(path, "a", 30)),
                multiprocessing.Process(target=_write_checkpoints, args=(path, "b", 30)),
            ]
            for worker in workers:
                worker.start()
            for worker in workers:
                worker.join(20)
                self.assertEqual(worker.exitcode, 0)

            os.environ["STUDIO_CHECKPOINT_PATH"] = str(path)
            loaded = wc.load()
            self.assertEqual(len(loaded), 60)


if __name__ == "__main__":
    unittest.main()
