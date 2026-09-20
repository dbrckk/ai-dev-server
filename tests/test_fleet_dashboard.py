import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from fleet_dashboard import collect


class FleetDashboardTests(unittest.TestCase):
    def test_collect_surfaces_regenerated_visual_quality(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            project = root / "deadline-zero"
            (project / ".autonomy").mkdir(parents=True)
            (project / "asset-forge-prefetch.json").write_text(json.dumps({
                "status": "completed",
                "quality_status": "regenerated",
                "batch": True,
                "routes": [{}, {}],
                "receipts": [{
                    "quality_summary": {
                        "checked": 2,
                        "regenerated": 1,
                        "minimum_score": 0.77,
                    }
                }],
            }))

            with patch("fleet_dashboard.inspect", return_value={
                "status": "healthy",
                "runtime_status": "complete",
                "attempt": 1,
                "checkpoint_entries": 3,
                "leases": {"claims": 0},
                "telemetry": {"events": 5},
                "errors": [],
            }), patch("fleet_dashboard.summarize_architecture_learning", return_value={
                "rankings": [],
                "projects_observed": 1,
            }):
                result = collect(root)

            visual = result["projects"][0]["visual_assets"]
            self.assertEqual(visual["quality_status"], "regenerated")
            self.assertEqual(visual["checked"], 2)
            self.assertEqual(visual["regenerated"], 1)
            self.assertEqual(visual["minimum_score"], 0.77)
            self.assertEqual(result["summary"]["visual_quality_regenerated"], 1)

    def test_collect_surfaces_low_visual_quality_failure(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            project = root / "deadline-zero"
            (project / ".autonomy").mkdir(parents=True)
            (project / "asset-forge-prefetch.json").write_text(json.dumps({
                "status": "failed",
                "quality_status": "low_quality",
                "batch": True,
                "routes": [{}, {}],
                "receipt": {
                    "success": False,
                    "error_code": "visual_quality_failed",
                },
            }))

            with patch("fleet_dashboard.inspect", return_value={
                "status": "healthy",
                "runtime_status": "blocked",
                "attempt": 1,
                "checkpoint_entries": 1,
                "leases": {"claims": 0},
                "telemetry": {"events": 1},
                "errors": [],
            }), patch("fleet_dashboard.summarize_architecture_learning", return_value={
                "rankings": [],
                "projects_observed": 1,
            }):
                result = collect(root)

            visual = result["projects"][0]["visual_assets"]
            self.assertEqual(visual["quality_status"], "low_quality")
            self.assertEqual(visual["error_code"], "visual_quality_failed")
            self.assertEqual(result["summary"]["visual_quality_low"], 1)


if __name__ == "__main__":
    unittest.main()
