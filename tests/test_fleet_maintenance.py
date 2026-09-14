import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import fleet_maintenance


class FleetMaintenanceTests(unittest.TestCase):
    def test_removes_only_known_temporary_files(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td) / "demo"
            autonomy = project / ".autonomy"
            autonomy.mkdir(parents=True)
            (autonomy / "keep.json").write_text("x", encoding="utf-8")
            (autonomy / "stale.tmp").write_bytes(b"abc")
            (autonomy / "write.partial").write_bytes(b"1234")

            with patch("fleet_maintenance.compact_telemetry", return_value={
                "compacted": False,
                "bytes_before": 0,
                "bytes_after": 0,
            }):
                report = fleet_maintenance.maintain_project(project)

            self.assertTrue((autonomy / "keep.json").is_file())
            self.assertFalse((autonomy / "stale.tmp").exists())
            self.assertFalse((autonomy / "write.partial").exists())
            self.assertEqual(report["temporary_files"]["removed"], 2)
            self.assertEqual(report["temporary_files"]["bytes_removed"], 7)

    def test_run_ignores_non_project_directories(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "plain").mkdir()
            (root / "project" / ".autonomy").mkdir(parents=True)

            with patch("fleet_maintenance.compact_telemetry", return_value={
                "compacted": False,
                "bytes_before": 0,
                "bytes_after": 0,
            }):
                report = fleet_maintenance.run(root)

            self.assertEqual(report["summary"]["projects"], 1)
            self.assertEqual(report["projects"][0]["id"], "project")


if __name__ == "__main__":
    unittest.main()
