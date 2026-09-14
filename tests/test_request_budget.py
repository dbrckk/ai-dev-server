import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from core import StudioError, request_check


BASE = {
    "id": "demo-v1",
    "target_repo": "owner/app",
    "app_name": "demo_app",
    "brief": "Build a complete polished mobile application.",
    "enabled": True,
}


class RequestBudgetTests(unittest.TestCase):
    def test_accepts_project_budget_overrides(self):
        req = dict(BASE)
        req["max_project_model_calls"] = 40
        req["max_project_repair_calls"] = 10
        result = request_check(req)
        self.assertEqual(result["max_project_model_calls"], 40)
        self.assertEqual(result["max_project_repair_calls"], 10)

    def test_repair_budget_cannot_exceed_explicit_total_budget(self):
        req = dict(BASE)
        req["max_project_model_calls"] = 5
        req["max_project_repair_calls"] = 6
        with self.assertRaises(StudioError):
            request_check(req)

    def test_rejects_excessive_project_budget(self):
        req = dict(BASE)
        req["max_project_model_calls"] = 501
        with self.assertRaises(StudioError):
            request_check(req)


if __name__ == "__main__":
    unittest.main()
