import multiprocessing
import tempfile
import time
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from file_lock import exclusive


def _hold_lock(path):
    with exclusive(Path(path), timeout_seconds=1.0):
        time.sleep(0.4)


class FileLockTests(unittest.TestCase):
    def test_lock_timeout_prevents_indefinite_deadlock(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "state.json"
            holder = multiprocessing.Process(target=_hold_lock, args=(str(path),))
            holder.start()
            time.sleep(0.1)

            with self.assertRaises(TimeoutError):
                with exclusive(path, timeout_seconds=0.05, poll_seconds=0.01):
                    pass

            holder.join(5)
            self.assertEqual(holder.exitcode, 0)

    def test_lock_releases_after_owner_exits(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "state.json"
            with exclusive(path, timeout_seconds=1.0):
                pass
            with exclusive(path, timeout_seconds=1.0):
                pass


if __name__ == "__main__":
    unittest.main()
