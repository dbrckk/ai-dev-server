import tempfile
import unittest
from pathlib import Path
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from worker_heartbeat import progress_marker, renew_if_progressed


class WorkerHeartbeatTests(unittest.TestCase):
    def test_marker_changes_with_checkpoint_progress(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            autonomy = root / ".autonomy"
            autonomy.mkdir()
            checkpoint = autonomy / "execution-checkpoint.json"
            checkpoint.write_text('{"round":1,"phase":"planned"}')
            first = progress_marker(root)
            checkpoint.write_text('{"round":1,"phase":"verified"}')
            second = progress_marker(root)
            self.assertNotEqual(first, second)

    def test_renew_passes_durable_marker_to_ledger(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "generic-report.json").write_text('{"status":"working"}')
            with patch("worker_heartbeat.heartbeat", return_value={"renewed": True}) as hb:
                result = renew_if_progressed(
                    root / "ledger.json", "reservation-1", root, now=100, ttl_seconds=300
                )
            self.assertTrue(result["renewed"])
            self.assertEqual(hb.call_args.args[1], "reservation-1")
            self.assertTrue(hb.call_args.kwargs["progress_marker"])
            self.assertEqual(hb.call_args.kwargs["now"], 100)
            self.assertEqual(hb.call_args.kwargs["ttl_seconds"], 300)


if __name__ == "__main__":
    unittest.main()
