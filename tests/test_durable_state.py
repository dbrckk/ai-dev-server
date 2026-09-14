import json
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from core import StudioError
import durable_state as ds


class DurableStateTests(unittest.TestCase):
    def test_roundtrip_and_checksum(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "state.json"
            value = {"status": "running", "counter": 2}
            ds.save(path, value)
            self.assertEqual(ds.load(path), value)

    def test_corruption_is_detected(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "state.json"
            ds.save(path, {"status": "stable"})
            payload = json.loads(path.read_text())
            payload["value"]["status"] = "tampered"
            path.write_text(json.dumps(payload))
            with self.assertRaises(StudioError):
                ds.load(path)

    def test_schema_one_is_migrated(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "state.json"
            value = {"status": "old"}
            envelope = {
                "schema": 1,
                "value": value,
                "sha256": ds._checksum(1, value),
            }
            path.write_text(json.dumps(envelope))
            loaded = ds.load(path)
            self.assertEqual(loaded["status"], "old")
            self.assertEqual(loaded["migration_history"][-1], {"from": 1, "to": 2})

    def test_backup_can_restore_corrupt_primary(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            primary = root / "state.json"
            backup = root / "backup.json"
            ds.save(backup, {"status": "good"})
            primary.write_text("{broken")
            restored = ds.repair_from_backup(primary, backup)
            self.assertEqual(restored, {"status": "good"})
            self.assertEqual(ds.load(primary), {"status": "good"})


    def test_load_recovering_restores_last_verified_backup(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "state.json"
            ds.save(path, {"generation": 1})
            ds.save(path, {"generation": 2})
            path.write_text("{corrupted", encoding="utf-8")

            loaded = ds.load_recovering(path)

            self.assertEqual(loaded, {"generation": 1})
            self.assertEqual(ds.load(path), {"generation": 1})



if __name__ == "__main__":
    unittest.main()
