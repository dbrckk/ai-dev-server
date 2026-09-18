import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from capacity_scheduler import main
from omniroute_capacity import OmniRouteCapacitySnapshot


class CapacitySchedulerOmniRouteTests(unittest.TestCase):
    def test_cli_replaces_static_omniroute_capacity_with_live_remaining(self):
        snapshot = OmniRouteCapacitySnapshot(
            steady_recurring_tokens=1_000,
            used_this_month=940,
            remaining_tokens=60,
            catalog_updated_at="2026-09-18",
            catalog_source="baseline",
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            projects = root / "projects.json"
            providers = root / "providers.json"
            output = root / "capacity.json"
            projects.write_text(
                json.dumps({"projects": [{"id": "p", "requested_tokens": 100}]}),
                encoding="utf-8",
            )
            providers.write_text(
                json.dumps({
                    "providers": [
                        {"name": "omniroute", "available_tokens": 999},
                        {"name": "other-free", "available_tokens": 40},
                    ]
                }),
                encoding="utf-8",
            )

            with patch.dict(os.environ, {"OMNIROUTE_API_KEY": "secret"}, clear=False):
                with patch(
                    "capacity_scheduler.fetch_omniroute_summary",
                    return_value=snapshot,
                ) as fetch:
                    rc = main([
                        "--projects", str(projects),
                        "--providers", str(providers),
                        "--omniroute-url", "http://127.0.0.1:20128",
                        "--output", str(output),
                    ])

            self.assertEqual(rc, 0)
            fetch.assert_called_once_with(
                "http://127.0.0.1:20128",
                api_key="secret",
                timeout=5.0,
            )
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(report["finite_capacity_tokens"], 100)
            self.assertEqual(report["capacity_sources"]["omniroute"]["remaining_tokens"], 60)
            self.assertEqual(report["capacity_sources"]["omniroute"]["used_this_month"], 940)
            self.assertEqual(report["capacity_sources"]["omniroute"]["steady_recurring_tokens"], 1_000)
            self.assertTrue(report["capacity_sources"]["omniroute"]["authenticated_usage"])


if __name__ == "__main__":
    unittest.main()
