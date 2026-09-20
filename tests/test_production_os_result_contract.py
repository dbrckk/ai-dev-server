import copy
import json
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from core import StudioError, request_check
from github_runner import write_production_os_result


BASE = {
    "id": "demo-v1",
    "target_repo": "owner/app",
    "app_name": "demo_app",
    "brief": "Build a complete polished mobile application.",
    "enabled": True,
}


class ProductionOSResultContractTests(unittest.TestCase):
    def test_request_accepts_optional_production_os_correlation(self):
        value = copy.deepcopy(BASE)
        value["production_os"] = {
            "workflow_id": "a" * 32,
            "workflow_task_id": "goal",
        }

        checked = request_check(value)

        self.assertEqual(
            checked["production_os"],
            {
                "workflow_id": "a" * 32,
                "workflow_task_id": "goal",
            },
        )

    def test_request_rejects_invalid_production_os_correlation(self):
        value = copy.deepcopy(BASE)
        value["production_os"] = {
            "workflow_id": "../bad",
            "workflow_task_id": "goal",
        }

        with self.assertRaisesRegex(StudioError, "production_os"):
            request_check(value)

    def test_result_envelope_correlates_usage_and_completion(self):
        request = copy.deepcopy(BASE)
        request["production_os"] = {
            "workflow_id": "b" * 32,
            "workflow_task_id": "instruction-1",
        }
        summary = {
            "status": "complete",
            "finished": True,
            "next_stage": None,
            "usage": {
                "input_tokens": 100,
                "cached_input_tokens": 20,
                "output_tokens": 30,
                "reasoning_tokens": 7,
                "total_tokens": 130,
                "runs": 1,
                "agents": {"codex": 1},
            },
        }

        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            envelope = write_production_os_result(out, request, summary)
            persisted = json.loads(
                (out / "production-os-result.json").read_text(encoding="utf-8")
            )

        self.assertEqual(envelope, persisted)
        self.assertEqual(
            envelope["schema_version"],
            "ai-dev-server/production-os-result/v1",
        )
        self.assertEqual(envelope["workflow_id"], "b" * 32)
        self.assertEqual(envelope["workflow_task_id"], "instruction-1")
        self.assertTrue(envelope["succeeded"])
        self.assertEqual(envelope["usage"]["total_tokens"], 130)

    def test_result_envelope_includes_visual_asset_quality(self):
        request = copy.deepcopy(BASE)
        request["production_os"] = {
            "workflow_id": "c" * 32,
            "workflow_task_id": "instruction-visual",
        }
        summary = {
            "status": "complete",
            "finished": True,
            "next_stage": None,
            "usage": {},
        }

        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            (out / "asset-forge-prefetch.json").write_text(json.dumps({
                "status": "completed",
                "quality_status": "regenerated",
                "batch": True,
                "routes": [{}, {}],
                "receipts": [{
                    "quality_summary": {
                        "checked": 2,
                        "regenerated": 1,
                        "minimum_score": 0.79,
                    },
                    "items": [{
                        "id": "hero-run",
                        "target_path": "assets/art/hero-run.png",
                        "depends_on": ["hero"],
                        "cache_hit": False,
                        "visual_similarity": {
                            "attempts": [
                                {"score": 0.40, "passed": False},
                                {"score": 0.79, "passed": True},
                            ],
                        },
                    }],
                }],
            }))
            envelope = write_production_os_result(out, request, summary)

        visual = envelope["evidence"]["visual_assets"]
        self.assertEqual(visual["quality_status"], "regenerated")
        self.assertEqual(visual["checked"], 2)
        self.assertEqual(visual["regenerated"], 1)
        self.assertEqual(visual["minimum_score"], 0.79)
        self.assertEqual(visual["routes"], 2)
        self.assertEqual(visual["items"][0]["id"], "hero-run")
        self.assertEqual(visual["items"][0]["score"], 0.79)
        self.assertEqual(visual["items"][0]["attempts"], 2)
        self.assertEqual(visual["items"][0]["depends_on"], ["hero"])

    def test_no_result_envelope_without_correlation(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            envelope = write_production_os_result(
                out,
                copy.deepcopy(BASE),
                {"status": "complete", "finished": True, "usage": {}},
            )
            self.assertIsNone(envelope)
            self.assertFalse((out / "production-os-result.json").exists())


if __name__ == "__main__":
    unittest.main()
