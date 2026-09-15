import json
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from capacity_ledger import reserve, transfer_project_reservations, claim_preemption_lease, heartbeat
from worker_reaper import classify


class WorkerReaperTests(unittest.TestCase):
    def test_expired_claimed_worker_with_progress_is_stalled(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ledger = root / "capacity-ledger.json"
            transfer_project_reservations(
                ledger, victim_project_id="low", contender_project_id="high",
                reserve_tokens=100, now=100, ttl_seconds=30,
            )
            claim = claim_preemption_lease(ledger, "high", now=101, ttl_seconds=30)
            heartbeat(ledger, claim["reservation_id"], progress_marker="p1", now=110, ttl_seconds=30)
            report = classify(root, now=141)
            self.assertEqual(report["summary"]["stalled"], 1)
            self.assertEqual(report["summary"]["recoverable_tokens"], 100)

    def test_expired_unclaimed_preemption_lease_is_orphaned(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            transfer_project_reservations(
                root / "capacity-ledger.json",
                victim_project_id="low", contender_project_id="high",
                reserve_tokens=80, now=100, ttl_seconds=30,
            )
            report = classify(root, now=131)
            self.assertEqual(report["summary"]["orphaned"], 1)

    def test_expired_worker_without_heartbeat_is_crashed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ledger = root / "capacity-ledger.json"
            transfer_project_reservations(
                ledger, victim_project_id="low", contender_project_id="high",
                reserve_tokens=60, now=100, ttl_seconds=30,
            )
            claim_preemption_lease(ledger, "high", now=101, ttl_seconds=30)
            report = classify(root, now=132)
            self.assertEqual(report["summary"]["crashed"], 1)

    def test_terminal_project_is_classified_completed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ledger = root / "capacity-ledger.json"
            transfer_project_reservations(
                ledger, victim_project_id="low", contender_project_id="high",
                reserve_tokens=40, now=100, ttl_seconds=30,
            )
            claim_preemption_lease(ledger, "high", now=101, ttl_seconds=30)
            project = root / "high"
            project.mkdir()
            (project / "generic-report.json").write_text(json.dumps({"status": "complete"}))
            report = classify(root, now=132)
            self.assertEqual(report["summary"]["completed"], 1)


if __name__ == "__main__":
    unittest.main()
