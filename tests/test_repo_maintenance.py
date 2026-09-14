import sys
from datetime import datetime, timezone
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from repo_maintenance import classify

class RepoMaintenanceTests(unittest.TestCase):
    def setUp(self):
        self.now=datetime(2026,9,14,tzinfo=timezone.utc).timestamp()

    def test_archived_is_archived(self):
        result=classify({"archived":True,"pushed_at":"2026-09-01T00:00:00Z"},now=self.now)
        self.assertEqual(result["status"],"archived")

    def test_recent_push_is_active(self):
        result=classify({"archived":False,"pushed_at":"2026-09-01T00:00:00Z"},now=self.now)
        self.assertEqual(result["status"],"active")

    def test_old_push_is_stale(self):
        result=classify({"archived":False,"pushed_at":"2025-01-01T00:00:00Z"},now=self.now)
        self.assertEqual(result["status"],"stale")
        self.assertGreater(result["age_days"],365)

    def test_missing_timestamp_is_unknown(self):
        result=classify({"archived":False},now=self.now)
        self.assertEqual(result["status"],"unknown")

if __name__=="__main__":
    unittest.main()
